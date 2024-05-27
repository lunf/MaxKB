# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: problem_api.py
    @date:2024/3/11 10:49
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ProblemApi(ApiMixin):
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

    class BatchOperate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                title="The problemidList of",
                description="The problemidList of",
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING)
            )

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The problemid')]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['content'],
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="The content of the question",
                                              description="The content of the question"),

                }
            )

    class Paragraph(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return ProblemApi.Operate.get_request_params_api()

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['content'],
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title="Part of content.",
                                              description="Part of content."),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title="Section title",
                                            description="Section title"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is Available", description="Is Available"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="Number of fate.", description="Number of fate."),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                  description="Change time.",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                  description="Creating time.",
                                                  default="1970-01-01 00:00:00"
                                                  ),
                }
            )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid'),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='The problem')]

    class BatchCreate(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY,
                                  items=ProblemApi.Create.get_request_body_api())

        @staticmethod
        def get_request_params_api():
            return ProblemApi.Create.get_request_params_api()

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_STRING, description="The question text.")

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The knowledge baseid')]
