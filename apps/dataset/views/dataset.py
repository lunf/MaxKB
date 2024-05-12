# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： dataset.py
    @date：2023/9/21 15:52
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants, Permission, Group, Operate, \
    ViewPermission, RoleConstants
from common.response import result
from common.response.result import get_page_request_params, get_page_api_response, get_api_response
from common.swagger_api.common_api import CommonApi
from dataset.serializers.dataset_serializers import DataSetSerializers


class Dataset(APIView):
    authentication_classes = [TokenAuth]

    class SyncWeb(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="synchronizedWebSite Knowledge Base",
                             operation_id="synchronizedWebSite Knowledge Base",
                             manual_parameters=DataSetSerializers.SyncWeb.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base"])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('dataset_id'))],
            compare=CompareConstants.AND), PermissionConstants.DATASET_EDIT,
            compare=CompareConstants.AND)
        def put(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.SyncWeb(
                data={'sync_type': request.query_params.get('sync_type'), 'id': dataset_id,
                      'user_id': str(request.user.id)}).sync())

    class CreateWebDataset(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="CreatedwebSite Knowledge Base",
                             operation_id="CreatedwebSite Knowledge Base",
                             request_body=DataSetSerializers.Create.CreateWebSerializers.get_request_body_api(),
                             responses=get_api_response(
                                 DataSetSerializers.Create.CreateWebSerializers.get_response_body_api()),
                             tags=["The knowledge base"]
                             )
        @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
        def post(self, request: Request):
            return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save_web(request.data))

    class Application(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Available Information Base Applications List",
                             operation_id="Available Information Base Applications List",
                             manual_parameters=DataSetSerializers.Application.get_request_params_api(),
                             responses=result.get_api_array_response(
                                 DataSetSerializers.Application.get_response_body_api()),
                             tags=["The knowledge base"])
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(
                data={'id': dataset_id, 'user_id': str(request.user.id)}).list_application())

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="Get a Knowledge Base List",
                         operation_id="Get a Knowledge Base List",
                         manual_parameters=DataSetSerializers.Query.get_request_params_api(),
                         responses=result.get_api_array_response(DataSetSerializers.Query.get_response_body_api()),
                         tags=["The knowledge base"])
    @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        d = DataSetSerializers.Query(data={**request.query_params, 'user_id': str(request.user.id)})
        d.is_valid()
        return result.success(d.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Creating a Knowledge Base",
                         operation_id="Creating a Knowledge Base",
                         request_body=DataSetSerializers.Create.get_request_body_api(),
                         responses=get_api_response(DataSetSerializers.Create.get_response_body_api()),
                         tags=["The knowledge base"]
                         )
    @has_permissions(PermissionConstants.DATASET_CREATE, compare=CompareConstants.AND)
    def post(self, request: Request):
        return result.success(DataSetSerializers.Create(data={'user_id': request.user.id}).save(request.data))

    class HitTest(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="Test list of fate", operation_id="Test list of fate",
                             manual_parameters=CommonApi.HitTestApi.get_request_params_api(),
                             responses=result.get_api_array_response(CommonApi.HitTestApi.get_response_body_api()),
                             tags=["The knowledge base"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.HitTest(data={'id': dataset_id, 'user_id': request.user.id,
                                                 "query_text": request.query_params.get("query_text"),
                                                 "top_number": request.query_params.get("top_number"),
                                                 'similarity': request.query_params.get('similarity'),
                                                 'search_mode': request.query_params.get('search_mode')}).hit_test(
                ))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods="DELETE", detail=False)
        @swagger_auto_schema(operation_summary="Remove the Knowledge Base", operation_id="Remove the Knowledge Base",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')),
                         lambda r, k: Permission(group=Group.DATASET, operate=Operate.DELETE,
                                                 dynamic_tag=k.get('dataset_id')), compare=CompareConstants.AND)
        def delete(self, request: Request, dataset_id: str):
            operate = DataSetSerializers.Operate(data={'id': dataset_id})
            return result.success(operate.delete())

        @action(methods="GET", detail=False)
        @swagger_auto_schema(operation_summary="Information based on the knowledge base.id", operation_id="Information based on the knowledge base.id",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base"])
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.USE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def get(self, request: Request, dataset_id: str):
            return result.success(DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).one(
                user_id=request.user.id))

        @action(methods="PUT", detail=False)
        @swagger_auto_schema(operation_summary="Modification of Knowledge Base Information", operation_id="Modification of Knowledge Base Information",
                             manual_parameters=DataSetSerializers.Operate.get_request_params_api(),
                             request_body=DataSetSerializers.Operate.get_request_body_api(),
                             responses=get_api_response(DataSetSerializers.Operate.get_response_body_api()),
                             tags=["The knowledge base"]
                             )
        @has_permissions(lambda r, keywords: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                                        dynamic_tag=keywords.get('dataset_id')))
        def put(self, request: Request, dataset_id: str):
            return result.success(
                DataSetSerializers.Operate(data={'id': dataset_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                     user_id=request.user.id))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get the Knowledge Base Page List",
                             operation_id="Get the Knowledge Base Page List",
                             manual_parameters=get_page_request_params(
                                 DataSetSerializers.Query.get_request_params_api()),
                             responses=get_page_api_response(DataSetSerializers.Query.get_response_body_api()),
                             tags=["The knowledge base"]
                             )
        @has_permissions(PermissionConstants.DATASET_READ, compare=CompareConstants.AND)
        def get(self, request: Request, current_page, page_size):
            d = DataSetSerializers.Query(
                data={'name': request.query_params.get('name', None), 'desc': request.query_params.get("desc", None),
                      'user_id': str(request.user.id)})
            d.is_valid()
            return result.success(d.page(current_page, page_size))
