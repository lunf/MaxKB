# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: chat_api.py
    @date:2023/11/7 17:29
    @desc:
"""
from drf_yasg import openapi

from application.swagger_api.application_api import ApplicationApi
from common.mixins.api_mixin import ApiMixin


class ChatApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title="The problem", description="The problem"),
                're_chat': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Re-created", default=False),
                'stream': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Re-created", default=True)

            }
        )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'application', 'abstract', 'chat_record_count', 'mark_sum', 'star_num', 'trample_num',
                      'update_time', 'create_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'application_id': openapi.Schema(type=openapi.TYPE_STRING, title="Applicationsid",
                                                 description="Applicationsid", default='Applicationsid'),
                'abstract': openapi.Schema(type=openapi.TYPE_STRING, title="The summary",
                                           description="The summary", default='The summary'),
                'chat_id': openapi.Schema(type=openapi.TYPE_STRING, title="Dialogueid",
                                          description="Dialogueid", default="Dialogueid"),
                'chat_record_count': openapi.Schema(type=openapi.TYPE_STRING, title="Number of Questions",
                                                    description="Number of Questions",
                                                    default="Number of Questions"),
                'mark_sum': openapi.Schema(type=openapi.TYPE_STRING, title="Number of Signs",
                                           description="Number of Signs", default=1),
                'star_num': openapi.Schema(type=openapi.TYPE_STRING, title="The number of praise.",
                                           description="The number of praise.", default=1),
                'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="The number of steps.",
                                              description="The number of steps.", default=1),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                              description="Change time.",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                              description="Creating time.",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )

    class OpenChat(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Applicationsid'),

                    ]

    class OpenTempChat(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['model_id', 'multiple_rounds_dialogue', 'dataset_setting', 'model_setting',
                          'problem_optimization'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="Applicationsid",
                                                     description="Applicationsid,The time of modification,No time for creation."),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="The modelid", description="The modelid"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="The Knowledge BaseIdList of", description="The Knowledge BaseIdList of"),
                    'multiple_rounds_dialogue': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Opening multiple sessions.",
                                                               description="Opening multiple sessions."),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Problems optimized",
                                                           description="Optimization of the problem.", default=True)
                }
            )

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='history_day',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_NUMBER,
                                  required=True,
                                  description='History of Days'),
                openapi.Parameter(name='abstract', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description="The summary"),
                openapi.Parameter(name='min_star', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description="The minimum number."),
                openapi.Parameter(name='min_trample', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description="The minimum number of steps."),
                openapi.Parameter(name='comparer', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description="or|and comparator")
                ]


class ChatRecordApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Dialogueid'),
                ]

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'chat', 'vote_status', 'dataset', 'paragraph', 'source_id', 'source_type',
                      'message_tokens', 'answer_tokens',
                      'problem_text', 'answer_text', 'improve_paragraph_id_list'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'chat': openapi.Schema(type=openapi.TYPE_STRING, title="Meeting Diaryid",
                                       description="Meeting Diaryid", default='Meeting Diaryid'),
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title="state of voting",
                                              description="state of voting", default="state of voting"),
                'dataset': openapi.Schema(type=openapi.TYPE_STRING, title="The data collectionid", description="The data collectionid",
                                          default="The data collectionid"),
                'paragraph': openapi.Schema(type=openapi.TYPE_STRING, title="Paragraphsid",
                                            description="Paragraphsid", default=1),
                'source_id': openapi.Schema(type=openapi.TYPE_STRING, title="Resourcesid",
                                            description="Resourcesid", default=1),
                'source_type': openapi.Schema(type=openapi.TYPE_STRING, title="Type of Resource",
                                              description="Type of Resource", default='xxx'),
                'message_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, title="The problem consumption.tokenNumber of",
                                                 description="The problem consumption.tokenNumber of", default=0),
                'answer_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, title="The answer is consumed.tokenNumber of",
                                                description="The answer is consumed.tokenNumber of", default=0),
                'improve_paragraph_id_list': openapi.Schema(type=openapi.TYPE_STRING, title="Improve the list of notes",
                                                            description="Improve the list of notes",
                                                            default=[]),
                'index': openapi.Schema(type=openapi.TYPE_STRING, title="The meeting. corresponding to below.",
                                        description="The meeting.idcorresponding to below.",
                                        default="The meeting.idcorresponding to below."
                                        ),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                              description="Change time.",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                              description="Creating time.",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )


class ImproveApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meetingid'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meeting recordsid'),
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='The knowledge baseid'),
                openapi.Parameter(name='document_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Documentsid'),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, title="Title of paragraph",
                                        description="Title of paragraph"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, title="Contents of paragraph",
                                          description="Contents of paragraph")

            }
        )


class VoteApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meetingid'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meeting recordsid')
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['vote_status'],
            properties={
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title="state of voting",
                                              description="-1:Cancel voting.|0:agreed|1:opposed"),

            }
        )


class ChatRecordImproveApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Applicationsid'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meetingid'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='Meeting recordsid')
                ]

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                      'document_id', 'title',
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
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.",
                                              description="Change time.",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.",
                                              description="Creating time.",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )
