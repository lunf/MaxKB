# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： api_key_model.py
    @date：2023/11/14 17:15
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from application.models import Application
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class ApplicationApiKey(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="PrimaryId")
    secret_key = models.CharField(max_length=1024, verbose_name="Secret Key", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User Id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="Application Id")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    allow_cross_domain = models.BooleanField(default=False, verbose_name="Whether cross-domain is allowed")
    cross_domain_list = ArrayField(verbose_name="Cross-domain list",
                                base_field=models.CharField(max_length=128, blank=True)
                                , default=list)

    class Meta:
        db_table = "application_api_key"


class ApplicationAccessToken(AppModelMixin):
    """
    Applied certificationtoken
    """
    application = models.OneToOneField(Application, primary_key=True, on_delete=models.CASCADE, verbose_name="Application Id")
    access_token = models.CharField(max_length=128, verbose_name="User Open Access Certificationtoken", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Opening public access.")
    access_num = models.IntegerField(default=100, verbose_name="Number of Visits")
    white_active = models.BooleanField(default=False, verbose_name="Open the white list.")
    white_list = ArrayField(verbose_name="List of white lists",
                            base_field=models.CharField(max_length=128, blank=True)
                            , default=list)
    show_source = models.BooleanField(default=False, verbose_name="Showing a source of knowledge")

    class Meta:
        db_table = "application_access_token"


class ApplicationPublicAccessClient(AppModelMixin):
    id = models.UUIDField(max_length=128, primary_key=True, verbose_name="Public access link clientid")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="Application Id")
    access_num = models.IntegerField(default=0, verbose_name="Number of visits.")
    intraday_access_num = models.IntegerField(default=0, verbose_name="Number of visits on that day.")

    class Meta:
        db_table = "application_public_access_client"
