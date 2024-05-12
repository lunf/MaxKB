# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： problem.py
    @date：2023/10/23 13:54
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.problem_serializers import ProblemSerializers
from dataset.swagger_api.problem_api import ProblemApi


class Problem(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="List of Questions",
                         operation_id="List of Questions",
                         manual_parameters=ProblemApi.Query.get_request_params_api(),
                         responses=result.get_api_array_response(ProblemApi.get_response_body_api()),
                         tags=["The knowledge base/Documents/Paragraphs/The problem"]
                         )
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str):
        q = ProblemSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Creating problems.",
                         operation_id="Creating problems.",
                         manual_parameters=ProblemApi.BatchCreate.get_request_params_api(),
                         request_body=ProblemApi.BatchCreate.get_request_body_api(),
                         responses=result.get_api_response(ProblemApi.Query.get_response_body_api()),
                         tags=["The knowledge base/Documents/Paragraphs/The problem"])
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str):
        return result.success(
            ProblemSerializers.Create(
                data={'dataset_id': dataset_id, 'problem_list': request.data}).batch())

    class Paragraph(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="List of related paragraphs.",
                             operation_id="List of related paragraphs.",
                             manual_parameters=ProblemApi.Paragraph.get_request_params_api(),
                             responses=result.get_api_array_response(ProblemApi.Paragraph.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs/The problem"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).list_paragraph())

    class OperateBatch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Mass removal of problems.",
                             operation_id="Mass removal of problems.",
                             request_body=
                             ProblemApi.BatchOperate.get_request_body_api(),
                             manual_parameters=ProblemApi.BatchOperate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents/Paragraphs/The problem"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str):
            return result.success(
                ProblemSerializers.BatchOperate(data={'dataset_id': dataset_id}).delete(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary="Delete the problem.",
                             operation_id="Delete the problem.",
                             manual_parameters=ProblemApi.Operate.get_request_params_api(),
                             responses=result.get_default_response(),
                             tags=["The knowledge base/Documents/Paragraphs/The problem"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).delete())

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary="Modifying the problem",
                             operation_id="Modifying the problem",
                             manual_parameters=ProblemApi.Operate.get_request_params_api(),
                             request_body=ProblemApi.Operate.get_request_body_api(),
                             responses=result.get_api_response(ProblemApi.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs/The problem"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, problem_id: str):
            return result.success(ProblemSerializers.Operate(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'problem_id': problem_id}).edit(request.data))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary="List of issues to page.",
                             operation_id="List of issues to page.",
                             manual_parameters=result.get_page_request_params(
                                 ProblemApi.Query.get_request_params_api()),
                             responses=result.get_page_api_response(ProblemApi.get_response_body_api()),
                             tags=["The knowledge base/Documents/Paragraphs/The problem"])
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, current_page, page_size):
            d = ProblemSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size))
