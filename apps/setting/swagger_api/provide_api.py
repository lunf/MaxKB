# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: provide_api.py
    @date:2023/11/2 14:25
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ModelQueryApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='name',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='Name of model'),
                openapi.Parameter(name='model_type', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='Type of Model'),
                openapi.Parameter(name='model_name', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='The basic model name.'),
                openapi.Parameter(name='provider',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='Name of supply')
                ]


class ModelEditApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="The parameters required for the call function",
                              description="The parameters required for the call function",
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title="Name of model",
                                                         description="Name of model"),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="Suppliers",
                                                               description="Suppliers"),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="Suppliers",
                                                               description="Suppliers"),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title="Model Certificate Information",
                                                               description="Model Certificate Information")
                              }
                              )


class ModelCreateApi(ApiMixin):

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="The parameters required for the call function",
                              description="The parameters required for the call function",
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title="Name of model",
                                                         description="Name of model"),
                                  'provider': openapi.Schema(type=openapi.TYPE_STRING,
                                                             title="Suppliers",
                                                             description="Suppliers"),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="Suppliers",
                                                               description="Suppliers"),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="Suppliers",
                                                               description="Suppliers"),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title="Model Certificate Information",
                                                               description="Model Certificate Information")
                              }
                              )


class ProvideApi(ApiMixin):
    class ModelTypeList(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Name of supply'),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['key', 'value'],
                properties={
                    'key': openapi.Schema(type=openapi.TYPE_STRING, title="Model Type Description",
                                          description="Model Type Description", default="The big language model."),
                    'value': openapi.Schema(type=openapi.TYPE_STRING, title="Model Type Value",
                                            description="Model Type Value", default="LLM"),

                }
            )

    class ModelList(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Name of supply'),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Type of Model'),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_type'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of model",
                                           description="Name of model", default="Name of model"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Model Description",
                                           description="Model Description", default="xxxThe model"),
                    'model_type': openapi.Schema(type=openapi.TYPE_STRING, title="Model Type Value",
                                                 description="Model Type Value", default="LLM"),

                }
            )

    class ModelForm(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Name of supply'),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Type of Model'),
                    openapi.Parameter(name='model_name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Name of model'),
                    ]

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='provider',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Suppliers'),
                openapi.Parameter(name='method',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='The functions required.'),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="The parameters required for the call function",
                              description="The parameters required for the call function",
                              )
