# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: chat_serializers.py
    @date:2023/11/14 9:59
    @desc:
"""
import datetime
import json
import os
import re
import uuid
from functools import reduce
from typing import Dict

import xlwt
from django.core import validators
from django.core.cache import caches
from django.db import transaction, models
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from rest_framework import serializers

from application.models import Chat, Application, ApplicationDatasetMapping, VoteChoices, ChatRecord
from application.models.api_key_model import ApplicationAccessToken
from application.serializers.application_serializers import ModelDatasetAssociation, DatasetSettingSerializer, \
    ModelSettingSerializer
from application.serializers.chat_message_serializers import ChatInfo
from common.constants.permission_constants import RoleConstants
from common.db.search import native_search, native_page_search, page_search, get_dynamics_model
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.util.common import post
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.lock import try_lock, un_lock
from common.util.rsa_util import rsa_long_decrypt
from dataset.models import Document, Problem, Paragraph, ProblemParagraphMapping
from dataset.serializers.paragraph_serializers import ParagraphSerializers
from setting.models import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from smartdoc.conf import PROJECT_DIR

chat_cache = caches['model_cache']


class ChatSerializers(serializers.Serializer):
    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Applicationsid"))

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Chat).filter(id=self.data.get('chat_id'), application_id=self.data.get('application_id')).delete()
            return True

    class Query(serializers.Serializer):
        abstract = serializers.CharField(required=False, error_messages=ErrMessage.char("The summary"))
        history_day = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("History of Days"))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Usersid"))
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Applicationsid"))
        min_star = serializers.IntegerField(required=False, min_value=0,
                                            error_messages=ErrMessage.integer("The minimum number."))
        min_trample = serializers.IntegerField(required=False, min_value=0,
                                               error_messages=ErrMessage.integer("The minimum number of steps."))
        comparer = serializers.CharField(required=False, error_messages=ErrMessage.char("comparator"), validators=[
            validators.RegexValidator(regex=re.compile("^and|or$"),
                                      message="Only support.and|or", code=500)
        ])

        def get_end_time(self):
            history_day = self.data.get('history_day')
            return datetime.datetime.now() - datetime.timedelta(days=history_day)

        def get_query_set(self):
            end_time = self.get_end_time()
            query_set = QuerySet(model=get_dynamics_model(
                {'application_chat.application_id': models.CharField(),
                 'application_chat.abstract': models.CharField(),
                 "star_num": models.IntegerField(),
                 'trample_num': models.IntegerField(),
                 'comparer': models.CharField(),
                 'application_chat.create_time': models.DateTimeField()}))

            base_query_dict = {'application_chat.application_id': self.data.get("application_id"),
                               'application_chat.create_time__gte': end_time}
            if 'abstract' in self.data and self.data.get('abstract') is not None:
                base_query_dict['application_chat.abstract__icontains'] = self.data.get('abstract')
            base_condition = Q(**base_query_dict)
            min_star_query = None
            min_trample_query = None
            if 'min_star' in self.data and self.data.get('min_star') is not None:
                min_star_query = Q(star_num__gte=self.data.get('min_star'))
            if 'min_trample' in self.data and self.data.get('min_trample') is not None:
                min_trample_query = Q(trample_num__gte=self.data.get('min_trample'))
            if min_star_query is not None and min_trample_query is not None:
                if self.data.get(
                        'comparer') is not None and self.data.get('comparer') == 'or':
                    condition = base_condition & (min_star_query | min_trample_query)
                else:
                    condition = base_condition & (min_star_query & min_trample_query)
            elif min_star_query is not None:
                condition = base_condition & min_star_query
            elif min_trample_query is not None:
                condition = base_condition & min_trample_query
            else:
                condition = base_condition
            return query_set.filter(condition).order_by("-application_chat.create_time")

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application_chat.sql')),
                                 with_table_name=False)

        @staticmethod
        def to_row(row: Dict):
            details = row.get('details')
            padding_problem_text = details.get('problem_padding').get(
                'padding_problem_text') if 'problem_padding' in details and 'padding_problem_text' in details.get(
                'problem_padding') else ""
            paragraph_list = details.get('search_step').get(
                'paragraph_list') if 'search_step' in details and 'paragraph_list' in details.get('search_step') else []
            improve_paragraph_list = row.get('improve_paragraph_list')
            vote_status_map = {'-1': 'not voted.', '0': 'agreed', '1': 'opposed'}
            return [str(row.get('chat_id')), row.get('abstract'), row.get('problem_text'), padding_problem_text,
                    row.get('answer_text'), vote_status_map.get(row.get('vote_status')), len(paragraph_list), "\n".join(
                    [f"{index}、{paragraph_list[index].get('title')}\n{paragraph_list[index].get('content')}" for index
                     in
                     range(len(paragraph_list))]),
                    "\n".join([
                        f"{improve_paragraph_list[index].get('title')}\n{improve_paragraph_list[index].get('content')}"
                        for index in range(len(improve_paragraph_list))]),
                    row.get('message_tokens') + row.get('answer_tokens'), row.get('run_time'),
                    str(row.get('create_time'))]

        def export(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            data_list = native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'export_application_chat.sql')),
                                      with_table_name=False)

            # Create the workbook object.
            workbook = xlwt.Workbook(encoding='utf-8')
            # Adding a working table.
            worksheet = workbook.add_sheet('Sheet1')
            data = [
                ['MeetingID', 'The summary', 'User Problems', 'Problems after optimization', 'Reply', 'User feedback', 'Reference to the number of points.', 'Section title+The content',
                 'Signed', 'consumptiontokens', 'It takes time（s）', 'Question time.'],
                *[self.to_row(row) for row in data_list]
            ]
            # Write data into the table.
            for row_idx, row in enumerate(data):
                for col_idx, col in enumerate(row):
                    worksheet.write(row_idx, col_idx, col)
                # CreatedHttpResponseThe object returns.ExcelDocuments
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="data.xls"'

            workbook.save(response)
            return response

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application_chat.sql')),
                                      with_table_name=False)

    class OpenChat(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Usersid"))

        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Applicationsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            application_id = self.data.get('application_id')
            if not QuerySet(Application).filter(id=application_id, user_id=user_id).exists():
                raise AppApiException(500, 'Applications do not exist.')

        def open(self):
            self.is_valid(raise_exception=True)
            application_id = self.data.get('application_id')
            application = QuerySet(Application).get(id=application_id)
            model = QuerySet(Model).filter(id=application.model_id).first()
            dataset_id_list = [str(row.dataset_id) for row in
                               QuerySet(ApplicationDatasetMapping).filter(
                                   application_id=application_id)]
            chat_model = None
            if model is not None:
                chat_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                                   json.loads(
                                                                                       rsa_long_decrypt(
                                                                                           model.credential)),
                                                                                   streaming=True)

            chat_id = str(uuid.uuid1())
            chat_cache.set(chat_id,
                           ChatInfo(chat_id, chat_model, dataset_id_list,
                                    [str(document.id) for document in
                                     QuerySet(Document).filter(
                                         dataset_id__in=dataset_id_list,
                                         is_active=False)],
                                    application), timeout=60 * 30)
            return chat_id

    class OpenTempChat(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Usersid"))

        id = serializers.UUIDField(required=False, allow_null=True,
                                   error_messages=ErrMessage.uuid("Applicationsid"))
        model_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                         error_messages=ErrMessage.uuid("The modelid"))

        multiple_rounds_dialogue = serializers.BooleanField(required=True,
                                                            error_messages=ErrMessage.boolean("Many Rounds of Meetings"))

        dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                     error_messages=ErrMessage.list("Related data"))
        # Data setup related settings
        dataset_setting = DatasetSettingSerializer(required=True)
        # Models related settings
        model_setting = ModelSettingSerializer(required=True)
        # Complete the problem.
        problem_optimization = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("Complete the problem."))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            user_id = self.get_user_id()
            ModelDatasetAssociation(
                data={'user_id': user_id, 'model_id': self.data.get('model_id'),
                      'dataset_id_list': self.data.get('dataset_id_list')}).is_valid()
            return user_id

        def get_user_id(self):
            if 'id' in self.data and self.data.get('id') is not None:
                application = QuerySet(Application).filter(id=self.data.get('id')).first()
                if application is None:
                    raise AppApiException(500, "Applications do not exist.")
                return application.user_id
            return self.data.get('user_id')

        def open(self):
            user_id = self.is_valid(raise_exception=True)
            chat_id = str(uuid.uuid1())
            model_id = self.data.get('model_id')
            if model_id is not None and len(model_id) > 0:
                model = QuerySet(Model).filter(user_id=user_id, id=self.data.get('model_id')).first()
                chat_model = ModelProvideConstants[model.provider].value.get_model(model.model_type, model.model_name,
                                                                                   json.loads(
                                                                                       rsa_long_decrypt(
                                                                                           model.credential)),
                                                                                   streaming=True)
            else:
                model = None
                chat_model = None
            dataset_id_list = self.data.get('dataset_id_list')
            application = Application(id=None, dialogue_number=3, model=model,
                                      dataset_setting=self.data.get('dataset_setting'),
                                      model_setting=self.data.get('model_setting'),
                                      problem_optimization=self.data.get('problem_optimization'))
            chat_cache.set(chat_id,
                           ChatInfo(chat_id, chat_model, dataset_id_list,
                                    [str(document.id) for document in
                                     QuerySet(Document).filter(
                                         dataset_id__in=dataset_id_list,
                                         is_active=False)],
                                    application), timeout=60 * 30)
            return chat_id


class ChatRecordSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'chat_id', 'vote_status', 'problem_text', 'answer_text',
                  'message_tokens', 'answer_tokens', 'const', 'improve_paragraph_id_list', 'run_time', 'index',
                  'create_time', 'update_time']


class ChatRecordSerializer(serializers.Serializer):
    class Operate(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Applicationsid"))
        chat_record_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogue recordsid"))

        def is_valid(self, *, current_role=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=self.data.get('application_id')).first()
            if application_access_token is None:
                raise AppApiException(500, 'No Application Certification Information')
            if not application_access_token.show_source and current_role == RoleConstants.APPLICATION_ACCESS_TOKEN.value:
                raise AppApiException(500, 'Not open to display knowledge sources')

        def get_chat_record(self):
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_info: ChatInfo = chat_cache.get(chat_id)
            if chat_info is not None:
                chat_record_list = [chat_record for chat_record in chat_info.chat_record_list if
                                    chat_record.id == uuid.UUID(chat_record_id)]
                if chat_record_list is not None and len(chat_record_list):
                    return chat_record_list[-1]
            return QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()

        def one(self, current_role: RoleConstants, with_valid=True):
            if with_valid:
                self.is_valid(current_role=current_role, raise_exception=True)
            chat_record = self.get_chat_record()
            if chat_record is None:
                raise AppApiException(500, "There is no dialogue.")
            return ChatRecordSerializer.Query.reset_chat_record(chat_record)

    class Query(serializers.Serializer):
        application_id = serializers.UUIDField(required=True)
        chat_id = serializers.UUIDField(required=True)

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id'))
            return [ChatRecordSerializerModel(chat_record).data for chat_record in
                    QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by("create_time")]

        @staticmethod
        def reset_chat_record(chat_record):
            dataset_list = []
            paragraph_list = []
            if 'search_step' in chat_record.details and chat_record.details.get('search_step').get(
                    'paragraph_list') is not None:
                paragraph_list = chat_record.details.get('search_step').get(
                    'paragraph_list')
                dataset_list = [{'id': dataset_id, 'name': name} for dataset_id, name in reduce(lambda x, y: {**x, **y},
                                                                                                [{row.get(
                                                                                                    'dataset_id'): row.get(
                                                                                                    "dataset_name")} for
                                                                                                    row in
                                                                                                    paragraph_list],
                                                                                                {}).items()]

            return {
                **ChatRecordSerializerModel(chat_record).data,
                'padding_problem_text': chat_record.details.get('problem_padding').get(
                    'padding_problem_text') if 'problem_padding' in chat_record.details else None,
                'dataset_list': dataset_list,
                'paragraph_list': paragraph_list
            }

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            page = page_search(current_page, page_size,
                               QuerySet(ChatRecord).filter(chat_id=self.data.get('chat_id')).order_by("create_time"),
                               post_records_handler=lambda chat_record: self.reset_chat_record(chat_record))
            return page

    class Vote(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))

        chat_record_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogue recordsid"))

        vote_status = serializers.ChoiceField(choices=VoteChoices.choices, error_messages=ErrMessage.uuid("state of offer"))

        @transaction.atomic
        def vote(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            if not try_lock(self.data.get('chat_record_id')):
                raise AppApiException(500, "The current session is being voted.,Do not repeat the request.")
            try:
                chat_record_details_model = QuerySet(ChatRecord).get(id=self.data.get('chat_record_id'),
                                                                     chat_id=self.data.get('chat_id'))
                if chat_record_details_model is None:
                    raise AppApiException(500, "No dialogue. chat_record_id")
                vote_status = self.data.get("vote_status")
                if chat_record_details_model.vote_status == VoteChoices.UN_VOTE:
                    if vote_status == VoteChoices.STAR:
                        # The praise.
                        chat_record_details_model.vote_status = VoteChoices.STAR

                    if vote_status == VoteChoices.TRAMPLE:
                        # step down.
                        chat_record_details_model.vote_status = VoteChoices.TRAMPLE
                    chat_record_details_model.save()
                else:
                    if vote_status == VoteChoices.UN_VOTE:
                        # Cancelled praise.
                        chat_record_details_model.vote_status = VoteChoices.UN_VOTE
                        chat_record_details_model.save()
                    else:
                        raise AppApiException(500, "have voted.,Please cancel and then vote.")
            finally:
                un_lock(self.data.get('chat_record_id'))
            return True

    class ImproveSerializer(serializers.Serializer):
        title = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                      error_messages=ErrMessage.char("Title of paragraph"))
        content = serializers.CharField(required=True, error_messages=ErrMessage.char("Contents of paragraph"))

    class ParagraphModel(serializers.ModelSerializer):
        class Meta:
            model = Paragraph
            fields = "__all__"

    class ChatRecordImprove(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))

        chat_record_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogue recordsid"))

        def get(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
            if chat_record is None:
                raise AppApiException(500, 'No dialogue records.')
            if chat_record.improve_paragraph_id_list is None or len(chat_record.improve_paragraph_id_list) == 0:
                return []

            paragraph_model_list = QuerySet(Paragraph).filter(id__in=chat_record.improve_paragraph_id_list)
            if len(paragraph_model_list) < len(chat_record.improve_paragraph_id_list):
                paragraph_model_id_list = [str(p.id) for p in paragraph_model_list]
                chat_record.improve_paragraph_id_list = list(
                    filter(lambda p_id: paragraph_model_id_list.__contains__(p_id),
                           chat_record.improve_paragraph_id_list))
                chat_record.save()
            return [ChatRecordSerializer.ParagraphModel(p).data for p in paragraph_model_list]

    class Improve(serializers.Serializer):
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))

        chat_record_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogue recordsid"))

        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The knowledge baseid"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Documentsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, "Documentsidwrongly.")

        @staticmethod
        def post_embedding_paragraph(chat_record, paragraph_id):
            # Send to Quantitative Events
            ListenerManagement.embedding_by_paragraph_signal.send(paragraph_id)
            return chat_record

        @post(post_function=post_embedding_paragraph)
        @transaction.atomic
        def improve(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            ChatRecordSerializer.ImproveSerializer(data=instance).is_valid(raise_exception=True)
            chat_record_id = self.data.get('chat_record_id')
            chat_id = self.data.get('chat_id')
            chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
            if chat_record is None:
                raise AppApiException(500, 'No dialogue records.')

            document_id = self.data.get("document_id")
            dataset_id = self.data.get("dataset_id")
            paragraph = Paragraph(id=uuid.uuid1(),
                                  document_id=document_id,
                                  content=instance.get("content"),
                                  dataset_id=dataset_id,
                                  title=instance.get("title") if 'title' in instance else '')

            problem = Problem(id=uuid.uuid1(), content=chat_record.problem_text, dataset_id=dataset_id)
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(), dataset_id=dataset_id,
                                                                document_id=document_id,
                                                                problem_id=problem.id,
                                                                paragraph_id=paragraph.id)
            # Inserting the problem.
            problem.save()
            # Insert the paragraph.
            paragraph.save()
            # Introduction to Related Problems
            problem_paragraph_mapping.save()
            chat_record.improve_paragraph_id_list.append(paragraph.id)
            # Add a Note.
            chat_record.save()
            return ChatRecordSerializerModel(chat_record).data, paragraph.id

        class Operate(serializers.Serializer):
            chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))

            chat_record_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogue recordsid"))

            dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The knowledge baseid"))

            document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Documentsid"))

            paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Paragraphsid"))

            def delete(self, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)

                chat_record_id = self.data.get('chat_record_id')
                chat_id = self.data.get('chat_id')
                dataset_id = self.data.get('dataset_id')
                document_id = self.data.get('document_id')
                paragraph_id = self.data.get('paragraph_id')
                chat_record = QuerySet(ChatRecord).filter(id=chat_record_id, chat_id=chat_id).first()
                if chat_record is None:
                    raise AppApiException(500, 'No dialogue records.')
                if not chat_record.improve_paragraph_id_list.__contains__(uuid.UUID(paragraph_id)):
                    raise AppApiException(500, f'Paragraphsiderrors,There is no current dialogue record.【{paragraph_id}】Paragraphsid')
                chat_record.improve_paragraph_id_list = [row for row in chat_record.improve_paragraph_id_list if
                                                         str(row) != paragraph_id]
                chat_record.save()
                o = ParagraphSerializers.Operate(
                    data={"dataset_id": dataset_id, 'document_id': document_id, "paragraph_id": paragraph_id})
                o.is_valid(raise_exception=True)
                return o.delete()
