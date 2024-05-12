# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： system_setting.py
    @date：2024/3/19 16:05
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class SystemSettingEmailApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="Parameters related to the mailbox",
                              description="Parameters related to the mailbox",
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="SMTP The host",
                                                               description="SMTP The host"),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title="SMTP The port.",
                                                               description="SMTP The port."),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title="The mailbox of the sender",
                                                                    description="The mailbox of the sender"),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title="The code",
                                                                        description="The code"),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="is opened.TLS",
                                                                  description="is opened.TLS"),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="is opened.SSL",
                                                                  description="is opened.SSL"),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="sending the mailbox.",
                                                               description="sending the mailbox.")
                              }
                              )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="Parameters related to the mailbox",
                              description="Parameters related to the mailbox",
                              required=['email_host', 'email_port', 'email_host_user', 'email_host_password',
                                        'email_use_tls', 'email_use_ssl', 'from_email'],
                              properties={
                                  'email_host': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="SMTP The host",
                                                               description="SMTP The host"),
                                  'email_port': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                               title="SMTP The port.",
                                                               description="SMTP The port."),
                                  'email_host_user': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    title="The mailbox of the sender",
                                                                    description="The mailbox of the sender"),
                                  'email_host_password': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        title="The code",
                                                                        description="The code"),
                                  'email_use_tls': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="is opened.TLS",
                                                                  description="is opened.TLS"),
                                  'email_use_ssl': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                  title="is opened.SSL",
                                                                  description="is opened.SSL"),
                                  'from_email': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="sending the mailbox.",
                                                               description="sending the mailbox.")
                              }
                              )
