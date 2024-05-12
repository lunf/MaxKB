# coding=utf-8
"""
    @project: qabot
    @Author：The Tiger
    @file： team_serializers.py
    @date：2023/9/5 16:32
    @desc:
"""
import datetime
import os
import random
import re
import uuid

from django.core import validators, signing, cache
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.db.models import Q, QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from application.models import Application
from common.constants.authentication_type import AuthenticationType
from common.constants.exception_code_constants import ExceptionCodeConstants
from common.constants.permission_constants import RoleConstants, get_permission_list_by_role
from common.db.search import page_search
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.response.result import get_api_response
from common.util.field_message import ErrMessage
from common.util.lock import lock
from dataset.models import DataSet, Document, Paragraph, Problem, ProblemParagraphMapping
from setting.models import Team, SystemSetting, SettingType, Model, TeamMember, TeamMemberPermission
from smartdoc.conf import PROJECT_DIR
from users.models.user import User, password_encrypt, get_user_dynamics_permission

user_cache = cache.caches['user_cache']


class SystemSerializer(ApiMixin, serializers.Serializer):
    @staticmethod
    def get_profile():
        version = os.environ.get('MAXKB_VERSION')
        return {'version': version}

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[],
            properties={
                'version': openapi.Schema(type=openapi.TYPE_STRING, title="The system version number.", description="The system version number."),
            }
        )


class LoginSerializer(ApiMixin, serializers.Serializer):
    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char("User Name"))

    password = serializers.CharField(required=True, error_messages=ErrMessage.char("The code"))

    def is_valid(self, *, raise_exception=False):
        """
        The exam parameters.
        :param raise_exception: Remove the abnormal. Only isTrue
        :return: User Information
        """
        super().is_valid(raise_exception=True)
        username = self.data.get("username")
        password = password_encrypt(self.data.get("password"))
        user = QuerySet(User).filter(Q(username=username,
                                       password=password) | Q(email=username,
                                                              password=password)).first()
        if user is None:
            raise ExceptionCodeConstants.INCORRECT_USERNAME_AND_PASSWORD.value.to_app_api_exception()
        if not user.is_active:
            raise AppApiException(1005, "Users are banned.,Please contact the manager.!")
        return user

    def get_user_token(self):
        """
        Obtaining UsersToken
        :return: UsersToken(Certification Information)
        """
        user = self.is_valid()
        token = signing.dumps({'username': user.username, 'id': str(user.id), 'email': user.email,
                               'type': AuthenticationType.USER.value})
        return token

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="The code", description="The code")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_STRING,
            title="token",
            default="xxxx",
            description="Certificationtoken"
        ))


class RegisterSerializer(ApiMixin, serializers.Serializer):
    """
    Subjects of registration request
    """
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char("The mailbox"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char("User Name"),
                                     max_length=20,
                                     min_length=6,
                                     validators=[
                                         validators.RegexValidator(regex=re.compile("^[a-zA-Z][a-zA-Z0-9_]{5,20}$"),
                                                                   message="The number of characters in the username is 6-20 characters, and it must start with a letter. Letters, numbers, underscores, etc. can be used.")
                                     ])
    password = serializers.CharField(required=True, error_messages=ErrMessage.char("The code"),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message="Password Length6-20A character. Must have letters.、The numbers、Special character combination.")])

    re_password = serializers.CharField(required=True,
                                        error_messages=ErrMessage.char("Confirm the password."),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message="Confirm the password length.6-20A character. Must have letters.、The numbers、Special character combination.")])

    code = serializers.CharField(required=True, error_messages=ErrMessage.char("verification code"))

    class Meta:
        model = User
        fields = '__all__'

    @lock(lock_key=lambda this, raise_exception: (
            this.initial_data.get("email") + ":register"

    ))
    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('password') != self.data.get('re_password'):
            raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()
        username = self.data.get("username")
        email = self.data.get("email")
        code = self.data.get("code")
        code_cache_key = email + ":register"
        cache_code = user_cache.get(code_cache_key)
        if code != cache_code:
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        u = QuerySet(User).filter(Q(username=username) | Q(email=email)).first()
        if u is not None:
            if u.email == email:
                raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
            if u.username == username:
                raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

        return True

    @transaction.atomic
    def save(self, **kwargs):
        m = User(
            **{'id': uuid.uuid1(), 'email': self.data.get("email"), 'username': self.data.get("username"),
               'role': RoleConstants.USER.name})
        m.set_password(self.data.get("password"))
        # Insert the user.
        m.save()
        # The initial user team.
        Team(**{'user': m, 'name': m.username + 'The team.'}).save()
        email = self.data.get("email")
        code_cache_key = email + ":register"
        # Remove the verification code.
        user_cache.delete(code_cache_key)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 're_password', 'code'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="The code", description="The code"),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title="Confirm the password.", description="Confirm the password."),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="verification code", description="verification code")
            }
        )


class CheckCodeSerializer(ApiMixin, serializers.Serializer):
    """
     School verification code.
    """
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char("The mailbox"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])
    code = serializers.CharField(required=True, error_messages=ErrMessage.char("verification code"))

    type = serializers.CharField(required=True,
                                 error_messages=ErrMessage.char("Type of"),
                                 validators=[
                                     validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                                               message="Type only supports.register|reset_password", code=500)
                                 ])

    def is_valid(self, *, raise_exception=False):
        super().is_valid()
        value = user_cache.get(self.data.get("email") + ":" + self.data.get("type"))
        if value is None or value != self.data.get("code"):
            raise ExceptionCodeConstants.CODE_ERROR.value.to_app_api_exception()
        return True

    class Meta:
        model = User
        fields = '__all__'

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="verification code", description="verification code"),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title="Type of", description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            title="is successful.",
            default=True,
            description="The wrong advice."))


class RePasswordSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages=ErrMessage.char("The mailbox"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    code = serializers.CharField(required=True, error_messages=ErrMessage.char("verification code"))

    password = serializers.CharField(required=True, error_messages=ErrMessage.char("The code"),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message="Confirm the password length.6-20A character.，Must have letters.、The numbers、Special character combination.")])

    re_password = serializers.CharField(required=True, error_messages=ErrMessage.char("Confirm the password."),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message="Confirm the password length.6-20A character.，Must have letters.、The numbers、Special character combination.")]
                                        )

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        email = self.data.get("email")
        cache_code = user_cache.get(email + ':reset_password')
        if self.data.get('password') != self.data.get('re_password'):
            raise AppApiException(ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.code,
                                  ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.message)
        if cache_code != self.data.get('code'):
            raise AppApiException(ExceptionCodeConstants.CODE_ERROR.value.code,
                                  ExceptionCodeConstants.CODE_ERROR.value.message)
        return True

    def reset_password(self):
        """
        Modify the password.
        :return: is successful.
        """
        if self.is_valid():
            email = self.data.get("email")
            QuerySet(User).filter(email=email).update(
                password=password_encrypt(self.data.get('password')))
            code_cache_key = email + ":reset_password"
            # Remove the verification code.
            user_cache.delete(code_cache_key)
            return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code', "password", 're_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="verification code", description="verification code"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, title="The code", description="The code"),
                're_password': openapi.Schema(type=openapi.TYPE_STRING, title="Confirm the password.", description="Confirm the password.")
            }
        )


class SendEmailSerializer(ApiMixin, serializers.Serializer):
    email = serializers.EmailField(
        required=True
        , error_messages=ErrMessage.char("The mailbox"),
        validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                              code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

    type = serializers.CharField(required=True, error_messages=ErrMessage.char("Type of"), validators=[
        validators.RegexValidator(regex=re.compile("^register|reset_password$"),
                                  message="Type only supports.register|reset_password", code=500)
    ])

    class Meta:
        model = User
        fields = '__all__'

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        user_exists = QuerySet(User).filter(email=self.data.get('email')).exists()
        if not user_exists and self.data.get('type') == 'reset_password':
            raise ExceptionCodeConstants.EMAIL_IS_NOT_EXIST.value.to_app_api_exception()
        elif user_exists and self.data.get('type') == 'register':
            raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
        code_cache_key = self.data.get('email') + ":" + self.data.get("type")
        code_cache_key_lock = code_cache_key + "_lock"
        ttl = user_cache.ttl(code_cache_key_lock)
        if ttl is not None:
            raise AppApiException(500, f"{ttl.total_seconds()}Do not send emails again in a second.")
        return True

    def send(self):
        """
        sending the mail.
        :return:   sending success.
        :exception Unusual failure.
        """
        email = self.data.get("email")
        state = self.data.get("type")
        # Create a random verification code.
        code = "".join(list(map(lambda i: random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'
                                                         ]), range(6))))
        # Get a mail template.
        file = open(os.path.join(PROJECT_DIR, "apps", "common", 'template', 'email_template.html'), "r",
                    encoding='utf-8')
        content = file.read()
        file.close()
        code_cache_key = email + ":" + state
        code_cache_key_lock = code_cache_key + "_lock"
        # Set up cache.
        user_cache.set(code_cache_key_lock, code, timeout=datetime.timedelta(minutes=1))
        system_setting = QuerySet(SystemSetting).filter(type=SettingType.EMAIL.value).first()
        if system_setting is None:
            user_cache.delete(code_cache_key_lock)
            raise AppApiException(1004, "The mailbox is not set.,Please contact the administrator.")
        try:
            connection = EmailBackend(system_setting.meta.get("email_host"),
                                      system_setting.meta.get('email_port'),
                                      system_setting.meta.get('email_host_user'),
                                      system_setting.meta.get('email_host_password'),
                                      system_setting.meta.get('email_use_tls'),
                                      False,
                                      system_setting.meta.get('email_use_ssl')
                                      )
            # sending the mail.
            send_mail(f'【MaxKB Intelligent Knowledge Base-{"User Registration" if state == "register" else "Modify the password."}】',
                      '',
                      html_message=f'{content.replace("${code}", code)}',
                      from_email=system_setting.meta.get('from_email'),
                      recipient_list=[email], fail_silently=False, connection=connection)
        except Exception as e:
            user_cache.delete(code_cache_key_lock)
            raise AppApiException(500, f"{str(e)}Email sent failed.")
        user_cache.set(code_cache_key, code, timeout=datetime.timedelta(minutes=30))
        return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'type'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'type': openapi.Schema(type=openapi.TYPE_STRING, title="Type of", description="register|reset_password")
            }
        )

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(type=openapi.TYPE_STRING, default=True))


class UserProfile(ApiMixin):

    @staticmethod
    def get_user_profile(user: User):
        """
        Obtaining User Details
        :param user: User Objects
        :return:
        """
        permission_list = get_user_dynamics_permission(str(user.id))
        permission_list += [p.value for p in get_permission_list_by_role(RoleConstants[user.role])]
        return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role,
                'permissions': [str(p) for p in permission_list],
                'is_edit_password': user.password == 'd880e722c47a34d8e9fce789fc62389d' if user.role == 'ADMIN' else False}

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="Usersid", description="Usersid"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="The role", description="The role"),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title="Is Available", description="Is Available"),
                "permissions": openapi.Schema(type=openapi.TYPE_ARRAY, title="List of permissions", description="List of permissions",
                                              items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        )


class UserSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "id",
                  "username", ]

    def get_response_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'role', 'is_active'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="Usersid", description="Usersid"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="The role", description="The role"),
                'is_active': openapi.Schema(type=openapi.TYPE_STRING, title="Is Available", description="Is Available")
            }
        )

    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='email_or_username',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Mailbox or User Name')]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'id'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='User keyid', description="User keyid"),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address.")
                }
            )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            email_or_username = self.data.get('email_or_username')
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model in
                    QuerySet(User).filter(Q(username=email_or_username) | Q(email=email_or_username))]


class UserInstanceSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'role', 'nick_name', 'create_time', 'update_time']

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'username', 'email', 'phone', 'is_active', 'role', 'nick_name', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="Usersid", description="Usersid"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, title="The phone number.", description="The phone number."),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="is activated.", description="is activated."),
                'role': openapi.Schema(type=openapi.TYPE_STRING, title="The role", description="The role"),
                'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of", description="Name of"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="Creating time.", description="Change time."),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="Change time.", description="Change time.")
            }
        )

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='user_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='User Nameid')

                ]


class UserManageSerializer(serializers.Serializer):
    class Query(ApiMixin, serializers.Serializer):
        email_or_username = serializers.CharField(required=False, allow_null=True,
                                                  error_messages=ErrMessage.char("Mailbox or User Name"))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='email_or_username',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='Mailbox or User Name')]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'id'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='User keyid', description="User keyid"),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address.")
                }
            )

        def get_query_set(self):
            email_or_username = self.data.get('email_or_username')
            query_set = QuerySet(User)
            if email_or_username is not None:
                query_set = query_set.filter(
                    Q(username__contains=email_or_username) | Q(email__contains=email_or_username))
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [{'id': user_model.id, 'username': user_model.username, 'email': user_model.email} for user_model in
                    self.get_query_set()]

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(current_page, page_size,
                               self.get_query_set(),
                               post_records_handler=lambda u: UserInstanceSerializer(u).data)

    class UserInstance(ApiMixin, serializers.Serializer):
        email = serializers.EmailField(
            required=True,
            error_messages=ErrMessage.char("The mailbox"),
            validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                                  code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

        username = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("User Name"),
                                         max_length=20,
                                         min_length=6,
                                         validators=[
                                             validators.RegexValidator(regex=re.compile("^[a-zA-Z][a-zA-Z0-9_]{5,20}$"),
                                                                       message="The number of characters in the username is 6-20 characters, and it must start with a letter. Letters, numbers, underscores, etc. can be used.")
                                         ])
        password = serializers.CharField(required=True, error_messages=ErrMessage.char("The code"),
                                         validators=[validators.RegexValidator(regex=re.compile(
                                             "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                             "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                             , message="Password Length6-20A character. Must have letters.、The numbers、Special character combination.")])

        nick_name = serializers.CharField(required=False, error_messages=ErrMessage.char("Name of"), max_length=64,
                                          allow_null=True, allow_blank=True)
        phone = serializers.CharField(required=False, error_messages=ErrMessage.char("The phone number."), max_length=20,
                                      allow_null=True, allow_blank=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            username = self.data.get('username')
            email = self.data.get('email')
            u = QuerySet(User).filter(Q(username=username) | Q(email=email)).first()
            if u is not None:
                if u.email == email:
                    raise ExceptionCodeConstants.EMAIL_IS_EXIST.value.to_app_api_exception()
                if u.username == username:
                    raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['username', 'email', 'password'],
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
                    'password': openapi.Schema(type=openapi.TYPE_STRING, title="The code", description="The code"),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, title="The phone number.", description="The phone number."),
                    'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of", description="Name of")
                }
            )

    class UserEditInstance(ApiMixin, serializers.Serializer):
        email = serializers.EmailField(
            required=False,
            error_messages=ErrMessage.char("The mailbox"),
            validators=[validators.EmailValidator(message=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.message,
                                                  code=ExceptionCodeConstants.EMAIL_FORMAT_ERROR.value.code)])

        nick_name = serializers.CharField(required=False, error_messages=ErrMessage.char("Name of"), max_length=64,
                                          allow_null=True, allow_blank=True)
        phone = serializers.CharField(required=False, error_messages=ErrMessage.char("The phone number."), max_length=20,
                                      allow_null=True, allow_blank=True)
        is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char("Is Available"))

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            if QuerySet(User).filter(email=self.data.get('email')).exclude(id=user_id).exists():
                raise AppApiException(1004, "The mailbox has been used.")

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox"),
                    'nick_name': openapi.Schema(type=openapi.TYPE_STRING, title="Name of", description="Name of"),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING, title="The phone number.", description="The phone number."),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="Is Available", description="Is Available"),
                }
            )

    class RePasswordInstance(ApiMixin, serializers.Serializer):
        password = serializers.CharField(required=True, error_messages=ErrMessage.char("The code"),
                                         validators=[validators.RegexValidator(regex=re.compile(
                                             "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                             "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                             , message="Password Length6-20A character.，Must have letters.、The numbers、Special character combination.")])
        re_password = serializers.CharField(required=True, error_messages=ErrMessage.char("Confirm the password."),
                                            validators=[validators.RegexValidator(regex=re.compile(
                                                "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                                "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                                , message="Confirm the password length.6-20A character.，Must have letters.、The numbers、Special character combination.")]
                                            )

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['password', 're_password'],
                properties={
                    'password': openapi.Schema(type=openapi.TYPE_STRING, title="The code", description="The code"),
                    're_password': openapi.Schema(type=openapi.TYPE_STRING, title="Confirm the password.",
                                                  description="Confirm the password."),
                }
            )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('password') != self.data.get('re_password'):
                raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()

    @transaction.atomic
    def save(self, instance, with_valid=True):
        if with_valid:
            UserManageSerializer.UserInstance(data=instance).is_valid(raise_exception=True)

        user = User(id=uuid.uuid1(), email=instance.get('email'),
                    phone="" if instance.get('phone') is None else instance.get('phone'),
                    nick_name="" if instance.get('nick_name') is None else instance.get('nick_name')
                    , username=instance.get('username'), password=password_encrypt(instance.get('password')),
                    role=RoleConstants.USER.name,
                    is_active=True)
        user.save()
        # The initial user team.
        Team(**{'user': user, 'name': user.username + 'The team.'}).save()
        return UserInstanceSerializer(user).data

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("Usersid"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(User).filter(id=self.data.get('id')).exists():
                raise AppApiException(1004, "User does not exist.")

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                user = QuerySet(User).filter(id=self.data.get('id')).first()
                if user.role == RoleConstants.ADMIN.name:
                    raise AppApiException(1004, "Managers cannot be removed.")
            user_id = self.data.get('id')

            team_member_list = QuerySet(TeamMember).filter(Q(user_id=user_id) | Q(team_id=user_id))
            # Delete membership rights.
            QuerySet(TeamMemberPermission).filter(
                member_id__in=[team_member.id for team_member in team_member_list]).delete()
            # Remove Team Members
            team_member_list.delete()
            # Remove app related. Because the application is connected to the extension, there is no need to manually remove it.
            QuerySet(Application).filter(user_id=self.data.get('id')).delete()
            # Delete the data set.
            dataset_list = QuerySet(DataSet).filter(user_id=self.data.get('id'))
            dataset_id_list = [str(dataset.id) for dataset in dataset_list]
            QuerySet(Document).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(Paragraph).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(ProblemParagraphMapping).filter(dataset_id__in=dataset_id_list).delete()
            QuerySet(Problem).filter(dataset_id__in=dataset_id_list).delete()
            ListenerManagement.delete_embedding_by_dataset_id_list_signal.send(dataset_id_list)
            dataset_list.delete()
            # Remove the team.
            QuerySet(Team).filter(user_id=self.data.get('id')).delete()
            # Remove the model.
            QuerySet(Model).filter(user_id=self.data.get('id')).delete()
            # Remove Users
            QuerySet(User).filter(id=self.data.get('id')).delete()
            return True

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.UserEditInstance(data=instance).is_valid(user_id=self.data.get('id'),
                                                                              raise_exception=True)

            user = QuerySet(User).filter(id=self.data.get('id')).first()
            if user.role == RoleConstants.ADMIN.name and 'is_active' in instance and instance.get(
                    'is_active') is not None:
                raise AppApiException(1004, "Can't change the status of the manager.")
            update_keys = ['email', 'nick_name', 'phone', 'is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    user.__setattr__(update_key, instance.get(update_key))
            user.save()
            return UserInstanceSerializer(user).data

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user = QuerySet(User).filter(id=self.data.get('id')).first()
            return UserInstanceSerializer(user).data

        def re_password(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                UserManageSerializer.RePasswordInstance(data=instance).is_valid(raise_exception=True)
            user = QuerySet(User).filter(id=self.data.get('id')).first()
            user.password = password_encrypt(instance.get('password'))
            user.save()
            return True
