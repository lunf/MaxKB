# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： chat_views.py
    @date：2023/11/14 9:53
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from application.serializers.chat_message_serializers import ChatMessageSerializer
from application.serializers.chat_serializers import ChatSerializers, ChatRecordSerializer
from application.swagger_api.chat_api import ChatApi, VoteApi, ChatRecordApi, ImproveApi, ChatRecordImproveApi
from common.auth import TokenAuth, has_permissions
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Permission, Group, Operate, \
    RoleConstants, ViewPermission, CompareConstants
from common.response import result
from common.util.common import query_params_to_single_dict


class ChatView(APIView):
    authentication_classes = [TokenAuth]

    class Export(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Exporting Dialogue",
                             operation_id="Exporting Dialogue",
                             manual_parameters=ChatApi.get_request_params_api(),
                             tags=["Applications/Dialogues"]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str):
            return ChatSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                      'user_id': request.user.id}).export()

    class Open(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a meeting.id,According to Applicationid",
                             operation_id="Get a meeting.id,According to Applicationid",
                             manual_parameters=ChatApi.OpenChat.get_request_params_api(),
                             tags=["Applications/Meeting"])
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_ACCESS_TOKEN,
                            RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))],
                           compare=CompareConstants.AND)
        )
        def get(self, request: Request, application_id: str):
            return result.success(ChatSerializers.OpenChat(
                data={'user_id': request.user.id, 'application_id': application_id}).open())

    class OpenTemp(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Get a meeting.id(according to the model.id,List of Knowledge Base,There are several sessions.)",
                             operation_id="Get a meeting.id",
                             request_body=ChatApi.OpenTempChat.get_request_body_api(),
                             tags=["Applications/Meeting"])
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def post(self, request: Request):
            return result.success(ChatSerializers.OpenTempChat(
                data={**request.data, 'user_id': request.user.id}).open())

    class Message(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary="Dialogue",
                             operation_id="Dialogue",
                             request_body=ChatApi.get_request_body_api(),
                             tags=["Applications/Meeting"])
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                            RoleConstants.APPLICATION_ACCESS_TOKEN],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def post(self, request: Request, chat_id: str):
            return ChatMessageSerializer(data={'chat_id': chat_id, 'message': request.data.get('message'),
                                               're_chat': (request.data.get(
                                                   're_chat') if 're_chat' in request.data else False),
                                               'stream': (request.data.get(
                                                   'stream') if 'stream' in request.data else True),
                                               'application_id': (request.auth.keywords.get(
                                                   'application_id') if request.auth.client_type == AuthenticationType.APPLICATION_ACCESS_TOKEN.value else None),
                                               'client_id': request.auth.client_id,
                                               'client_type': request.auth.client_type}).chat()

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="Get a dialogue list.",
                         operation_id="Get a dialogue list.",
                         manual_parameters=ChatApi.get_request_params_api(),
                         responses=result.get_api_array_response(ChatApi.get_response_body_api()),
                         tags=["Applications/Dialogues"]
                         )
    @has_permissions(
        ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                       [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                       dynamic_tag=keywords.get('application_id'))])
    )
    def get(self, request: Request, application_id: str):
        return result.success(ChatSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                  'user_id': request.user.id}).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Delete the dialogue.",
                             operation_id="Delete the dialogue.",
                             tags=["Applications/Dialogues"])
        @has_permissions(ViewPermission(
            [RoleConstants.ADMIN, RoleConstants.USER],
            [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.MANAGE,
                                            dynamic_tag=keywords.get('application_id'))],
            compare=CompareConstants.AND),
            compare=CompareConstants.AND)
        def delete(self, request: Request, application_id: str, chat_id: str):
            return result.success(
                ChatSerializers.Operate(
                    data={'application_id': application_id, 'user_id': request.user.id,
                          'chat_id': chat_id}).delete())

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Page to Get Dialogue List",
                             operation_id="Page to Get Dialogue List",
                             manual_parameters=result.get_page_request_params(ChatApi.get_request_params_api()),
                             responses=result.get_page_api_response(ChatApi.get_response_body_api()),
                             tags=["Applications/Dialogues"]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str, current_page: int, page_size: int):
            return result.success(ChatSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'application_id': application_id,
                      'user_id': request.user.id}).page(current_page=current_page,
                                                        page_size=page_size))

    class ChatRecord(APIView):
        authentication_classes = [TokenAuth]

        class Operate(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary="Get the dialogue record details",
                                 operation_id="Get the dialogue record details",
                                 manual_parameters=ChatRecordApi.get_request_params_api(),
                                 responses=result.get_api_array_response(ChatRecordApi.get_response_body_api()),
                                 tags=["Applications/Dialogues"]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                                RoleConstants.APPLICATION_ACCESS_TOKEN],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.Operate(
                    data={'application_id': application_id,
                          'chat_id': chat_id,
                          'chat_record_id': chat_record_id}).one(request.auth.current_role))

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="Get a dialogue record list",
                             operation_id="Get a dialogue record list",
                             manual_parameters=ChatRecordApi.get_request_params_api(),
                             responses=result.get_api_array_response(ChatRecordApi.get_response_body_api()),
                             tags=["Applications/Dialogues"]
                             )
        @has_permissions(
            ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                           [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                           dynamic_tag=keywords.get('application_id'))])
        )
        def get(self, request: Request, application_id: str, chat_id: str):
            return result.success(ChatRecordSerializer.Query(
                data={'application_id': application_id,
                      'chat_id': chat_id}).list())

        class Page(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary="Get a dialogue record list",
                                 operation_id="Get a dialogue record list",
                                 manual_parameters=result.get_page_request_params(
                                     ChatRecordApi.get_request_params_api()),
                                 responses=result.get_page_api_response(ChatRecordApi.get_response_body_api()),
                                 tags=["Applications/Dialogues"]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            def get(self, request: Request, application_id: str, chat_id: str, current_page: int, page_size: int):
                return result.success(ChatRecordSerializer.Query(
                    data={'application_id': application_id,
                          'chat_id': chat_id}).page(current_page, page_size))

        class Vote(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary="The praise.,step down.",
                                 operation_id="The praise.,step down.",
                                 manual_parameters=VoteApi.get_request_params_api(),
                                 request_body=VoteApi.get_request_body_api(),
                                 responses=result.get_default_response(),
                                 tags=["Applications/Meeting"]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER, RoleConstants.APPLICATION_KEY,
                                RoleConstants.APPLICATION_ACCESS_TOKEN],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))])
            )
            def put(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.Vote(
                    data={'vote_status': request.data.get('vote_status'), 'chat_id': chat_id,
                          'chat_record_id': chat_record_id}).vote())

        class ChatRecordImprove(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['GET'], detail=False)
            @swagger_auto_schema(operation_summary="Get information on the item list.",
                                 operation_id="Get information on the item list.",
                                 manual_parameters=ChatRecordImproveApi.get_request_params_api(),
                                 responses=result.get_api_response(ChatRecordImproveApi.get_response_body_api()),
                                 tags=["Applications/Dialogues/Signed"]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))]
                               ))
            def get(self, request: Request, application_id: str, chat_id: str, chat_record_id: str):
                return result.success(ChatRecordSerializer.ChatRecordImprove(
                    data={'chat_id': chat_id, 'chat_record_id': chat_record_id}).get())

        class Improve(APIView):
            authentication_classes = [TokenAuth]

            @action(methods=['PUT'], detail=False)
            @swagger_auto_schema(operation_summary="Signed",
                                 operation_id="Signed",
                                 manual_parameters=ImproveApi.get_request_params_api(),
                                 request_body=ImproveApi.get_request_body_api(),
                                 responses=result.get_api_response(ChatRecordApi.get_response_body_api()),
                                 tags=["Applications/Dialogues/Signed"]
                                 )
            @has_permissions(
                ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                               [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                               dynamic_tag=keywords.get('application_id'))],

                               ), ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                 [lambda r, keywords: Permission(group=Group.DATASET,
                                                                                 operate=Operate.MANAGE,
                                                                                 dynamic_tag=keywords.get(
                                                                                     'dataset_id'))],
                                                 compare=CompareConstants.AND
                                                 ), compare=CompareConstants.AND)
            def put(self, request: Request, application_id: str, chat_id: str, chat_record_id: str, dataset_id: str,
                    document_id: str):
                return result.success(ChatRecordSerializer.Improve(
                    data={'chat_id': chat_id, 'chat_record_id': chat_record_id,
                          'dataset_id': dataset_id, 'document_id': document_id}).improve(request.data))

            class Operate(APIView):
                authentication_classes = [TokenAuth]

                @action(methods=['DELETE'], detail=False)
                @swagger_auto_schema(operation_summary="Signed",
                                     operation_id="Signed",
                                     manual_parameters=ImproveApi.get_request_params_api(),
                                     responses=result.get_api_response(ChatRecordApi.get_response_body_api()),
                                     tags=["Applications/Dialogues/Signed"]
                                     )
                @has_permissions(
                    ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                   [lambda r, keywords: Permission(group=Group.APPLICATION, operate=Operate.USE,
                                                                   dynamic_tag=keywords.get('application_id'))],

                                   ), ViewPermission([RoleConstants.ADMIN, RoleConstants.USER],
                                                     [lambda r, keywords: Permission(group=Group.DATASET,
                                                                                     operate=Operate.MANAGE,
                                                                                     dynamic_tag=keywords.get(
                                                                                         'dataset_id'))],
                                                     compare=CompareConstants.AND
                                                     ), compare=CompareConstants.AND)
                def delete(self, request: Request, application_id: str, chat_id: str, chat_record_id: str,
                           dataset_id: str,
                           document_id: str, paragraph_id: str):
                    return result.success(ChatRecordSerializer.Improve.Operate(
                        data={'chat_id': chat_id, 'chat_record_id': chat_record_id,
                              'dataset_id': dataset_id, 'document_id': document_id,
                              'paragraph_id': paragraph_id}).delete())
