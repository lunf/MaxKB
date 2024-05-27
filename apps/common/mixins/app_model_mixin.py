# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: app_model_mixin.py
    @date:2023/9/21 9:41
    @desc:
"""
from django.db import models


class AppModelMixin(models.Model):
    create_time = models.DateTimeField(verbose_name="Creating time.", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="Change time.", auto_now=True)

    class Meta:
        abstract = True
        ordering = ['create_time']
