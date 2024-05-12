# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： document_serializers.py
    @date：2023/9/22 13:43
    @desc:
"""
import logging
import os
import re
import traceback
import uuid
from functools import reduce
from typing import List, Dict

from django.core import validators
from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import native_search, native_page_search
from common.event.common import work_thread_pool
from common.event.listener_manage import ListenerManagement, SyncWebDocumentArgs, UpdateEmbeddingDatasetIdArgs
from common.exception.app_exception import AppApiException
from common.handle.impl.doc_split_handle import DocSplitHandle
from common.handle.impl.pdf_split_handle import PdfSplitHandle
from common.handle.impl.text_split_handle import TextSplitHandle
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import Fork
from common.util.split_model import get_split_model
from dataset.models.data_set import DataSet, Document, Paragraph, Problem, Type, Status, ProblemParagraphMapping, Image
from dataset.serializers.common_serializers import BatchSerializer, MetaSerializer
from dataset.serializers.paragraph_serializers import ParagraphSerializers, ParagraphInstanceSerializer
from smartdoc.conf import PROJECT_DIR


class DocumentEditInstanceSerializer(ApiMixin, serializers.Serializer):
    meta = serializers.DictField(required=False)
    name = serializers.CharField(required=False, max_length=128, min_length=1,
                                 error_messages=ErrMessage.char(
                                     "Name of documentation"))
    hit_handling_method = serializers.CharField(required=False, validators=[
        validators.RegexValidator(regex=re.compile("^optimization|directly_return$"),
                                  message="Type only supports.optimization|directly_return",
                                  code=500)
    ], error_messages=ErrMessage.char("Method of Treatment"))

    directly_return_similarity = serializers.FloatField(required=False,
                                                        max_value=2,
                                                        min_value=0,
                                                        error_messages=ErrMessage.float(
                                                            "Return score directly"))

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(
        "Is documentation available?"))

    @staticmethod
    def get_meta_valid_map():
        dataset_meta_valid_map = {
            Type.base: MetaSerializer.BaseMeta,
            Type.web: MetaSerializer.WebMeta
        }
        return dataset_meta_valid_map

    def is_valid(self, *, document: Document = None):
        super().is_valid(raise_exception=True)
        if 'meta' in self.data and self.data.get('meta') is not None:
            dataset_meta_valid_map = self.get_meta_valid_map()
            valid_class = dataset_meta_valid_map.get(document.type)
            valid_class(data=self.data.get('meta')).is_valid(raise_exception=True)


class DocumentWebInstanceSerializer(ApiMixin, serializers.Serializer):
    source_url_list = serializers.ListField(required=True,
                                            child=serializers.CharField(required=True, error_messages=ErrMessage.char(
                                                "The document address.")),
                                            error_messages=ErrMessage.char(
                                                "List of documents"))
    selector = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char(
                                         "The Selector"))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['source_url_list'],
            properties={
                'source_url_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="List of paragraphs", description="List of paragraphs",
                                                  items=openapi.Schema(type=openapi.TYPE_STRING)),
                'selector': openapi.Schema(type=openapi.TYPE_STRING, title="Name of documentation", description="Name of documentation")
            }
        )


class DocumentInstanceSerializer(ApiMixin, serializers.Serializer):
    name = serializers.CharField(required=True,
                                 error_messages=ErrMessage.char("Name of documentation"),
                                 max_length=128,
                                 min_length=1)

    paragraphs = ParagraphInstanceSerializer(required=False, many=True, allow_null=True)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'paragraphs'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of documentation", description="Name of documentation"),
                'paragraphs': openapi.Schema(type=openapi.TYPE_ARRAY, title="List of paragraphs", description="List of paragraphs",
                                             items=ParagraphSerializers.Create.get_request_body_api())
            }
        )


class DocumentSerializers(ApiMixin, serializers.Serializer):
    class Migrate(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True,
                                           error_messages=ErrMessage.char(
                                               "The knowledge baseid"))
        target_dataset_id = serializers.UUIDField(required=True,
                                                  error_messages=ErrMessage.char(
                                                      "The target knowledge baseid"))
        document_id_list = serializers.ListField(required=True, error_messages=ErrMessage.char("List of documents"),
                                                 child=serializers.UUIDField(required=True,
                                                                             error_messages=ErrMessage.uuid("Documentsid")))

        @transaction.atomic
        def migrate(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            target_dataset_id = self.data.get('target_dataset_id')
            dataset = QuerySet(DataSet).filter(id=dataset_id).first()
            target_dataset = QuerySet(DataSet).filter(id=target_dataset_id).first()
            document_id_list = self.data.get('document_id_list')
            document_list = QuerySet(Document).filter(dataset_id=dataset_id, id__in=document_id_list)
            paragraph_list = QuerySet(Paragraph).filter(dataset_id=dataset_id, document_id__in=document_id_list)

            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(paragraph__in=paragraph_list)
            problem_list = QuerySet(Problem).filter(
                id__in=[problem_paragraph_mapping.problem_id for problem_paragraph_mapping in
                        problem_paragraph_mapping_list])
            target_problem_list = list(
                QuerySet(Problem).filter(content__in=[problem.content for problem in problem_list],
                                         dataset_id=target_dataset_id))
            target_handle_problem_list = [
                self.get_target_dataset_problem(target_dataset_id, problem_paragraph_mapping,
                                                problem_list, target_problem_list) for
                problem_paragraph_mapping
                in
                problem_paragraph_mapping_list]

            create_problem_list = [problem for problem, is_create in target_handle_problem_list if
                                   is_create is not None and is_create]
            # Inserting the problem.
            QuerySet(Problem).bulk_create(create_problem_list)
            # Modifiedmapping
            QuerySet(ProblemParagraphMapping).bulk_update(problem_paragraph_mapping_list, ['problem_id', 'dataset_id'])
            # Modifying the document.
            if dataset.type == Type.base.value and target_dataset.type == Type.web.value:
                document_list.update(dataset_id=target_dataset_id, type=Type.web,
                                     meta={'source_url': '', 'selector': ''})
            elif target_dataset.type == Type.base.value and dataset.type == Type.web.value:
                document_list.update(dataset_id=target_dataset_id, type=Type.base,
                                     meta={})
            else:
                document_list.update(dataset_id=target_dataset_id)
            # 修改向量信息
            ListenerManagement.update_embedding_dataset_id(UpdateEmbeddingDatasetIdArgs(
                [paragraph.id for paragraph in paragraph_list],
                target_dataset_id))
            # 修改段落信息
            paragraph_list.update(dataset_id=target_dataset_id)

        @staticmethod
        def get_target_dataset_problem(target_dataset_id: str,
                                       problem_paragraph_mapping,
                                       source_problem_list,
                                       target_problem_list):
            source_problem_list = [source_problem for source_problem in source_problem_list if
                                   source_problem.id == problem_paragraph_mapping.problem_id]
            problem_paragraph_mapping.dataset_id = target_dataset_id
            if len(source_problem_list) > 0:
                problem_content = source_problem_list[-1].content
                problem_list = [problem for problem in target_problem_list if problem.content == problem_content]
                if len(problem_list) > 0:
                    problem = problem_list[-1]
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, False
                else:
                    problem = Problem(id=uuid.uuid1(), dataset_id=target_dataset_id, content=problem_content)
                    target_problem_list.append(problem)
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, True
            return None

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='target_dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The target knowledge baseid')
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                title='DocumentsidList of',
                description="DocumentsidList of"
            )

    class Query(ApiMixin, serializers.Serializer):
        # The knowledge baseid
        dataset_id = serializers.UUIDField(required=True,
                                           error_messages=ErrMessage.char(
                                               "The knowledge baseid"))

        name = serializers.CharField(required=False, max_length=128,
                                     min_length=1,
                                     error_messages=ErrMessage.char(
                                         "Name of documentation"))
        hit_handling_method = serializers.CharField(required=False, error_messages=ErrMessage.char("Method of Treatment"))

        def get_query_set(self):
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'dataset_id': self.data.get("dataset_id")})
            if 'name' in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'name__icontains': self.data.get('name')})
            if 'hit_handling_method' in self.data and self.data.get('hit_handling_method') is not None:
                query_set = query_set.filter(**{'hit_handling_method': self.data.get('hit_handling_method')})
            query_set = query_set.order_by('-create_time')
            return query_set

        def list(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_query_set()
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return native_page_search(current_page, page_size, query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Name of documentation'),
                    openapi.Parameter(name='hit_handling_method', in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Method of handling documents.')]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY,
                                  title="List of documents", description="List of documents",
                                  items=DocumentSerializers.Operate.get_response_body_api())

    class Sync(ApiMixin, serializers.Serializer):
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            first = QuerySet(Document).filter(id=document_id).first()
            if first is None:
                raise AppApiException(500, "DocumentsidThere is no")
            if first.type != Type.web:
                raise AppApiException(500, "OnlywebSite types support synchronization.")

        def sync(self, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            document = QuerySet(Document).filter(id=document_id).first()
            if document.type != Type.web:
                return True
            try:
                document.status = Status.embedding
                document.save()
                source_url = document.meta.get('source_url')
                selector_list = document.meta.get('selector').split(
                    " ") if 'selector' in document.meta and document.meta.get('selector') is not None else []
                result = Fork(source_url, selector_list).fork()
                if result.status == 200:
                    # Delete the paragraph.
                    QuerySet(model=Paragraph).filter(document_id=document_id).delete()
                    # Delete the problem.
                    QuerySet(model=ProblemParagraphMapping).filter(document_id=document_id).delete()
                    # Remove to the quantum.
                    ListenerManagement.delete_embedding_by_document_signal.send(document_id)
                    paragraphs = get_split_model('web.md').parse(result.content)
                    document.char_length = reduce(lambda x, y: x + y,
                                                  [len(p.get('content')) for p in paragraphs],
                                                  0)
                    document.save()
                    document_paragraph_model = DocumentSerializers.Create.get_paragraph_model(document, paragraphs)

                    paragraph_model_list = document_paragraph_model.get('paragraph_model_list')
                    problem_model_list = document_paragraph_model.get('problem_model_list')
                    problem_paragraph_mapping_list = document_paragraph_model.get('problem_paragraph_mapping_list')
                    # Introduction to paragraphs
                    QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
                    # Mass Injection Problems
                    QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
                    # Introduction to Related Problems
                    QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                        problem_paragraph_mapping_list) > 0 else None
                    # to Quantity.
                    if with_embedding:
                        ListenerManagement.embedding_by_document_signal.send(document_id)
                else:
                    document.status = Status.error
                    document.save()
            except Exception as e:
                logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
                document.status = Status.error
                document.save()
            return True

    class Operate(ApiMixin, serializers.Serializer):
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Documentsid')
                    ]

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            if not QuerySet(Document).filter(id=document_id).exists():
                raise AppApiException(500, "DocumentsidThere is no")

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'id': self.data.get("document_id")})
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')), with_search_one=True)

        def edit(self, instance: Dict, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            _document = QuerySet(Document).get(id=self.data.get("document_id"))
            if with_valid:
                DocumentEditInstanceSerializer(data=instance).is_valid(document=_document)
            update_keys = ['name', 'is_active', 'hit_handling_method', 'directly_return_similarity', 'meta']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    _document.__setattr__(update_key, instance.get(update_key))
            _document.save()
            return self.one()

        def refresh(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_id = self.data.get("document_id")
            document = QuerySet(Document).filter(id=document_id).first()
            if document.type == Type.web:
                # The synchronization
                work_thread_pool.submit(lambda x: DocumentSerializers.Sync(data={'document_id': document_id}).sync(),
                                        {})

            else:
                if document.status != Status.embedding.value:
                    document.status = Status.embedding
                    document.save()
                ListenerManagement.embedding_by_document_signal.send(document_id)
            return True

        @transaction.atomic
        def delete(self):
            document_id = self.data.get("document_id")
            QuerySet(model=Document).filter(id=document_id).delete()
            # Delete the paragraph.
            QuerySet(model=Paragraph).filter(document_id=document_id).delete()
            # Delete the problem.
            QuerySet(model=ProblemParagraphMapping).filter(document_id=document_id).delete()
            # Remove to the quantum.
            ListenerManagement.delete_embedding_by_document_signal.send(document_id)
            return True

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'char_length', 'user_id', 'paragraph_count', 'is_active'
                                                                                     'update_time', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="The name",
                                           description="The name", default="Testing knowledge."),
                    'char_length': openapi.Schema(type=openapi.TYPE_INTEGER, title="Number of characters",
                                                  description="Number of characters", default=10),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="Usersid", description="Usersid"),
                    'paragraph_count': openapi.Schema(type=openapi.TYPE_INTEGER, title="Number of documents",
                                                      description="Number of documents", default=1),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is Available",
                                                description="Is Available", default=True),
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
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Document Name", description="Document Name"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is it available", description="Is it available"),
                    'hit_handling_method': openapi.Schema(type=openapi.TYPE_STRING, title="hit handling method",
                                                        description="ai optimization: optimization, direct return: directly_return"),
                    'directly_return_similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title="Return the score directly",
                                                                default=0.9),
                    'meta': openapi.Schema(type=openapi.TYPE_OBJECT, title="Document metadata",
                                        description="Document metadata->web:{source_url:xxx,selector:'xxx'},base:{}"),
                }
            )

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get('dataset_id')).exists():
                raise AppApiException(10000, "The knowledge baseidThere is no")
            return True

        @staticmethod
        def post_embedding(result, document_id):
            ListenerManagement.embedding_by_document_signal.send(document_id)
            return result

        @post(post_function=post_embedding)
        @transaction.atomic
        def save(self, instance: Dict, with_valid=False, **kwargs):
            if with_valid:
                DocumentInstanceSerializer(data=instance).is_valid(raise_exception=True)
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            document_paragraph_model = self.get_document_paragraph_model(dataset_id, instance)
            document_model = document_paragraph_model.get('document')
            paragraph_model_list = document_paragraph_model.get('paragraph_model_list')
            problem_model_list = document_paragraph_model.get('problem_model_list')
            problem_paragraph_mapping_list = document_paragraph_model.get('problem_paragraph_mapping_list')

            # Insert the document.
            document_model.save()
            # Introduction to paragraphs
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # Mass Injection Problems
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # A lot of connected issues.
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None
            document_id = str(document_model.id)
            return DocumentSerializers.Operate(
                data={'dataset_id': dataset_id, 'document_id': document_id}).one(
                with_valid=True), document_id

        @staticmethod
        def get_sync_handler(dataset_id):
            def handler(source_url: str, selector, response: Fork.Response):
                if response.status == 200:
                    try:
                        paragraphs = get_split_model('web.md').parse(response.content)
                        # Inserted
                        DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(
                            {'name': source_url, 'paragraphs': paragraphs,
                             'meta': {'source_url': source_url, 'selector': selector},
                             'type': Type.web}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')
                else:
                    Document(name=source_url,
                             meta={'source_url': source_url, 'selector': selector},
                             type=Type.web,
                             char_length=0,
                             status=Status.error).save()

            return handler

        def save_web(self, instance: Dict, with_valid=True):
            if with_valid:
                DocumentWebInstanceSerializer(data=instance).is_valid(raise_exception=True)
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            source_url_list = instance.get('source_url_list')
            selector = instance.get('selector')
            args = SyncWebDocumentArgs(source_url_list, selector, self.get_sync_handler(dataset_id))
            ListenerManagement.sync_web_document_signal.send(args)

        @staticmethod
        def get_paragraph_model(document_model, paragraph_list: List):
            dataset_id = document_model.dataset_id
            paragraph_model_dict_list = [ParagraphSerializers.Create(
                data={'dataset_id': dataset_id, 'document_id': str(document_model.id)}).get_paragraph_problem_model(
                dataset_id, document_model.id, paragraph) for paragraph in paragraph_list]

            paragraph_model_list = []
            problem_model_list = []
            problem_paragraph_mapping_list = []
            for paragraphs in paragraph_model_dict_list:
                paragraph = paragraphs.get('paragraph')
                for problem_model in paragraphs.get('problem_model_list'):
                    problem_model_list.append(problem_model)
                for problem_paragraph_mapping in paragraphs.get('problem_paragraph_mapping_list'):
                    problem_paragraph_mapping_list.append(problem_paragraph_mapping)
                paragraph_model_list.append(paragraph)

            return {'document': document_model, 'paragraph_model_list': paragraph_model_list,
                    'problem_model_list': problem_model_list,
                    'problem_paragraph_mapping_list': problem_paragraph_mapping_list}

        @staticmethod
        def get_document_paragraph_model(dataset_id, instance: Dict):
            document_model = Document(
                **{'dataset_id': dataset_id,
                   'id': uuid.uuid1(),
                   'name': instance.get('name'),
                   'char_length': reduce(lambda x, y: x + y,
                                         [len(p.get('content')) for p in instance.get('paragraphs', [])],
                                         0),
                   'meta': instance.get('meta') if instance.get('meta') is not None else {},
                   'type': instance.get('type') if instance.get('type') is not None else Type.base})

            return DocumentSerializers.Create.get_paragraph_model(document_model,
                                                                  instance.get('paragraphs') if
                                                                  'paragraphs' in instance else [])

        @staticmethod
        def get_request_body_api():
            return DocumentInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid')
                    ]

    class Split(ApiMixin, serializers.Serializer):
        file = serializers.ListField(required=True, error_messages=ErrMessage.list(
            "List of documents"))

        limit = serializers.IntegerField(required=False, error_messages=ErrMessage.integer(
            "Part length"))

        patterns = serializers.ListField(required=False,
                                         child=serializers.CharField(required=True, error_messages=ErrMessage.char(
                                             "Parts of identification.")),
                                         error_messages=ErrMessage.uuid(
                                             "Part Identification List"))

        with_filter = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(
            "Automatic cleaning."))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            files = self.data.get('file')
            for f in files:
                if f.size > 1024 * 1024 * 100:
                    raise AppApiException(500, "The maximum file can not exceed.100MB")

        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_ARRAY,
                                  items=openapi.Items(type=openapi.TYPE_FILE),
                                  required=True,
                                  description='uploaded documents'),
                openapi.Parameter(name='limit',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_INTEGER, title="Part length", description="Part length"),
                openapi.Parameter(name='patterns',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                  title="Section Rules List", description="Section Rules List"),
                openapi.Parameter(name='with_filter',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_BOOLEAN, title="Remove special characters.", description="Remove special characters."),
            ]

        def parse(self):
            file_list = self.data.get("file")
            return list(
                map(lambda f: file_to_paragraph(f, self.data.get("patterns", None), self.data.get("with_filter", None),
                                                self.data.get("limit", None)), file_list))

    class SplitPattern(ApiMixin, serializers.Serializer):
        @staticmethod
        def list():
            return [{'key': "#", 'value': '(?<=^)# .*|(?<=\\n)# .*'},
                    {'key': '##', 'value': '(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'},
                    {'key': '###', 'value': "(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"},
                    {'key': '####', 'value': "(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"},
                    {'key': '#####', 'value': "(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"},
                    {'key': '######', 'value': "(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"},
                    {'key': '-', 'value': '(?<! )- .*'},
                    {'key': 'The Space', 'value': '(?<!\\s)\\s(?!\\s)'},
                    {'key': 'Number of', 'value': '(?<!；)；(?!；)'}, {'key': 'The Comedy', 'value': '(?<!，)，(?!，)'},
                    {'key': 'The phrase', 'value': '(?<!。)。(?!。)'}, {'key': 'Back to car.', 'value': '(?<!\\n)\\n(?!\\n)'},
                    {'key': 'The empty', 'value': '(?<!\\n)\\n\\n(?!\\n)'}]

    class Batch(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The knowledge baseid"))

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY, items=DocumentSerializers.Create.get_request_body_api())

        @staticmethod
        def post_embedding(document_list):
            for document_dict in document_list:
                ListenerManagement.embedding_by_document_signal.send(document_dict.get('id'))
            return document_list

        @post(post_function=post_embedding)
        @transaction.atomic
        def batch_save(self, instance_list: List[Dict], with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            DocumentInstanceSerializer(many=True, data=instance_list).is_valid(raise_exception=True)
            dataset_id = self.data.get("dataset_id")
            document_model_list = []
            paragraph_model_list = []
            problem_model_list = []
            problem_paragraph_mapping_list = []
            # Insert the document.
            for document in instance_list:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(dataset_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem in document_paragraph_dict_model.get('problem_model_list'):
                    problem_model_list.append(problem)
                for problem_paragraph_mapping in document_paragraph_dict_model.get('problem_paragraph_mapping_list'):
                    problem_paragraph_mapping_list.append(problem_paragraph_mapping)

            # Insert the document.
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # Introduction to paragraphs
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # Mass Injection Problems
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # A lot of connected issues.
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None
            # Ask for documents.
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'id__in': [d.id for d in document_model_list]})
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')), with_search_one=False),

        @staticmethod
        def _batch_sync(document_id_list: List[str]):
            for document_id in document_id_list:
                DocumentSerializers.Sync(data={'document_id': document_id}).sync()

        def batch_sync(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                self.is_valid(raise_exception=True)
            # The synchronization
            work_thread_pool.submit(self._batch_sync,
                                    instance.get('id_list'))
            return True

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                self.is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            QuerySet(Document).filter(id__in=document_id_list).delete()
            QuerySet(Paragraph).filter(document_id__in=document_id_list).delete()
            QuerySet(ProblemParagraphMapping).filter(document_id__in=document_id_list).delete()
            # Remove to the quantum.
            ListenerManagement.delete_embedding_by_document_list_signal.send(document_id_list)
            return True

        def batch_edit_hit_handling(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                hit_handling_method = instance.get('hit_handling_method')
                if hit_handling_method is None:
                    raise AppApiException(500, 'The treatment method must be filled.')
                if hit_handling_method != 'optimization' and hit_handling_method != 'directly_return':
                    raise AppApiException(500, 'The treatment method must bedirectly_return|optimization')
                self.is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            hit_handling_method = instance.get('hit_handling_method')
            directly_return_similarity = instance.get('directly_return_similarity')
            update_dict = {'hit_handling_method': hit_handling_method}
            if directly_return_similarity is not None:
                update_dict['directly_return_similarity'] = directly_return_similarity
            QuerySet(Document).filter(id__in=document_id_list).update(**update_dict)


class FileBufferHandle:
    buffer = None

    def get_buffer(self, file):
        if self.buffer is None:
            self.buffer = file.read()
        return self.buffer


default_split_handle = TextSplitHandle()
split_handles = [DocSplitHandle(), PdfSplitHandle(), default_split_handle]


def save_image(image_list):
    QuerySet(Image).bulk_create(image_list)


def file_to_paragraph(file, pattern_list: List, with_filter: bool, limit: int):
    get_buffer = FileBufferHandle().get_buffer
    for split_handle in split_handles:
        if split_handle.support(file, get_buffer):
            return split_handle.handle(file, pattern_list, with_filter, limit, get_buffer, save_image)
    return default_split_handle.handle(file, pattern_list, with_filter, limit, get_buffer, save_image)
