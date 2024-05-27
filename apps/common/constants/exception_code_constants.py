# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: exception_code_constants.py
    @date:2023/9/4 14:09
    @desc: Unusual Classes
"""
from enum import Enum

from common.exception.app_exception import AppApiException


class ExceptionCodeConstantsValue:
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def get_message(self):
        return self.message

    def get_code(self):
        return self.code

    def to_app_api_exception(self):
        return AppApiException(code=self.code, message=self.message)


class ExceptionCodeConstants(Enum):
    INCORRECT_USERNAME_AND_PASSWORD = ExceptionCodeConstantsValue(1000, "User name or password is incorrect.")
    NOT_AUTHENTICATION = ExceptionCodeConstantsValue(1001, "Please log in first.,and carry users.Token")
    EMAIL_SEND_ERROR = ExceptionCodeConstantsValue(1002, "Email sent failed.")
    EMAIL_FORMAT_ERROR = ExceptionCodeConstantsValue(1003, "Email Format Error")
    EMAIL_IS_EXIST = ExceptionCodeConstantsValue(1004, "The mailbox has been registered.,Do not repeat registration.")
    EMAIL_IS_NOT_EXIST = ExceptionCodeConstantsValue(1005, "The mailbox is not registered.,Please register first.")
    CODE_ERROR = ExceptionCodeConstantsValue(1005, "Verification code is incorrect.,or verification code.")
    USERNAME_IS_EXIST = ExceptionCodeConstantsValue(1006, "Username has been used.,Please use other user names.")
    USERNAME_ERROR = ExceptionCodeConstantsValue(1006, "Username cannot be empty.,and the length.6-20")
    PASSWORD_NOT_EQ_RE_PASSWORD = ExceptionCodeConstantsValue(1007, "Password is incompatible with confirmation.")
