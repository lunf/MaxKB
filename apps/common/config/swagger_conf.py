# coding=utf-8
"""
    @project: qabot
    @Author：The Tiger
    @file： swagger_conf.py
    @date：2023/9/5 14:01
    @desc: usedswagger The group
"""

from drf_yasg.inspectors import SwaggerAutoSchema

tags_dict = {
    'user': 'Users'
}


class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        tags = super().get_tags(operation_keys)
        if "api" in tags and operation_keys:
            return [tags_dict.get(operation_keys[1]) if operation_keys[1] in tags_dict else operation_keys[1]]
        return tags
