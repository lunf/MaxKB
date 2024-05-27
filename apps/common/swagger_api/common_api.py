# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: common.py
    @date:2023/12/25 16:17
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class CommonApi:
    class HitTestApi(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [
                    openapi.Parameter(name='query_text',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='The question text.'),
                    openapi.Parameter(name='top_number',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_NUMBER,
                                      default=10,
                                      required=True,
                                      description='topN'),
                    openapi.Parameter(name='similarity',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_NUMBER,
                                      default=0.6,
                                      required=True,
                                      description='Related'),
                    openapi.Parameter(name='search_mode',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      default="embedding",
                                      required=True,
                                      description='The search model.embedding|keywords|blend'
                                      )
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                          'document_id', 'title',
                          'similarity', 'comprehensive_score',
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
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title="Relevantity score.",
                                                 description="Relevantity score.", default=True),
                    'comprehensive_score': openapi.Schema(type=openapi.TYPE_NUMBER, title="Comprehensive score.,Used for ordering",
                                                          description="Comprehensive score.,Used for ordering", default=True),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                                  description="Change time.",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                                  description="Creating time.",
                                                  default="1970-01-01 00:00:00"
                                                  ),

                }
            )
