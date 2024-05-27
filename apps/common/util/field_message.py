# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: field_message.py
    @date:2024/3/1 14:30
    @desc:
"""
from django.utils.translation import gettext_lazy


class ErrMessage:
    @staticmethod
    def char(field: str):
        return {
            'invalid': gettext_lazy("【%s】Not an effective string. " % field),
            'blank': gettext_lazy("【%s】This field cannot be for empty characters. " % field),
            'max_length': gettext_lazy("【%s】Please make sure that the number of characters in this field does not exceed {max_length} one. " % field),
            'min_length': gettext_lazy("【%s】Please make sure that this field contains at least {min_length} A character. " % field),
            'required': gettext_lazy('【%s】This field must be filled. ' % field),
            'null': gettext_lazy('【%s】This field cannot benull. ' % field)
        }

    @staticmethod
    def uuid(field: str):
        return {'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field),
                'invalid': gettext_lazy("【%s】must be effective.UUID. " % field),
                }

    @staticmethod
    def integer(field: str):
        return {'invalid': gettext_lazy('【%s】must be effective.integer. ' % field),
                'max_value': gettext_lazy('【%s】Make sure that this value is less than or equal to {max_value} . ' % field),
                'min_value': gettext_lazy('【%s】Make sure that the value is greater than or equal to {min_value} . ' % field),
                'max_string_length': gettext_lazy('【%s】The string is too big. ') % field,
                'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field),
                }

    @staticmethod
    def list(field: str):
        return {'not_a_list': gettext_lazy('【%s】should be a list.,But the type is "{input_type}".' % field),
                'empty': gettext_lazy('【%s】This list cannot be empty. ' % field),
                'min_length': gettext_lazy('【%s】Please make sure that this field contains at least {min_length} one element. ' % field),
                'max_length': gettext_lazy('【%s】Please make sure that the elements in this field do not exceed {max_length} one. ' % field),
                'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field),
                }

    @staticmethod
    def boolean(field: str):
        return {'invalid': gettext_lazy('【%s】It must be effective bull value. ' % field),
                'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field)}

    @staticmethod
    def dict(field: str):
        return {'not_a_dict': gettext_lazy('【%s】It should be a dictionary.,But the type is "{input_type}' % field),
                'empty': gettext_lazy('【%s】may be empty. ' % field),
                'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field),
                }

    @staticmethod
    def float(field: str):
        return {'invalid': gettext_lazy('【%s】We need an effective number. ' % field),
                'max_value': gettext_lazy('【%s】Make sure that this value is less than or equal to {max_value}. ' % field),
                'min_value': gettext_lazy('【%s】Make sure that the value is greater than or equal to {min_value}. ' % field),
                'max_string_length': gettext_lazy('【%s】The string is too big. ' % field),
                'required': gettext_lazy('【%s】This field must be filled. ' % field),
                'null': gettext_lazy('【%s】This field cannot benull. ' % field),
                }

    @staticmethod
    def json(field: str):
        return {
            'invalid': gettext_lazy('【%s】The value must be effective.JSON. ' % field),
            'required': gettext_lazy('【%s】This field must be filled. ' % field),
            'null': gettext_lazy('【%s】This field cannot benull. ' % field),
        }

    @staticmethod
    def base(field: str):
        return {
            'required': gettext_lazy('【%s】This field must be filled. ' % field),
            'null': gettext_lazy('【%s】This field cannot benull. ' % field),
        }

    @staticmethod
    def date(field: str):
        return {
            'required': gettext_lazy('【%s】This field must be filled. ' % field),
            'null': gettext_lazy('【%s】This field cannot benull. ' % field),
            'invalid': gettext_lazy('【%s】Date Format Error. Please change one of the following formats.  {format}. '),
            'datetime': gettext_lazy('【%s】It should be date. But it is the date time. ')
        }

    @staticmethod
    def image(field: str):
        return {
            'required': gettext_lazy('【%s】This field must be filled. ' % field),
            'null': gettext_lazy('【%s】This field cannot benull. ' % field),
            'invalid_image': gettext_lazy('【%s】upload effective images. The file you upload is not an image or an image has been damaged. ' % field),
            'max_length': gettext_lazy('Please make sure that this file name contains a maximum of {max_length} A character.(The length is {length}). ')
        }
