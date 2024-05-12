# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： paragraph_serializers.py
    @date：2023/10/16 15:51
    @desc:
"""
import uuid
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import page_search
from common.event.listener_manage import ListenerManagement, UpdateEmbeddingDocumentIdArgs, UpdateEmbeddingDatasetIdArgs
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.field_message import ErrMessage
from dataset.models import Paragraph, Problem, Document, ProblemParagraphMapping
from dataset.serializers.common_serializers import update_document_char_length, BatchSerializer
from dataset.serializers.problem_serializers import ProblemInstanceSerializer, ProblemSerializer, ProblemSerializers
from embedding.models import SourceType


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'content', 'is_active', 'document_id', 'title',
                  'create_time', 'update_time']


class ParagraphInstanceSerializer(ApiMixin, serializers.Serializer):
    """
    Subjects of implementation
    """
    content = serializers.CharField(required=True, error_messages=ErrMessage.char("Contents of paragraph"),
                                    max_length=4096,
                                    min_length=1,
                                    allow_null=True, allow_blank=True)

    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char("Title of paragraph"),
                                  allow_null=True, allow_blank=True)

    problem_list = ProblemInstanceSerializer(required=False, many=True)

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char("The paragraph is available."))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title="Part of content.",
                                          description="Part of content."),

                'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title="Section title",
                                        description="Section title"),

                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is Available", description="Is Available"),

                'problem_list': openapi.Schema(type=openapi.TYPE_ARRAY, title='List of Questions',
                                               description="List of Questions",
                                               items=ProblemInstanceSerializer.get_request_body_api())
            }
        )


class EditParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        "Section title"), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=False, max_length=4096, allow_null=True, allow_blank=True,
                                    error_messages=ErrMessage.char(
                                        "Part of content."))
    problem_list = ProblemInstanceSerializer(required=False, many=True)


class ParagraphSerializers(ApiMixin, serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        "Section title"), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=True, max_length=4096, error_messages=ErrMessage.char(
        "Part of content."))

    class Problem(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The knowledge baseid"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Documentsid"))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Paragraphsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "ParagraphsidThere is no")

        def list(self, with_valid=False):
            """
            Get a problem list.
            :param with_valid: is tested.
            :return: List of Questions
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get("dataset_id"),
                                                                                 paragraph_id=self.data.get(
                                                                                     'paragraph_id'))
            return [ProblemSerializer(row).data for row in
                    QuerySet(Problem).filter(id__in=[row.problem_id for row in problem_paragraph_mapping])]

        @transaction.atomic
        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid()
                ProblemInstanceSerializer(data=instance).is_valid(raise_exception=True)
            problem = QuerySet(Problem).filter(dataset_id=self.data.get('dataset_id'),
                                               content=instance.get('content')).first()
            if problem is None:
                problem = Problem(id=uuid.uuid1(), dataset_id=self.data.get('dataset_id'),
                                  content=instance.get('content'))
                problem.save()
            if QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get('dataset_id'), problem_id=problem.id,
                                                        paragraph_id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "already connected.,Do not repeat the connection.")
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(),
                                                                problem_id=problem.id,
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                dataset_id=self.data.get('dataset_id'))
            problem_paragraph_mapping.save()
            if with_embedding:
                ListenerManagement.embedding_by_problem_signal.send({'text': problem.content,
                                                                     'is_active': True,
                                                                     'source_type': SourceType.PROBLEM,
                                                                     'source_id': problem_paragraph_mapping.id,
                                                                     'document_id': self.data.get('document_id'),
                                                                     'paragraph_id': self.data.get('paragraph_id'),
                                                                     'dataset_id': self.data.get('dataset_id'),
                                                                     })

            return ProblemSerializers.Operate(
                data={'dataset_id': self.data.get('dataset_id'),
                      'problem_id': problem.id}).one(with_valid=True)

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
                                      description='Documentsid'),
                    openapi.Parameter(name='paragraph_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Paragraphsid')]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_OBJECT,
                                  required=["content"],
                                  properties={
                                      'content': openapi.Schema(
                                          type=openapi.TYPE_STRING, title="The content")
                                  })

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'dataset_id', 'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="The content of the question",
                                              description="The content of the question", default='The content of the question'),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="The number of fate", description="The number of fate",
                                              default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="The knowledge baseid",
                                                 description="The knowledge baseid", default='xxx'),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                  description="Change time.",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                  description="Creating time.",
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

    class Association(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The knowledge baseid"))

        problem_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The problemid"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Documentsid"))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Paragraphsid"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            paragraph_id = self.data.get('paragraph_id')
            problem_id = self.data.get("problem_id")
            if not QuerySet(Paragraph).filter(dataset_id=dataset_id, id=paragraph_id).exists():
                raise AppApiException(500, "The paragraph does not exist.")
            if not QuerySet(Problem).filter(dataset_id=dataset_id, id=problem_id).exists():
                raise AppApiException(500, "The problem does not exist.")

        def association(self, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem = QuerySet(Problem).filter(id=self.data.get("problem_id")).first()
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(),
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                dataset_id=self.data.get('dataset_id'),
                                                                problem_id=problem.id)
            problem_paragraph_mapping.save()
            if with_embedding:
                ListenerManagement.embedding_by_problem_signal.send({'text': problem.content,
                                                                     'is_active': True,
                                                                     'source_type': SourceType.PROBLEM,
                                                                     'source_id': problem_paragraph_mapping.id,
                                                                     'document_id': self.data.get('document_id'),
                                                                     'paragraph_id': self.data.get('paragraph_id'),
                                                                     'dataset_id': self.data.get('dataset_id'),
                                                                     })

        def un_association(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                paragraph_id=self.data.get('paragraph_id'),
                dataset_id=self.data.get('dataset_id'),
                problem_id=self.data.get(
                    'problem_id')).first()
            problem_paragraph_mapping_id = problem_paragraph_mapping.id
            problem_paragraph_mapping.delete()
            ListenerManagement.delete_embedding_by_source_signal.send(problem_paragraph_mapping_id)
            return True

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
                , openapi.Parameter(name='paragraph_id',
                                    in_=openapi.IN_PATH,
                                    type=openapi.TYPE_STRING,
                                    required=True,
                                    description='Paragraphsid'),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The problemid')
                    ]

    class Batch(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("文档id"))

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Paragraph, raise_exception=True)
                self.is_valid(raise_exception=True)
            paragraph_id_list = instance.get("id_list")
            QuerySet(Paragraph).filter(id__in=paragraph_id_list).delete()
            QuerySet(ProblemParagraphMapping).filter(paragraph_id__in=paragraph_id_list).delete()
            # 删除向量库
            ListenerManagement.delete_embedding_by_paragraph_ids(paragraph_id_list)
            return True

    class Migrate(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("文档id"))
        target_dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("目标知识库id"))
        target_document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("目标文档id"))
        paragraph_id_list = serializers.ListField(required=True, error_messages=ErrMessage.char("段落列表"),
                                                  child=serializers.UUIDField(required=True,
                                                                              error_messages=ErrMessage.uuid("段落id")))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_list = QuerySet(Document).filter(
                id__in=[self.data.get('document_id'), self.data.get('target_document_id')])
            document_id = self.data.get('document_id')
            target_document_id = self.data.get('target_document_id')
            if document_id == target_document_id:
                raise AppApiException(5000, "需要迁移的文档和目标文档一致")
            if len([document for document in document_list if str(document.id) == self.data.get('document_id')]) < 1:
                raise AppApiException(5000, f"文档id不存在【{self.data.get('document_id')}】")
            if len([document for document in document_list if
                    str(document.id) == self.data.get('target_document_id')]) < 1:
                raise AppApiException(5000, f"目标文档id不存在【{self.data.get('target_document_id')}】")

        @transaction.atomic
        def migrate(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            target_dataset_id = self.data.get('target_dataset_id')
            document_id = self.data.get('document_id')
            target_document_id = self.data.get('target_document_id')
            paragraph_id_list = self.data.get('paragraph_id_list')
            paragraph_list = QuerySet(Paragraph).filter(dataset_id=dataset_id, document_id=document_id,
                                                        id__in=paragraph_id_list)
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(paragraph__in=paragraph_list)
            # 同数据集迁移
            if target_dataset_id == dataset_id:
                if len(problem_paragraph_mapping_list):
                    problem_paragraph_mapping_list = [
                        self.update_problem_paragraph_mapping(target_document_id,
                                                              problem_paragraph_mapping) for problem_paragraph_mapping
                        in
                        problem_paragraph_mapping_list]
                    # 修改mapping
                    QuerySet(ProblemParagraphMapping).bulk_update(problem_paragraph_mapping_list,
                                                                  ['document_id'])
                # 修改向量段落信息
                ListenerManagement.update_embedding_document_id(UpdateEmbeddingDocumentIdArgs(
                    [paragraph.id for paragraph in paragraph_list],
                    target_document_id, target_dataset_id))
                # 修改段落信息
                paragraph_list.update(document_id=target_document_id)
            # 不同数据集迁移
            else:
                problem_list = QuerySet(Problem).filter(
                    id__in=[problem_paragraph_mapping.problem_id for problem_paragraph_mapping in
                            problem_paragraph_mapping_list])
                # 目标数据集问题
                target_problem_list = list(
                    QuerySet(Problem).filter(content__in=[problem.content for problem in problem_list],
                                             dataset_id=target_dataset_id))

                target_handle_problem_list = [
                    self.get_target_dataset_problem(target_dataset_id, target_document_id, problem_paragraph_mapping,
                                                    problem_list, target_problem_list) for
                    problem_paragraph_mapping
                    in
                    problem_paragraph_mapping_list]

                create_problem_list = [problem for problem, is_create in target_handle_problem_list if
                                       is_create is not None and is_create]
                # 插入问题
                QuerySet(Problem).bulk_create(create_problem_list)
                # 修改mapping
                QuerySet(ProblemParagraphMapping).bulk_update(problem_paragraph_mapping_list,
                                                              ['problem_id', 'dataset_id', 'document_id'])
                # 修改向量段落信息
                ListenerManagement.update_embedding_document_id(UpdateEmbeddingDocumentIdArgs(
                    [paragraph.id for paragraph in paragraph_list],
                    target_document_id, target_dataset_id))
                # 修改段落信息
                paragraph_list.update(dataset_id=target_dataset_id, document_id=target_document_id)

        @staticmethod
        def update_problem_paragraph_mapping(target_document_id: str, problem_paragraph_mapping):
            problem_paragraph_mapping.document_id = target_document_id
            return problem_paragraph_mapping

        @staticmethod
        def get_target_dataset_problem(target_dataset_id: str,
                                       target_document_id: str,
                                       problem_paragraph_mapping,
                                       source_problem_list,
                                       target_problem_list):
            source_problem_list = [source_problem for source_problem in source_problem_list if
                                   source_problem.id == problem_paragraph_mapping.problem_id]
            problem_paragraph_mapping.dataset_id = target_dataset_id
            problem_paragraph_mapping.document_id = target_document_id
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
                                      description='文档id'),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='文档id'),
                    openapi.Parameter(name='target_dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='目标知识库id'),
                    openapi.Parameter(name='target_document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='目标知识库id')
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                title='段落id列表',
                description="段落id列表"
            )

    class Operate(ApiMixin, serializers.Serializer):
        # Paragraphsid
        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Paragraphsid"))
        # The knowledge baseid
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "The knowledge baseid"))
        # Documentsid
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "ParagraphsidThere is no")

        @staticmethod
        def post_embedding(paragraph, instance):
            if 'is_active' in instance and instance.get('is_active') is not None:
                s = (ListenerManagement.enable_embedding_by_paragraph_signal if instance.get(
                    'is_active') else ListenerManagement.disable_embedding_by_paragraph_signal)
                s.send(paragraph.get('id'))
            else:
                ListenerManagement.embedding_by_paragraph_signal.send(paragraph.get('id'))
            return paragraph

        @post(post_embedding)
        @transaction.atomic
        def edit(self, instance: Dict):
            self.is_valid()
            EditParagraphSerializers(data=instance).is_valid(raise_exception=True)
            _paragraph = QuerySet(Paragraph).get(id=self.data.get("paragraph_id"))
            update_keys = ['title', 'content', 'is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    _paragraph.__setattr__(update_key, instance.get(update_key))

            if 'problem_list' in instance:
                update_problem_list = list(
                    filter(lambda row: 'id' in row and row.get('id') is not None, instance.get('problem_list')))

                create_problem_list = list(filter(lambda row: row.get('id') is None, instance.get('problem_list')))

                # Problems gathered
                problem_list = QuerySet(Problem).filter(paragraph_id=self.data.get("paragraph_id"))

                # The exam front. brought to.id
                for update_problem in update_problem_list:
                    if not set([str(row.id) for row in problem_list]).__contains__(update_problem.get('id')):
                        raise AppApiException(500, update_problem.get('id') + 'The problemidThere is no')
                # Problems that need to be removed.
                delete_problem_list = list(filter(
                    lambda row: not [str(update_row.get('id')) for update_row in update_problem_list].__contains__(
                        str(row.id)), problem_list)) if len(update_problem_list) > 0 else []
                # Delete the problem.
                QuerySet(Problem).filter(id__in=[row.id for row in delete_problem_list]).delete() if len(
                    delete_problem_list) > 0 else None
                # Create a new problem.
                QuerySet(Problem).bulk_create(
                    [Problem(id=uuid.uuid1(), content=p.get('content'), paragraph_id=self.data.get('paragraph_id'),
                             dataset_id=self.data.get('dataset_id'), document_id=self.data.get('document_id')) for
                     p in create_problem_list]) if len(create_problem_list) else None

                # Modification of Questions
                QuerySet(Problem).bulk_update(
                    [Problem(id=row.get('id'), content=row.get('content')) for row in update_problem_list],
                    ['content']) if len(
                    update_problem_list) > 0 else None

            _paragraph.save()
            update_document_char_length(self.data.get('document_id'))
            return self.one(), instance

        def get_problem_list(self):
            ProblemParagraphMapping(ProblemParagraphMapping)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                paragraph_id=self.data.get("paragraph_id"))
            if len(problem_paragraph_mapping) > 0:
                return [ProblemSerializer(problem).data for problem in
                        QuerySet(Problem).filter(id__in=[ppm.problem_id for ppm in problem_paragraph_mapping])]
            return []

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            return {**ParagraphSerializer(QuerySet(model=Paragraph).get(id=self.data.get('paragraph_id'))).data,
                    'problem_list': self.get_problem_list()}

        def delete(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            paragraph_id = self.data.get('paragraph_id')
            QuerySet(Paragraph).filter(id=paragraph_id).delete()
            QuerySet(ProblemParagraphMapping).filter(paragraph_id=paragraph_id).delete()
            ListenerManagement.delete_embedding_by_paragraph_signal.send(paragraph_id)

        @staticmethod
        def get_request_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_response_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(type=openapi.TYPE_STRING, in_=openapi.IN_PATH, name='paragraph_id',
                                      description="Paragraphsid")]

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "The knowledge baseid"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, "Documentsidwrongly.")

        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                ParagraphSerializers(data=instance).is_valid(raise_exception=True)
                self.is_valid()
            dataset_id = self.data.get("dataset_id")
            document_id = self.data.get('document_id')
            paragraph_problem_model = self.get_paragraph_problem_model(dataset_id, document_id, instance)
            paragraph = paragraph_problem_model.get('paragraph')
            problem_model_list = paragraph_problem_model.get('problem_model_list')
            problem_paragraph_mapping_list = paragraph_problem_model.get('problem_paragraph_mapping_list')
            # Insert the paragraph.
            paragraph_problem_model.get('paragraph').save()
            # Entering the problem.
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # Introduction to Relationship Problems
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None
            # Change the length.
            update_document_char_length(document_id)
            if with_embedding:
                ListenerManagement.embedding_by_paragraph_signal.send(str(paragraph.id))
            return ParagraphSerializers.Operate(
                data={'paragraph_id': str(paragraph.id), 'dataset_id': dataset_id, 'document_id': document_id}).one(
                with_valid=True)

        @staticmethod
        def get_paragraph_problem_model(dataset_id: str, document_id: str, instance: Dict):
            paragraph = Paragraph(id=uuid.uuid1(),
                                  document_id=document_id,
                                  content=instance.get("content"),
                                  dataset_id=dataset_id,
                                  title=instance.get("title") if 'title' in instance else '')
            problem_list = instance.get('problem_list')
            exists_problem_list = []
            if 'problem_list' in instance and len(problem_list) > 0:
                exists_problem_list = QuerySet(Problem).filter(dataset_id=dataset_id,
                                                               content__in=[p.get('content') for p in
                                                                            problem_list]).all()

            problem_model_list = [
                ParagraphSerializers.Create.or_get(exists_problem_list, problem.get('content'), dataset_id) for
                problem in (
                    instance.get('problem_list') if 'problem_list' in instance else [])]
            # The problem is heavy.
            problem_model_list = [x for i, x in enumerate(problem_model_list) if
                                  len([item for item in problem_model_list[:i] if item.content == x.content]) <= 0]

            problem_paragraph_mapping_list = [
                ProblemParagraphMapping(id=uuid.uuid1(), document_id=document_id, problem_id=problem_model.id,
                                        paragraph_id=paragraph.id,
                                        dataset_id=dataset_id) for
                problem_model in problem_model_list]
            return {'paragraph': paragraph,
                    'problem_model_list': [problem_model for problem_model in problem_model_list if
                                           not list(exists_problem_list).__contains__(problem_model)],
                    'problem_paragraph_mapping_list': problem_paragraph_mapping_list}

        @staticmethod
        def or_get(exists_problem_list, content, dataset_id):
            exists = [row for row in exists_problem_list if row.content == content]
            if len(exists) > 0:
                return exists[0]
            else:
                return Problem(id=uuid.uuid1(), content=content, dataset_id=dataset_id)

        @staticmethod
        def get_request_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='document_id', in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description="Documentsid")
                    ]

    class Query(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "The knowledge baseid"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "Documentsid"))

        title = serializers.CharField(required=False, error_messages=ErrMessage.char(
            "Title of paragraph"))

        content = serializers.CharField(required=False)

        def get_query_set(self):
            query_set = QuerySet(model=Paragraph)
            query_set = query_set.filter(
                **{'dataset_id': self.data.get('dataset_id'), 'document_id': self.data.get("document_id")})
            if 'title' in self.data:
                query_set = query_set.filter(
                    **{'title__icontains': self.data.get('title')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__icontains': self.data.get('content')})
            return query_set

        def list(self):
            return list(map(lambda row: ParagraphSerializer(row).data, self.get_query_set()))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return page_search(current_page, page_size, query_set, lambda row: ParagraphSerializer(row).data)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Documentsid'),
                    openapi.Parameter(name='title',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='The title'),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='The content')
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                          'document_id', 'title',
                          'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="Contents of paragraph",
                                              description="Contents of paragraph", default='Contents of paragraph'),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title="The title",
                                            description="The title", default="xxxThe description"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="The number of fate", description="The number of fate",
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="The number of praise.",
                                               description="The number of praise.", default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="The number of steps.",
                                                  description="The number of steps.", default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="The knowledge baseid",
                                                 description="The knowledge baseid", default='xxx'),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title="Documentsid",
                                                  description="Documentsid", default='xxx'),
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
