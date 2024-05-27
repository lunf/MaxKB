# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: application_statistics_api.py
    @date:2024/3/27 15:09
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ApplicationStatisticsApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='start_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='The Time Begins'),
                openapi.Parameter(name='end_time',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='The time ends.'),
                ]

    class ChatRecordAggregate(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['star_num', 'trample_num', 'tokens_num', 'chat_record_count'],
                properties={
                    'star_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="The number of praise.",
                                               description="The number of praise."),

                    'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="The number of steps.", description="The number of steps."),
                    'tokens_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="tokenNumber of use",
                                                 description="tokenNumber of use"),
                    'chat_record_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="Number of conversations",
                                                        description="Number of conversations"),
                    'customer_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="Number of customers",
                                                   description="Number of customers"),
                    'customer_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="Added number of customers.",
                                                           description="Added number of customers."),
                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title="Date of",
                                          description="Date of,The field only exists when the trend is investigated."),
                }
            )

    class CustomerCountTrend(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="Added number", description="Added number"),

                    'day': openapi.Schema(type=openapi.TYPE_STRING,
                                          title="time",
                                          description="time"),
                }
            )

    class CustomerCount(ApiMixin):
        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['added_count'],
                properties={
                    'today_added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="A new number today.",
                                                        description="A new number today."),
                    'added_count': openapi.Schema(type=openapi.TYPE_NUMBER, title="Added number", description="Added number"),

                }
            )
