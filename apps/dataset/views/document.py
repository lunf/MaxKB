# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： document.py
    @date：2023/9/22 11:32
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate, CompareConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.common_serializers import BatchSerializer
from dataset.serializers.document_serializers import DocumentSerializers, DocumentWebInstanceSerializer
from dataset.swagger_api.document_api import DocumentApi


class WebDocument(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="CreatedWebSite Documents",
                         operation_id="CreatedWebSite Documents",
                         request_body=DocumentWebInstanceSerializer.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=["The knowledge base/Documents"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save_web(request.data, with_valid=True))


class Document(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Creating Documents",
                         operation_id="Creating Documents",
                         request_body=DocumentSerializers.Create.get_request_body_api(),
                         manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                         tags=["The knowledge base/Documents"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="List of documents",
                         operation_id="List of documents",
                         manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                         responses=result.get_api_response(DocumentSerializers.Query.get_response_body_api()),
                         tags=["The knowledge base/Documents"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        d = DocumentSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
        d.is_valid(raise_exception=True)
        return result.success(d.list())

    class BatchEditHitHandling(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Modification of the method of handling documents.",
                             operation_id="Modification of the method of handling documents.",
                             request_body=
                             DocumentApi.BatchEditHitHandlingApi.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_edit_hit_handling(request.data))

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Create a lot of documents",
                             operation_id="Create a lot of documents",
                             request_body=
                             DocumentSerializers.Batch.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DocumentSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def post(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_save(request.data))

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Multiple synchronous documents",
                             operation_id="Multiple synchronous documents",
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_sync(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Remove the document.",
                             operation_id="Remove the document.",
                             request_body=
                             BatchSerializer.get_request_body_api(),
                             manual_parameters=DocumentSerializers.Create.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            return result.success(DocumentSerializers.Batch(data={'dataset_id': dataset_id}).batch_delete(request.data))

    class Refresh(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Update the document to the quantum library.",
                             operation_id="Update the document to the quantum library.",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).refresh(
                ))

    class Migrate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Mass Migration Documents",
                             operation_id="Mass Migration Documents",
                             manual_parameters=DocumentSerializers.Migrate.get_request_params_api(),
                             request_body=DocumentSerializers.Migrate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base/Documents"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')),
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('target_dataset_id')),
            compare=CompareConstants.AND
        )
        def put(self, request: Request, dataset_id: str, target_dataset_id: str):
            return result.success(
                DocumentSerializers.Migrate(
                    data={'dataset_id': dataset_id, 'target_dataset_id': target_dataset_id,
                          'document_id_list': request.data}).migrate(

                ))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get the document details.",
                             operation_id="Get the document details.",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.one())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Modifying the document.",
                             operation_id="Modifying the document.",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             request_body=DocumentSerializers.Operate.get_request_body_api(),
                             responses=result.get_api_response(DocumentSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base/Documents"]
                             )
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str):
            return result.success(
                DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id}).edit(
                    request.data,
                    with_valid=True))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Delete the document.",
                             operation_id="Delete the document.",
                             manual_parameters=DocumentSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str):
            operate = DocumentSerializers.Operate(data={'document_id': document_id, 'dataset_id': dataset_id})
            operate.is_valid(raise_exception=True)
            return result.success(operate.delete())

    class SplitPattern(APIView):
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a section identification list.",
                             operation_id="Get a section identification list.",
                             tags=["The knowledge base/Documents"],
                             security=[])
        def get(self, request: Request):
            return result.success(DocumentSerializers.SplitPattern.list())

    class Split(APIView):
        parser_classes = [MultiPartParser]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Section of documents.",
                             operation_id="Section of documents.",
                             manual_parameters=DocumentSerializers.Split.get_request_params_api(),
                             tags=["The knowledge base/Documents"],
                             security=[])
        def post(self, request: Request):
            split_data = {'file': request.FILES.getlist('file')}
            request_data = request.data
            if 'patterns' in request.data and request.data.get('patterns') is not None and len(
                    request.data.get('patterns')) > 0:
                split_data.__setitem__('patterns', request_data.getlist('patterns'))
            if 'limit' in request.data:
                split_data.__setitem__('limit', request_data.get('limit'))
            if 'with_filter' in request.data:
                split_data.__setitem__('with_filter', request_data.get('with_filter'))
            ds = DocumentSerializers.Split(
                data=split_data)
            ds.is_valid(raise_exception=True)
            return result.success(ds.parse())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get the Knowledge Base Page List",
                             operation_id="Get the Knowledge Base Page List",
                             manual_parameters=DocumentSerializers.Query.get_request_params_api(),
                             responses=result.get_page_api_response(DocumentSerializers.Query.get_response_body_api()),
                             tags=["The knowledge base/Documents"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = DocumentSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
