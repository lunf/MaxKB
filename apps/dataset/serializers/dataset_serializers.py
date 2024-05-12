# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： dataset_serializers.py
    @date：2023/9/21 16:14
    @desc:
"""
import logging
import os.path
import re
import traceback
import uuid
from functools import reduce
from typing import Dict
from urllib.parse import urlparse

from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet, Q
from drf_yasg import openapi
from rest_framework import serializers

from application.models import ApplicationDatasetMapping
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.db.search import get_dynamics_model, native_page_search, native_search
from common.db.sql_execute import select_list
from common.event import ListenerManagement, SyncWebDatasetArgs
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import ChildLink, Fork
from common.util.split_model import get_split_model
from dataset.models.data_set import DataSet, Document, Paragraph, Problem, Type, ProblemParagraphMapping
from dataset.serializers.common_serializers import list_paragraph, MetaSerializer
from dataset.serializers.document_serializers import DocumentSerializers, DocumentInstanceSerializer
from embedding.models import SearchMode
from setting.models import AuthOperate
from smartdoc.conf import PROJECT_DIR

"""
# __exact  Exactly equal to like ‘aaa’
# __iexact Exactly equal to Ignoring the size of writing. ilike 'aaa'
# __contains Includedlike '%aaa%'
# __icontains Included Ignoring the size of writing. ilike ‘%aaa%’，But forsqlitefor，containsThe effect is equal toicontains。
# __gt  greater than
# __gte More than equal.
# __lt less than
# __lte Less than equal.
# __in It exists in onelistwithin the range
# __startswith by…Beginning
# __istartswith by…Beginning Ignoring the size of writing.
# __endswith by…The end
# __iendswith by…The end，Ignoring the size of writing.
# __range in…within the range
# __year Year of the Date Field
# __month Month of Date Fields
# __day Day of the Date Field
# __isnull=True/False
"""


class DataSetSerializers(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ['id', 'name', 'desc', 'meta', 'create_time', 'update_time']

    class Application(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("Usersid"))

        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("The data collectionid"))

        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='The knowledge baseid')
            ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'user_id', 'status',
                          'create_time',
                          'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description="The key.id"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Application Name", description="Application Name"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Application Description", description="Application Description"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="The modelid", description="The modelid"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Open multiple rounds of dialogue.",
                                                               description="Open multiple rounds of dialogue."),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="Opening White.", description="Opening White."),
                    'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title="Examples List", description="Examples List"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="The User", description="The User"),

                    'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="is published.", description='is published.'),

                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.", description='Creating time.'),

                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.", description='Change time.')
                }
            )

    class Query(ApiMixin, serializers.Serializer):
        """
        Question of objects.
        """
        name = serializers.CharField(required=False,
                                     error_messages=ErrMessage.char("Name of Knowledge Base"),
                                     max_length=64,
                                     min_length=1)

        desc = serializers.CharField(required=False,
                                     error_messages=ErrMessage.char("Knowledge Base Description"),
                                     max_length=256,
                                     min_length=1,
                                     )

        user_id = serializers.CharField(required=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp.name': models.CharField(), 'temp.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField(), 'temp.create_time': models.DateTimeField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__icontains': self.data.get("name")})
            query_set = query_set.order_by("-temp.create_time")
            query_set_dict['default_sql'] = query_set

            query_set_dict['dataset_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'dataset.user_id': models.CharField(),
                 })).filter(
                **{'dataset.user_id': user_id}
            )

            query_set_dict['team_member_permission_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'user_id': models.CharField(),
                 'team_member_permission.auth_target_type': models.CharField(),
                 'team_member_permission.operate': ArrayField(verbose_name="Authorization operating list",
                                                              base_field=models.CharField(max_length=256,
                                                                                          blank=True,
                                                                                          choices=AuthOperate.choices,
                                                                                          default=AuthOperate.USE)
                                                              )})).filter(
                **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE'],
                   'team_member_permission.auth_target_type': 'DATASET'})

            return query_set_dict

        def page(self, current_page: int, page_size: int):
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')),
                                      post_records_handler=lambda r: r)

        def list(self):
            return native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Name of Knowledge Base'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Knowledge Base Description')
                    ]

        @staticmethod
        def get_response_body_api():
            return DataSetSerializers.Operate.get_response_body_api()

    class Create(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("Usersid"), )

        class CreateBaseSerializers(ApiMixin, serializers.Serializer):
            """
            Create general data set sequencing objects
            """
            name = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("Name of Knowledge Base"),
                                         max_length=64,
                                         min_length=1)

            desc = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("Knowledge Base Description"),
                                         max_length=256,
                                         min_length=1)

            documents = DocumentInstanceSerializer(required=False, many=True)

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)
                return True

        class CreateWebSerializers(serializers.Serializer):
            """
            CreatedwebSite Setting Objects
            """
            name = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("Name of Knowledge Base"),
                                         max_length=64,
                                         min_length=1)

            desc = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("Knowledge Base Description"),
                                         max_length=256,
                                         min_length=1)
            source_url = serializers.CharField(required=True, error_messages=ErrMessage.char("Web root address"), )

            selector = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                             error_messages=ErrMessage.char("The Selector"))

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)
                source_url = self.data.get('source_url')
                response = Fork(source_url, []).fork()
                if response.status == 500:
                    raise AppApiException(500, f"urlerrors,Unable to analyze【{source_url}】")
                return True

            @staticmethod
            def get_response_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                              'update_time', 'create_time', 'document_list'],
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                             description="id", default="xx"),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, title="The name",
                                               description="The name", default="Testing knowledge."),
                        'desc': openapi.Schema(type=openapi.TYPE_STRING, title="described",
                                               description="described", default="Test Knowledge Base Description"),
                        'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="The Userid",
                                                  description="The Userid", default="user_xxxx"),
                        'char_length': openapi.Schema(type=openapi.TYPE_STRING, title="Number of characters",
                                                      description="Number of characters", default=10),
                        'document_count': openapi.Schema(type=openapi.TYPE_STRING, title="Number of documents",
                                                         description="Number of documents", default=1),
                        'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                      description="Change time.",
                                                      default="1970-01-01 00:00:00"),
                        'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                      description="Creating time.",
                                                      default="1970-01-01 00:00:00"
                                                      ),
                        'document_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="List of documents",
                                                        description="List of documents",
                                                        items=DocumentSerializers.Operate.get_response_body_api())
                    }
                )

            @staticmethod
            def get_request_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['name', 'desc', 'url'],
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of Knowledge Base", description="Name of Knowledge Base"),
                        'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Knowledge Base Description", description="Knowledge Base Description"),
                        'source_url': openapi.Schema(type=openapi.TYPE_STRING, title="webThe siteurl",
                                                     description="webThe siteurl"),
                        'selector': openapi.Schema(type=openapi.TYPE_STRING, title="The Selector", description="The Selector")
                    }
                )

        @staticmethod
        def post_embedding_dataset(document_list, dataset_id):
            # Send to Quantitative Events
            ListenerManagement.embedding_by_dataset_signal.send(dataset_id)
            return document_list

        @post(post_function=post_embedding_dataset)
        @transaction.atomic
        def save(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self.CreateBaseSerializers(data=instance).is_valid()
            dataset_id = uuid.uuid1()
            user_id = self.data.get('user_id')
            if QuerySet(DataSet).filter(user_id=user_id, name=instance.get('name')).exists():
                raise AppApiException(500, "Repeat the name of the knowledge base!")
            dataset = DataSet(
                **{'id': dataset_id, 'name': instance.get("name"), 'desc': instance.get('desc'), 'user_id': user_id})

            document_model_list = []
            paragraph_model_list = []
            problem_model_list = []
            problem_paragraph_mapping_list = []
            # Insert the document.
            for document in instance.get('documents') if 'documents' in instance else []:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(dataset_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem in document_paragraph_dict_model.get('problem_model_list'):
                    problem_model_list.append(problem)
                for problem_paragraph_mapping in document_paragraph_dict_model.get('problem_paragraph_mapping_list'):
                    problem_paragraph_mapping_list.append(problem_paragraph_mapping)

            # Insert the Knowledge Base.
            dataset.save()
            # Insert the document.
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # Introduction to paragraphs
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # Mass Injection Problems
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # A lot of connected issues.
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None

            # Reacting data
            return {**DataSetSerializers(dataset).data,
                'document_list': DocumentSerializers.Query(data={'dataset_id': dataset_id}).list(
                    with_valid=True)}, dataset_id

        @staticmethod
        def get_last_url_path(url):
            parsed_url = urlparse(url)
            if parsed_url.path is None or len(parsed_url.path) == 0:
                return url
            else:
                return parsed_url.path.split("/")[-1]

        @staticmethod
        def get_save_handler(dataset_id, selector):
            def handler(child_link: ChildLink, response: Fork.Response):
                if response.status == 200:
                    try:
                        document_name = child_link.tag.text if child_link.tag is not None and len(
                            child_link.tag.text.strip()) > 0 else child_link.url
                        paragraphs = get_split_model('web.md').parse(response.content)
                        DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(
                            {'name': document_name, 'paragraphs': paragraphs,
                             'meta': {'source_url': child_link.url, 'selector': selector},
                             'type': Type.web}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

            return handler

        def save_web(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self.CreateWebSerializers(data=instance).is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            if QuerySet(DataSet).filter(user_id=user_id, name=instance.get('name')).exists():
                raise AppApiException(500, "Repeat the name of the knowledge base!")
            dataset_id = uuid.uuid1()
            dataset = DataSet(
                **{'id': dataset_id, 'name': instance.get("name"), 'desc': instance.get('desc'), 'user_id': user_id,
                   'type': Type.web,
                   'meta': {'source_url': instance.get('source_url'), 'selector': instance.get('selector')}})
            dataset.save()
            ListenerManagement.sync_web_dataset_signal.send(
                SyncWebDatasetArgs(str(dataset_id), instance.get('source_url'), instance.get('selector'),
                                   self.get_save_handler(dataset_id, instance.get('selector'))))
            return {**DataSetSerializers(dataset).data,
                    'document_list': []}

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                          'update_time', 'create_time', 'document_list'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="The name",
                                           description="The name", default="Testing knowledge."),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="described",
                                           description="described", default="Test Knowledge Base Description"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="The Userid",
                                              description="The Userid", default="user_xxxx"),
                    'char_length': openapi.Schema(type=openapi.TYPE_STRING, title="Number of characters",
                                                  description="Number of characters", default=10),
                    'document_count': openapi.Schema(type=openapi.TYPE_STRING, title="Number of documents",
                                                     description="Number of documents", default=1),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                  description="Change time.",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                  description="Creating time.",
                                                  default="1970-01-01 00:00:00"
                                                  ),
                    'document_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="List of documents",
                                                    description="List of documents",
                                                    items=DocumentSerializers.Operate.get_response_body_api())
                }
            )

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of Knowledge Base", description="Name of Knowledge Base"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Knowledge Base Description", description="Knowledge Base Description"),
                    'documents': openapi.Schema(type=openapi.TYPE_ARRAY, title="Documents Data", description="Documents Data",
                                                items=DocumentSerializers().Create.get_request_body_api()
                                                )
                }
            )

    class Edit(serializers.Serializer):
        name = serializers.CharField(required=False, max_length=64, min_length=1,
                                     error_messages=ErrMessage.char("Name of Knowledge Base"))
        desc = serializers.CharField(required=False, max_length=256, min_length=1,
                                     error_messages=ErrMessage.char("Knowledge Base Description"))
        meta = serializers.DictField(required=False)
        application_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True,
                                                                                                     error_messages=ErrMessage.char(
                                                                                                         "Applicationsid")),
                                                         error_messages=ErrMessage.char("Applied lists"))

        @staticmethod
        def get_dataset_meta_valid_map():
            dataset_meta_valid_map = {
                Type.base: MetaSerializer.BaseMeta,
                Type.web: MetaSerializer.WebMeta
            }
            return dataset_meta_valid_map

        def is_valid(self, *, dataset: DataSet = None):
            super().is_valid(raise_exception=True)
            if 'meta' in self.data and self.data.get('meta') is not None:
                dataset_meta_valid_map = self.get_dataset_meta_valid_map()
                valid_class = dataset_meta_valid_map.get(dataset.type)
                valid_class(data=self.data.get('meta')).is_valid(raise_exception=True)

    class HitTest(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char("id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char("Usersid"))
        query_text = serializers.CharField(required=True, error_messages=ErrMessage.char("Question of text."))
        top_number = serializers.IntegerField(required=True, max_value=10, min_value=1,
                                              error_messages=ErrMessage.char("ReplyTop"))
        similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                            error_messages=ErrMessage.char("similarity"))
        search_mode = serializers.CharField(required=True, validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message="Type only supports.register|reset_password", code=500)
        ], error_messages=ErrMessage.char("The search model."))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "idThere is no")

        def hit_test(self):
            self.is_valid()
            vector = VectorStore.get_embedding_vector()
            exclude_document_id_list = [str(document.id) for document in
                                        QuerySet(Document).filter(
                                            dataset_id=self.data.get('id'),
                                            is_active=False)]
            # Recovered to Quantum.
            hit_list = vector.hit_test(self.data.get('query_text'), [self.data.get('id')], exclude_document_id_list,
                                       self.data.get('top_number'),
                                       self.data.get('similarity'),
                                       SearchMode(self.data.get('search_mode')),
                                       EmbeddingModel.get_embedding_model())
            hit_dict = reduce(lambda x, y: {**x, **y}, [{hit.get('paragraph_id'): hit} for hit in hit_list], {})
            p_list = list_paragraph([h.get('paragraph_id') for h in hit_list])
            return [{**p, 'similarity': hit_dict.get(p.get('id')).get('similarity'),
                     'comprehensive_score': hit_dict.get(p.get('id')).get('comprehensive_score')} for p in p_list]

    class SyncWeb(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "The knowledge baseid"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(
            "Usersid"))
        sync_type = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "Types of Sync"), validators=[
            validators.RegexValidator(regex=re.compile("^replace|complete$"),
                                      message="Simultaneous types only support.:replace|complete", code=500)
        ])

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            first = QuerySet(DataSet).filter(id=self.data.get("id")).first()
            if first is None:
                raise AppApiException(300, "idThere is no")
            if first.type != Type.web:
                raise AppApiException(500, "OnlywebSite types support synchronization.")

        def sync(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            sync_type = self.data.get('sync_type')
            dataset_id = self.data.get('id')
            dataset = QuerySet(DataSet).get(id=dataset_id)
            self.__getattribute__(sync_type + '_sync')(dataset)
            return True

        @staticmethod
        def get_sync_handler(dataset):
            def handler(child_link: ChildLink, response: Fork.Response):
                if response.status == 200:
                    try:
                        document_name = child_link.tag.text if child_link.tag is not None and len(
                            child_link.tag.text.strip()) > 0 else child_link.url
                        paragraphs = get_split_model('web.md').parse(response.content)
                        first = QuerySet(Document).filter(meta__source_url=child_link.url, dataset=dataset).first()
                        if first is not None:
                            # If there is,Use the document sync.
                            DocumentSerializers.Sync(data={'document_id': first.id}).sync()
                        else:
                            # Inserted
                            DocumentSerializers.Create(data={'dataset_id': dataset.id}).save(
                                {'name': document_name, 'paragraphs': paragraphs,
                                 'meta': {'source_url': child_link.url, 'selector': dataset.meta.get('selector')},
                                 'type': Type.web}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

            return handler

        def replace_sync(self, dataset):
            """
            Replacement of Sync.
            :return:
            """
            url = dataset.meta.get('source_url')
            selector = dataset.meta.get('selector') if 'selector' in dataset.meta else None
            ListenerManagement.sync_web_dataset_signal.send(
                SyncWebDatasetArgs(str(dataset.id), url, selector,
                                   self.get_sync_handler(dataset)))

        def complete_sync(self, dataset):
            """
            Complete synchronization  Remove all current data collected documents.,Another synchronization.
            :return:
            """
            # Remove related issues.
            QuerySet(ProblemParagraphMapping).filter(dataset=dataset).delete()
            # Delete the document.
            QuerySet(Document).filter(dataset=dataset).delete()
            # Delete the paragraph.
            QuerySet(Paragraph).filter(dataset=dataset).delete()
            # Remove the quantity.
            ListenerManagement.delete_embedding_by_dataset_signal.send(self.data.get('id'))
            # synchronized
            self.replace_sync(dataset)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='sync_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Types of Sync->replace:Replacement of Sync.,complete:Complete synchronization')
                    ]

    class Operate(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "The knowledge baseid"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(
            "Usersid"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "idThere is no")

        @transaction.atomic
        def delete(self):
            self.is_valid()
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            QuerySet(Document).filter(dataset=dataset).delete()
            QuerySet(ProblemParagraphMapping).filter(dataset=dataset).delete()
            QuerySet(Paragraph).filter(dataset=dataset).delete()
            QuerySet(Problem).filter(dataset=dataset).delete()
            dataset.delete()
            ListenerManagement.delete_embedding_by_dataset_signal.send(self.data.get('id'))
            return True

        def list_application(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            return select_list(get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_application.sql')),
                [self.data.get('user_id') if self.data.get('user_id') == str(dataset.user_id) else None,
                 dataset.user_id, self.data.get('user_id')])

        def one(self, user_id, with_valid=True):
            if with_valid:
                self.is_valid()
            query_set_dict = {'default_sql': QuerySet(model=get_dynamics_model(
                {'temp.id': models.UUIDField()})).filter(**{'temp.id': self.data.get("id")}),
                              'dataset_custom_sql': QuerySet(model=get_dynamics_model(
                                  {'dataset.user_id': models.CharField()})).filter(
                                  **{'dataset.user_id': user_id}
                              ), 'team_member_permission_custom_sql': QuerySet(
                    model=get_dynamics_model({'user_id': models.CharField(),
                                              'team_member_permission.operate': ArrayField(
                                                  verbose_name="Authorization operating list",
                                                  base_field=models.CharField(max_length=256,
                                                                              blank=True,
                                                                              choices=AuthOperate.choices,
                                                                              default=AuthOperate.USE)
                                              )})).filter(
                    **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE']})}
            all_application_list = [str(adm.get('id')) for adm in self.list_application(with_valid=False)]
            return {**native_search(query_set_dict, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')), with_search_one=True),
                'application_id_list': list(
                    filter(lambda application_id: all_application_list.__contains__(application_id),
                           [str(application_dataset_mapping.application_id) for
                            application_dataset_mapping in
                            QuerySet(ApplicationDatasetMapping).filter(
                                dataset_id=self.data.get('id'))]))}

        def edit(self, dataset: Dict, user_id: str):
            """
            Modifying the Knowledge Base
            :param user_id: Usersid
            :param dataset: Dict name desc
            :return:
            """
            self.is_valid()
            if QuerySet(DataSet).filter(user_id=user_id, name=dataset.get('name')).exclude(
                    id=self.data.get('id')).exists():
                raise AppApiException(500, "Repeat the name of the knowledge base!")
            _dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            DataSetSerializers.Edit(data=dataset).is_valid(dataset=_dataset)
            if "name" in dataset:
                _dataset.name = dataset.get("name")
            if 'desc' in dataset:
                _dataset.desc = dataset.get("desc")
            if 'meta' in dataset:
                _dataset.meta = dataset.get('meta')
            if 'application_id_list' in dataset and dataset.get('application_id_list') is not None:
                application_id_list = dataset.get('application_id_list')
                # Current users can modify the list of related knowledge bases
                application_dataset_id_list = [str(dataset_dict.get('id')) for dataset_dict in
                                               self.list_application(with_valid=False)]
                for dataset_id in application_id_list:
                    if not application_dataset_id_list.__contains__(dataset_id):
                        raise AppApiException(500, f"Unknown Applicationid${dataset_id},not connected.")

                # Removing already connected.id
                QuerySet(ApplicationDatasetMapping).filter(application_id__in=application_dataset_id_list,
                                                           dataset_id=self.data.get("id")).delete()
                # Inserted
                QuerySet(ApplicationDatasetMapping).bulk_create(
                    [ApplicationDatasetMapping(application_id=application_id, dataset_id=self.data.get('id')) for
                     application_id in
                     application_id_list]) if len(application_id_list) > 0 else None
                [ApplicationDatasetMapping(application_id=application_id, dataset_id=self.data.get('id')) for
                 application_id in application_id_list]

            _dataset.save()
            return self.one(with_valid=False, user_id=user_id)

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of Knowledge Base", description="Name of Knowledge Base"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Knowledge Base Description", description="Knowledge Base Description"),
                    'meta': openapi.Schema(type=openapi.TYPE_OBJECT, title="Database of Knowledge",
                                           description="Database of Knowledge->web:{source_url:xxx,selector:'xxx'},base:{}"),
                    'application_id_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="ApplicationsidList of",
                                                          description="ApplicationsidList of",
                                                          items=openapi.Schema(type=openapi.TYPE_STRING))
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                          'update_time', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="The name",
                                           description="The name", default="Testing knowledge."),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="described",
                                           description="described", default="Test Knowledge Base Description"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="The Userid",
                                              description="The Userid", default="user_xxxx"),
                    'char_length': openapi.Schema(type=openapi.TYPE_STRING, title="Number of characters",
                                                  description="Number of characters", default=10),
                    'document_count': openapi.Schema(type=openapi.TYPE_STRING, title="Number of documents",
                                                     description="Number of documents", default=1),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                  description="Change time.",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                  description="Creating time.",
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid')
                    ]
