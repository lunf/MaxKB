# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： common.py
    @date：2024/1/11 18:44
    @desc:
"""
from rest_framework import serializers


class InstanceField(serializers.Field):
    def __init__(self, model_type, **kwargs):
        self.model_type = model_type
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, self.model_type):
            self.fail('messageType of error', value=data)
        return data

    def to_representation(self, value):
        return value


class FunctionField(serializers.Field):

    def to_internal_value(self, data):
        if not callable(data):
            self.fail('Not a function.', value=data)
        return data

    def to_representation(self, value):
        return value


class UploadedImageField(serializers.ImageField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, value):
        return value
