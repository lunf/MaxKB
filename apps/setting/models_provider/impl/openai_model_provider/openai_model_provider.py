# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： openai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from setting.models_provider.impl.openai_model_provider.model.openai_chat_model import OpenAIChatModel
from smartdoc.conf import PROJECT_DIR


class OpenAILLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = OpenAIModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            model = OpenAIModelProvider().get_model(model_type, model_name, model_credential)
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


openai_llm_model_credential = OpenAILLMModelCredential()

model_dict = {
    'gpt-3.5-turbo': ModelInfo('gpt-3.5-turbo', 'The latestgpt-3.5-turbo，byOpenAIAdjust and update.', ModelTypeConst.LLM,
                               openai_llm_model_credential,
                               ),
    'gpt-3.5-turbo-0125': ModelInfo('gpt-3.5-turbo-0125',
                                    '2024Year1The Moon25The Daygpt-3.5-turboPhoto quickly.，Support the length.16,385 tokens', ModelTypeConst.LLM,
                                    openai_llm_model_credential,
                                    ),
    'gpt-3.5-turbo-1106': ModelInfo('gpt-3.5-turbo-1106',
                                    '2023Year11The Moon6The Daygpt-3.5-turboPhoto quickly.，Support the length.16,385 tokens', ModelTypeConst.LLM,
                                    openai_llm_model_credential,
                                    ),
    'gpt-3.5-turbo-0613': ModelInfo('gpt-3.5-turbo-0613',
                                    '[Legacy] 2023Year6The Moon13The Daygpt-3.5-turboPhoto quickly.，will be2024Year6The Moon13Day abandonment.',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
    'gpt-4': ModelInfo('gpt-4', 'The latestgpt-4，byOpenAIAdjust and update.', ModelTypeConst.LLM, openai_llm_model_credential,
                       ),
    'gpt-4-turbo': ModelInfo('gpt-4-turbo', 'The latestgpt-4-turbo，byOpenAIAdjust and update.', ModelTypeConst.LLM,
                             openai_llm_model_credential,
                             ),
    'gpt-4-turbo-preview': ModelInfo('gpt-4-turbo-preview', 'The latestgpt-4-turbo-preview，byOpenAIAdjust and update.',
                                     ModelTypeConst.LLM, openai_llm_model_credential,
                                     ),
    'gpt-4-turbo-2024-04-09': ModelInfo('gpt-4-turbo-2024-04-09',
                                        '2024Year4The Moon9The Daygpt-4-turboPhoto quickly.，Support the length.128,000 tokens',
                                        ModelTypeConst.LLM, openai_llm_model_credential,
                                        ),
    'gpt-4-0125-preview': ModelInfo('gpt-4-0125-preview', '2024Year1The Moon25The Daygpt-4-turboPhoto quickly.，Support the length.128,000 tokens',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
    'gpt-4-1106-preview': ModelInfo('gpt-4-1106-preview', '2023Year11The Moon6The Daygpt-4-turboPhoto quickly.，Support the length.128,000 tokens',
                                    ModelTypeConst.LLM, openai_llm_model_credential,
                                    ),
}


class OpenAIModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> OpenAIChatModel:
        azure_chat_open_ai = OpenAIChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key')
        )
        return azure_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return openai_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_openai_provider', name='OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'openai_model_provider', 'icon',
                         'openai_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, 'Models cannot be empty.')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "The big language model.", 'value': "LLM"}]
