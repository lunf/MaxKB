# coding=utf-8
"""
    @project: maxkb
    @Author: The Tiger
    @file:  model_management.py
    @date: 2023/10/31 15:11
    @desc:
"""
import uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Status(models.TextChoices):
    """Type of system setting."""
    SUCCESS = "SUCCESS", 'Successful'

    ERROR = "ERROR", "Failure"

    DOWNLOAD = "DOWNLOAD", 'Downloads'


class Model(AppModelMixin):
    """
    Model data
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")

    name = models.CharField(max_length=128, verbose_name="The name")

    status = models.CharField(max_length=20, verbose_name='Set the type.', choices=Status.choices,
                              default=Status.SUCCESS)

    model_type = models.CharField(max_length=128, verbose_name="Type of Model")

    model_name = models.CharField(max_length=128, verbose_name="Name of model")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Member Usersid")

    provider = models.CharField(max_length=128, verbose_name='Suppliers')

    credential = models.CharField(max_length=102400, verbose_name="Model Certification Information")

    meta = models.JSONField(verbose_name="Model of data,Used for storage downloads,or wrong information.", default=dict)

    class Meta:
        db_table = "model"
        unique_together = ['name', 'user_id']
