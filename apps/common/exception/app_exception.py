# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: app_exception.py
    @date:2023/9/4 14:04
    @desc:
"""
from rest_framework import status


class AppApiException(Exception):
    """
    Unusual in the project.
    """
    status_code = status.HTTP_200_OK

    def __init__(self, code, message):
        self.code = code
        self.message = message


class NotFound404(AppApiException):
    """
       Uncertified(not registered.)Unusual
       """
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, code, message):
        self.code = code
        self.message = message


class AppAuthenticationFailed(AppApiException):
    """
    Uncertified(not registered.)Unusual
    """
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, code, message):
        self.code = code
        self.message = message


class AppUnauthorizedFailed(AppApiException):
    """
    not authorized.(No authority.)Unusual
    """
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, code, message):
        self.code = code
        self.message = message


class AppEmbedIdentityFailed(AppApiException):
    """
    embeddedcookieUnusual
    """
    status_code = 460

    def __init__(self, code, message):
        self.code = code
        self.message = message


class AppChatNumOutOfBoundsFailed(AppApiException):
    """
      Number of visits greater than today
    """
    status_code = 461

    def __init__(self, code, message):
        self.code = code
        self.message = message
