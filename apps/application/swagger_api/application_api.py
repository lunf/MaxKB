# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： application_key.py
    @date：2023/11/7 10:50
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ApplicationApi(ApiMixin):
    class EditApplicationIcon(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_FILE,
                                  required=True,
                                  description='uploaded documents')
            ]

    class Authentication(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['access_token', ],
                properties={
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING, title="Applied certificationtoken",
                                                   description="Applied certificationtoken"),

                }
            )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'user_id', 'status', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description="The key.id"),
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="Application Name", description="Application Name"),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Application Description", description="Application Description"),
                'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="The modelid", description="The modelid"),
                "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Open multiple rounds of dialogue.",
                                                           description="Open multiple rounds of dialogue."),
                'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="Opening White.", description="Opening White."),
                'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                          title="Examples List", description="Examples List"),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="The User", description="The User"),

                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="is published.", description='is published.'),

                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.", description='Creating time.'),

                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.", description='Change time.'),

                'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_STRING),
                                                  title="The Knowledge BaseIdList of",
                                                  description="The Knowledge BaseIdList of(Return when requesting details.)")
            }
        )

    class ApiKey(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Applicationsid')

                    ]

        class Operate(ApiMixin):
            @staticmethod
            def get_request_params_api():
                return [openapi.Parameter(name='application_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description='Applicationsid'),
                        openapi.Parameter(name='api_key_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description='Applicationsapi_key id')
                        ]

            @staticmethod
            def get_request_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=[],
                    properties={
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is Active",
                                                     description="whether to activate"),
                        'allow_cross_domain': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Whether cross-domain is allowed",
                                                            description="Whether cross-domain is allowed"),
                        'cross_domain_list': openapi.Schema(type=openapi.TYPE_ARRAY, title='Cross-domain list',
                                                            items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )

    class AccessToken(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Applicationsid')

                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'access_token_reset': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="RepairedToken",
                                                         description="RepairedToken"),

                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="is activated.", description="is activated."),
                    'access_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="Number of Visits", description="Number of Visits"),
                    'white_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Open the white list.",
                                                   description="Open the white list."),
                    'white_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_STRING), title="List of white lists",
                                                 description="List of white lists"),
                    'show_source': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Showing a source of knowledge",
                                                  description="Showing a source of knowledge"),
                }
            )

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Application Name", description="Application Name"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Application Description", description="Application Description"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="The modelid", description="The modelid"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Open multiple rounds of dialogue.",
                                                               description="Open multiple rounds of dialogue."),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="Opening White.", description="Opening White."),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="The Knowledge BaseIdList of", description="The Knowledge BaseIdList of"),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Problems optimized",
                                                           description="Optimization of the problem.", default=True),
                    'icon': openapi.Schema(type=openapi.TYPE_STRING, title="icon",
                                           description="icon", default="/ui/favicon.ico")

                }
            )

    class DatasetSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[''],
                properties={
                    'top_n': openapi.Schema(type=openapi.TYPE_NUMBER, title="Reference to the number of points.", description="Reference to the number of points.",
                                            default=5),
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title='similarity', description="similarity",
                                                 default=0.6),
                    'max_paragraph_char_number': openapi.Schema(type=openapi.TYPE_NUMBER, title='Maximum number of characters.',
                                                                description="Maximum number of characters.", default=3000),
                    'search_mode': openapi.Schema(type=openapi.TYPE_STRING, title='The search model.',
                                                  description="embedding|keywords|blend", default='embedding'),
                    'no_references_setting': openapi.Schema(type=openapi.TYPE_OBJECT, title='The search model.',
                                                            required=['status', 'value'],
                                                            properties={
                                                                'status': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                         title="state of",
                                                                                         description="aiReply:ai_questioning,Identifying Answer:designated_answer",
                                                                                         default='ai_questioning'),
                                                                'value': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        title="Value",
                                                                                        description="aiReply:It is the word.,Identifying Answer:Identify the answer content.",
                                                                                        default='{question}'),
                                                            }),
                }
            )

    class ModelSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['prompt'],
                properties={
                    'prompt': openapi.Schema(type=openapi.TYPE_STRING, title="Suggestions", description="Suggestions",
                                             default=('known information：'
                                                      '\n{data}'
                                                      '\nReply to Request：'
                                                      '\n- If you don’t know the answer or don’t get the answer.，Please answer“No information found in the knowledge base.，Consulting relevant technical support or reference to official documents for operation”。'
                                                      '\n- Avoid mention that you are from<data></data>Knowledge obtained in。'
                                                      '\n- Please keep the answer and<data></data>The description is consistent.。'
                                                      '\n- Please usemarkdown Optimization of Answer Formats。'
                                                      '\n- <data></data>The image link.、Link address and script language please return.。'
                                                      '\n- Please use the same language to answer the question.。'
                                                      '\nThe problem：'
                                                      '\n{question}')),

                }
            )

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'dataset_setting', 'model_setting',
                          'problem_optimization'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="Application Name", description="Application Name"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="Application Description", description="Application Description"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="The modelid", description="The modelid"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Open multiple rounds of dialogue.",
                                                               description="Open multiple rounds of dialogue."),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="Opening White.", description="Opening White."),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="The Knowledge BaseIdList of", description="The Knowledge BaseIdList of"),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Problems optimized",
                                                           description="Optimization of the problem.", default=True)

                }
            )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Application Name'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Application Description')
                    ]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Applicationsid'),

                    ]
