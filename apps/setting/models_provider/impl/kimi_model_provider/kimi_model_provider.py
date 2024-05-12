# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： kimi_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain.chat_models.base import BaseChatModel


from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from smartdoc.conf import PROJECT_DIR
from setting.models_provider.impl.kimi_model_provider.model.kimi_chat_model import KimiChatModel




class KimiLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = KimiModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            # llm_kimi = Moonshot(
            #     model_name=model_name,
            #     base_url=model_credential['api_base'],
            #     moonshot_api_key=model_credential['api_key']
            # )

            model = KimiModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='Hello Hello')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'Study Failure,Please check if the parameters are correct.: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_base = forms.TextInputField('API Domain Name', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)


kimi_llm_model_credential = KimiLLMModelCredential()

model_dict = {
    'moonshot-v1-8k': ModelInfo('moonshot-v1-8k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                               ),
    'moonshot-v1-32k': ModelInfo('moonshot-v1-32k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                                    ),
    'moonshot-v1-128k': ModelInfo('moonshot-v1-128k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                       )
}


class KimiModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseChatModel:
        kimi_chat_open_ai = KimiChatModel(
            openai_api_base=model_credential['api_base'],
            openai_api_key=model_credential['api_key'],
            model_name=model_name,
        )
        return kimi_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return kimi_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_kimi_provider', name='Kimi', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'kimi_model_provider', 'icon',
                         'kimi_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, 'Models cannot be empty.')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "The big language model.", 'value': "LLM"}]
