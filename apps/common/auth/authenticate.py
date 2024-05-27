# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: authenticate.py
    @date:2023/9/4 11:16
    @desc:  Certification Classes
"""
import traceback

from django.core import cache
from django.core import signing
from rest_framework.authentication import TokenAuthentication

from common.auth.handle.impl.application_key import ApplicationKey
from common.auth.handle.impl.public_access_token import PublicAccessToken
from common.auth.handle.impl.user_token import UserToken
from common.exception.app_exception import AppAuthenticationFailed, AppEmbedIdentityFailed, AppChatNumOutOfBoundsFailed

token_cache = cache.caches['token_cache']


class AnonymousAuthentication(TokenAuthentication):
    def authenticate(self, request):
        return None, None


handles = [UserToken(), PublicAccessToken(), ApplicationKey()]


class TokenDetails:
    token_details = None
    is_load = False

    def __init__(self, token: str):
        self.token = token

    def get_token_details(self):
        if self.token_details is None and not self.is_load:
            try:
                self.token_details = signing.loads(self.token)
            except Exception as e:
                self.is_load = True
        return self.token_details


class TokenAuth(TokenAuthentication):
    # again authenticate Method, Customized Certification Rules
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        # Uncertified
        if auth is None:
            raise AppAuthenticationFailed(1003, 'not registered.,Please log in first.')
        try:
            token_details = TokenDetails(auth)
            for handle in handles:
                if handle.support(request, auth, token_details.get_token_details):
                    return handle.handle(request, auth, token_details.get_token_details)
            raise AppAuthenticationFailed(1002, "Identification information is incorrect.！illegal users")
        except Exception as e:
            traceback.format_exc()
            if isinstance(e, AppEmbedIdentityFailed) or isinstance(e, AppChatNumOutOfBoundsFailed):
                raise e
            raise AppAuthenticationFailed(1002, "Identification information is incorrect.！illegal users")
