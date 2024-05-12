# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： paragraph_serializers.py
    @date：2023/10/16 15:51
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, CompareConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.common_serializers import BatchSerializer
from dataset.serializers.paragraph_serializers import ParagraphSerializers


class Paragraph(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="List of paragraphs",
                         operation_id="List of paragraphs",
                         manual_parameters=ParagraphSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ParagraphSerializers.Query.get_response_body_api()),
                         tags=["The knowledge base/Documents/Paragraphs"]
                         )
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str, document_id: str):
        q = ParagraphSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                  'document_id': document_id})
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Creating paragraphs",
                         operation_id="Creating paragraphs",
                         manual_parameters=ParagraphSerializers.Create.get_request_params_api(),
                         request_body=ParagraphSerializers.Create.get_request_body_api(),
                         responses=result.get_api_response(ParagraphSerializers.Query.get_response_body_api()),
                         tags=["The knowledge base/Documents/Paragraphs"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str, document_id: str):
        return result.success(
            ParagraphSerializers.Create(data={'dataset_id': dataset_id, 'document_id': document_id}).save(request.data))

    class Problem(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Add Related Problems",
                             operation_id="Adding paragraph related issues",
                             manual_parameters=ParagraphSerializers.Problem.get_request_params_api(),
                             request_body=ParagraphSerializers.Problem.get_request_body_api(),
                             responses=result.get_api_response(ParagraphSerializers.Problem.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def post(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
            return result.success(ParagraphSerializers.Problem(
                data={"dataset_id": dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id}).save(
                request.data, with_valid=True))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get the question list of paragraphs",
                             operation_id="Get the question list of paragraphs",
                             manual_parameters=ParagraphSerializers.Problem.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 ParagraphSerializers.Problem.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
            return result.success(ParagraphSerializers.Problem(
                data={"dataset_id": dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id}).list(
                with_valid=True))

        class UnAssociation(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary="Removing Relationship Problems",
                                 operation_id="Removing Relationship Problems",
                                 manual_parameters=ParagraphSerializers.Association.get_request_params_api(),
                                 responses=result.get_default_response(),
                                 tags=["The knowledge base/Documents/Paragraphs"])
            @has_permissions(
                lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                        dynamic_tag=k.get('dataset_id')))
            def put(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str, problem_id: str):
                return result.success(ParagraphSerializers.Association(
                    data={'dataset_id': dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id,
                          'problem_id': problem_id}).un_association())

        class Association(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary="Related issues",
                                 operation_id="Related issues",
                                 manual_parameters=ParagraphSerializers.Association.get_request_params_api(),
                                 responses=result.get_default_response(),
                                 tags=["The knowledge base/Documents/Paragraphs"])
            @has_permissions(
                lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                        dynamic_tag=k.get('dataset_id')))
            def put(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str, problem_id: str):
                return result.success(ParagraphSerializers.Association(
                    data={'dataset_id': dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id,
                          'problem_id': problem_id}).association())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['UPDATE'], detail=False)
        @swagger_auto_schema(operation_summary="Modification of paragraph data",
                             operation_id="Modification of paragraph data",
                             manual_parameters=ParagraphSerializers.Operate.get_request_params_api(),
                             request_body=ParagraphSerializers.Operate.get_request_body_api(),
                             responses=result.get_api_response(ParagraphSerializers.Operate.get_response_body_api())
            , tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={"paragraph_id": paragraph_id, 'dataset_id': dataset_id, 'document_id': document_id})
            o.is_valid(raise_exception=True)
            return result.success(o.edit(request.data))

        @action(methods=['UPDATE'], detail=False)
        @swagger_auto_schema(operation_summary="Get detailed paragraphs.",
                             operation_id="Get detailed paragraphs.",
                             manual_parameters=ParagraphSerializers.Operate.get_request_params_api(),
                             responses=result.get_api_response(ParagraphSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={"dataset_id": dataset_id, 'document_id': document_id, "paragraph_id": paragraph_id})
            o.is_valid(raise_exception=True)
            return result.success(o.one())

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Delete the paragraph.",
                             operation_id="Delete the paragraph.",
                             manual_parameters=ParagraphSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
            o = ParagraphSerializers.Operate(
                data={"dataset_id": dataset_id, 'document_id': document_id, "paragraph_id": paragraph_id})
            o.is_valid(raise_exception=True)
            return result.success(o.delete())

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="批量删除段落",
                             operation_id="批量删除段落",
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=ParagraphSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档/段落"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str):
            return result.success(ParagraphSerializers.Batch(
                data={"dataset_id": dataset_id, 'document_id': document_id}).batch_delete(request.data))

    class BatchMigrate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="批量迁移段落",
                             operation_id="批量迁移段落",
                             manual_parameters=ParagraphSerializers.Migrate.get_request_params_api(),
                             request_body=ParagraphSerializers.Migrate.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=["知识库/文档/段落"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')),
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('target_dataset_id')),
            compare=CompareConstants.AND
        )
        def put(self, request: Request, dataset_id: str, target_dataset_id: str, document_id: str, target_document_id):
            return result.success(
                ParagraphSerializers.Migrate(
                    data={'dataset_id': dataset_id, 'target_dataset_id': target_dataset_id,
                          'document_id': document_id,
                          'target_document_id': target_document_id,
                          'paragraph_id_list': request.data}).migrate())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Section page to get paragraph list",
                             operation_id="Section page to get paragraph list",
                             manual_parameters=result.get_page_request_params(
                                 ParagraphSerializers.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ParagraphSerializers.Query.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str, current_page, page_size):
            d = ParagraphSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'document_id': document_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
