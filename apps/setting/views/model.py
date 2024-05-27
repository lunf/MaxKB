# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: model.py
    @date:2023/11/2 13:55
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from setting.serializers.provider_serializers import ProviderSerializer, ModelSerializer
from setting.swagger_api.provide_api import ProvideApi, ModelCreateApi, ModelQueryApi, ModelEditApi


class Model(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Creating a model.",
                         operation_id="Creating a model.",
                         request_body=ModelCreateApi.get_request_body_api()
        , tags=["The model"])
    @has_permissions(PermissionConstants.MODEL_CREATE)
    def post(self, request: Request):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
                                                                                                  with_valid=True))

    @action(methods=['PUT'], detail=False)
    @swagger_auto_schema(operation_summary="Download the model.,Try only withOllamaPlatform",
                         operation_id="Download the model.,Try only withOllamaPlatform",
                         request_body=ModelCreateApi.get_request_body_api()
        , tags=["The model"])
    @has_permissions(PermissionConstants.MODEL_CREATE)
    def put(self, request: Request):
        return result.success(
            ModelSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id,
                                                                                                  with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="Get a model list.",
                         operation_id="Get a model list.",
                         manual_parameters=ModelQueryApi.get_request_params_api()
        , tags=["The model"])
    @has_permissions(PermissionConstants.MODEL_READ)
    def get(self, request: Request):
        return result.success(
            ModelSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 'user_id': request.user.id}).list(
                with_valid=True))

    class ModelMeta(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="The model of query.metaInformation,The interface does not carry certification information.",
                             operation_id="The model of query.metaInformation,The interface does not carry certification information.",
                             tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one_meta(with_valid=True))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Modifying the model",
                             operation_id="Modifying the model",
                             request_body=ModelEditApi.get_request_body_api()
            , tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_CREATE)
        def put(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).edit(request.data,
                                                                                                str(request.user.id)))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Remove the model.",
                             operation_id="Remove the model.",
                             responses=result.get_default_response()
            , tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_DELETE)
        def delete(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).delete())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Detailed Model Information",
                             operation_id="Detailed Model Information",
                             tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request, model_id: str):
            return result.success(
                ModelSerializer.Operate(data={'id': model_id, 'user_id': request.user.id}).one(with_valid=True))


class Provide(APIView):
    authentication_classes = [TokenAuth]

    class Exec(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Calling the Supplier Function,Obtaining Form Data",
                             operation_id="Calling the Supplier Function,Obtaining Form Data",
                             manual_parameters=ProvideApi.get_request_params_api(),
                             request_body=ProvideApi.get_request_body_api()
            , tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_READ)
        def post(self, request: Request, provider: str, method: str):
            return result.success(
                ProviderSerializer(data={'provider': provider, 'method': method}).exec(request.data, with_valid=True))

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="Obtaining Model Supplier Data",
                         operation_id="Get a Model Supplier List"
        , tags=["The model"])
    @has_permissions(PermissionConstants.MODEL_READ)
    def get(self, request: Request):
        return result.success(
            [ModelProvideConstants[key].value.get_model_provide_info().to_dict() for key in
             ModelProvideConstants.__members__])

    class ModelTypeList(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a Model Type List",
                             operation_id="Get a Model Type List",
                             manual_parameters=ProvideApi.ModelTypeList.get_request_params_api(),
                             responses=result.get_api_array_response(ProvideApi.ModelTypeList.get_response_body_api())
            , tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            return result.success(ModelProvideConstants[provider].value.get_model_type_list())

    class ModelList(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a model list.",
                             operation_id="Get a model to create a form",
                             manual_parameters=ProvideApi.ModelList.get_request_params_api(),
                             responses=result.get_api_array_response(ProvideApi.ModelList.get_response_body_api())
            , tags=["The model"]
                             )
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')

            return result.success(
                ModelProvideConstants[provider].value.get_model_list(
                    model_type))

    class ModelForm(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a model to create a form",
                             operation_id="Get a model to create a form",
                             manual_parameters=ProvideApi.ModelForm.get_request_params_api(),
                             tags=["The model"])
        @has_permissions(PermissionConstants.MODEL_READ)
        def get(self, request: Request):
            provider = request.query_params.get('provider')
            model_type = request.query_params.get('model_type')
            model_name = request.query_params.get('model_name')
            return result.success(
                ModelProvideConstants[provider].value.get_model_credential(model_type, model_name).to_form_list())
