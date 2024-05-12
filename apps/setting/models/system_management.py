# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： system_management.py
    @date：2024/3/19 13:47
    @desc: Postbox management
"""

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin


class SettingType(models.IntegerChoices):
    """Type of system setting."""
    EMAIL = 0, 'The mailbox'

    RSA = 1, "Private key."


class SystemSetting(AppModelMixin):
    """
     System settings
    """
    type = models.IntegerField(primary_key=True, verbose_name='Set the type.', choices=SettingType.choices,
                               default=SettingType.EMAIL)

    meta = models.JSONField(verbose_name="Configuration of data", default=dict)

    class Meta:
        db_table = "system_setting"
