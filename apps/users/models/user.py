# coding=utf-8
"""
    @project: qabot
    @Author：The Tiger
    @file： users.py
    @date：2023/9/4 10:09
    @desc:
"""
import hashlib
import os
import uuid

from django.db import models

from common.constants.permission_constants import Permission, Group, Operate
from common.db.sql_execute import select_list
from common.mixins.app_model_mixin import AppModelMixin
from common.util.file_util import get_file_content
from smartdoc.conf import PROJECT_DIR

__all__ = ["User", "password_encrypt", 'get_user_dynamics_permission']


def password_encrypt(raw_password):
    """
    The code md5Cryptocurrency
    :param raw_password: The code
    :return:  Password after encryption.
    """
    md5 = hashlib.md5()  # 2，Examplesmd5() Method
    md5.update(raw_password.encode())  # 3，Type of byte encryption of the string.
    result = md5.hexdigest()  # 4，Cryptocurrency
    return result


def to_dynamics_permission(group_type: str, operate: list[str], dynamic_tag: str):
    """
    Conversion to Authority Objects
    :param group_type:  Type of grouping
    :param operate:     Operations
    :param dynamic_tag: Signed
    :return: List of permissions
    """
    return [Permission(group=Group[group_type], operate=Operate[o], dynamic_tag=dynamic_tag)
            for o in operate]


def get_user_dynamics_permission(user_id: str):
    """
    obtained Applications and data set permissions
    :param user_id: Usersid
    :return: Users Applications and data set permissions
    """
    member_permission_list = select_list(
        get_file_content(os.path.join(PROJECT_DIR, "apps", "setting", 'sql', 'get_user_permission.sql')),
        [user_id, user_id, user_id])
    result = []
    for member_permission in member_permission_list:
        result += to_dynamics_permission(member_permission.get('type'), member_permission.get('operate'),
                                         str(member_permission.get('id')))
    return result


class User(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    email = models.EmailField(unique=True, verbose_name="The mailbox")
    phone = models.CharField(max_length=20, verbose_name="The phone", default="")
    nick_name = models.CharField(max_length=150, verbose_name="The name", default="")
    username = models.CharField(max_length=150, unique=True, verbose_name="User Name")
    password = models.CharField(max_length=150, verbose_name="The code")
    role = models.CharField(max_length=150, verbose_name="The role")
    is_active = models.BooleanField(default=True)
    create_time = models.DateTimeField(verbose_name="Creating time.", auto_now_add=True, null=True)
    update_time = models.DateTimeField(verbose_name="Change time.", auto_now=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def set_password(self, raw_password):
        self.password = password_encrypt(raw_password)
        self._password = raw_password
