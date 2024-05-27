# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: system_setting.py
    @date:2024/3/19 16:01
    @desc:
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from setting.serializers.system_setting import SystemSettingSerializer
from setting.swagger_api.system_setting import SystemSettingEmailApi


class SystemSetting(APIView):
    class Email(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Create or modify mailbox settings",
                             operation_id="Create or modify mailbox settings",
                             request_body=SystemSettingEmailApi.get_request_body_api(), tags=["Postbox setup."],
                             responses=result.get_api_response(SystemSettingEmailApi.get_response_body_api()))
        @has_permissions(RoleConstants.ADMIN)
        def put(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.Create(
                    data=request.data).update_or_save())

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Testing the mailbox.",
                             operation_id="Testing the mailbox.",
                             request_body=SystemSettingEmailApi.get_request_body_api(),
                             responses=result.get_default_response(),
                             tags=["Postbox setup."])
        @has_permissions(RoleConstants.ADMIN)
        def post(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.Create(
                    data=request.data).is_valid())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get the mailbox setting.",
                             operation_id="Get the mailbox setting.",
                             responses=result.get_api_response(SystemSettingEmailApi.get_response_body_api()),
                             tags=["Postbox setup."])
        @has_permissions(RoleConstants.ADMIN)
        def get(self, request: Request):
            return result.success(
                SystemSettingSerializer.EmailSerializer.one())
