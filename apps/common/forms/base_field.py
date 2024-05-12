# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： base_field.py
    @date：2023/10/31 18:07
    @desc:
"""
from enum import Enum
from typing import List, Dict


class TriggerType(Enum):
    # Implementation of functions OptionListThe data
    OPTION_LIST = 'OPTION_LIST'
    # Execution function to obtain subforms
    CHILD_FORMS = 'CHILD_FORMS'


class BaseField:
    def __init__(self,
                 input_type: str,
                 label: str,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_dict: Dict = None,
                 relation_trigger_field_dict: Dict = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        """

        :param input_type: Fields
        :param label: The Tip
        :param default_value: The default value
        :param relation_show_field_dict:        {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the show.
        :param relation_trigger_field_dict:     {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the middle Implementation of functions The data
        :param trigger_type:                    Type of executor  OPTION_LISTrequestedOption_listThe data CHILD_FORMSApplication form
        :param attrs:                           The frontattrThe data
        :param props_info:                      Other additional information
        """
        if props_info is None:
            props_info = {}
        if attrs is None:
            attrs = {}
        self.label = label
        self.attrs = attrs
        self.props_info = props_info
        self.default_value = default_value
        self.input_type = input_type
        self.relation_show_field_dict = {} if relation_show_field_dict is None else relation_show_field_dict
        self.relation_trigger_field_dict = [] if relation_trigger_field_dict is None else relation_trigger_field_dict
        self.required = required
        self.trigger_type = trigger_type

    def to_dict(self):
        return {
            'input_type': self.input_type,
            'label': self.label,
            'required': self.required,
            'default_value': self.default_value,
            'relation_show_field_dict': self.relation_show_field_dict,
            'relation_trigger_field_dict': self.relation_trigger_field_dict,
            'trigger_type': self.trigger_type.value,
            'attrs': self.attrs,
            'props_info': self.props_info,
        }


class BaseDefaultOptionField(BaseField):
    def __init__(self, input_type: str,
                 label: str,
                 text_field: str,
                 value_field: str,
                 option_list: List[dict],
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_dict: Dict[str, object] = None,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        """

        :param input_type:           Fields
        :param label:           label
        :param text_field:      Text fields
        :param value_field:     Value Fields
        :param option_list:     Optional lists
        :param required:        must be filled.
        :param default_value:   The default value
        :param relation_show_field_dict:        {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the show.
        :param attrs:                           The frontattrThe data
        :param props_info:                      Other additional information
        """
        super().__init__(input_type, label, required, default_value, relation_show_field_dict,
                         {}, TriggerType.OPTION_LIST, attrs, props_info)
        self.text_field = text_field
        self.value_field = value_field
        self.option_list = option_list

    def to_dict(self):
        return {**super().to_dict(), 'text_field': self.text_field, 'value_field': self.value_field,
                'option_list': self.option_list}


class BaseExecField(BaseField):
    def __init__(self,
                 input_type: str,
                 label: str,
                 text_field: str,
                 value_field: str,
                 provider: str,
                 method: str,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_dict: Dict = None,
                 relation_trigger_field_dict: Dict = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        """

        :param input_type:  Fields
        :param label:  The Tip
        :param text_field:  Text fields
        :param value_field: Value Fields
        :param provider:    Designated Suppliers
        :param method:      Implementation of Supplier Functions method
        :param required:    must be filled.
        :param default_value: The default value
        :param relation_show_field_dict:        {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the show.
        :param relation_trigger_field_dict:     {field:field_value_list} stated in fieldis worth ,and worth it.field_value_listIn the middle Implementation of functions The data
        :param trigger_type:                    Type of executor  OPTION_LISTrequestedOption_listThe data CHILD_FORMSApplication form
        :param attrs:                           The frontattrThe data
        :param props_info:                      Other additional information
        """
        super().__init__(input_type, label, required, default_value, relation_show_field_dict,
                         relation_trigger_field_dict,
                         trigger_type, attrs, props_info)
        self.text_field = text_field
        self.value_field = value_field
        self.provider = provider
        self.method = method

    def to_dict(self):
        return {**super().to_dict(), 'text_field': self.text_field, 'value_field': self.value_field,
                'provider': self.provider, 'method': self.method}
