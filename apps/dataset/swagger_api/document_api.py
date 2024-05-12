# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： document_api.py
    @date：2024/4/28 13:56
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class DocumentApi(ApiMixin):
    class BatchEditHitHandlingApi(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                               title="primary key id list",
                                               description="primary key id list"),
                    'hit_handling_method': openapi.Schema(type=openapi.TYPE_STRING, title="hit handling method",
                                                        description="directly_return|optimization"),
                    'directly_return_similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title="Directly return similarity")
                }
            )
