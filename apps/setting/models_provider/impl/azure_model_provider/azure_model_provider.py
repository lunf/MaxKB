# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: azure_model_provider.py
    @date:2023/10/31 16:19
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain_community.chat_models.azure_openai import AzureChatOpenAI

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from setting.models_provider.impl.azure_model_provider.model.azure_chat_model import AzureChatModel
from smartdoc.conf import PROJECT_DIR


class AzureLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = AzureModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')

        for key in ['api_base', 'api_key', 'deployment_name']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            model = AzureModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='Hello Hello')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, 'Study Failure,Please check if the parameters are correct.')
            else:
                return False

        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_base = forms.TextInputField('API Domain Name', required=True)

    api_key = forms.PasswordInputField("API Key", required=True)

    deployment_name = forms.TextInputField("Deployment Name", required=True)


class DefaultAzureLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = AzureModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')

        for key in ['api_base', 'api_key', 'deployment_name', 'api_version']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            model = AzureModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='Hello Hello')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, 'Study Failure,Please check if the parameters are correct.')
            else:
                return False

        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_version = forms.TextInputField("api_version", required=True)

    api_base = forms.TextInputField('API Domain Name', required=True)

    api_key = forms.PasswordInputField("API Key", required=True)

    deployment_name = forms.TextInputField("Deployment Name", required=True)


azure_llm_model_credential = AzureLLMModelCredential()

base_azure_llm_model_credential = DefaultAzureLLMModelCredential()

model_dict = {
    'gpt-3.5-turbo-0613': ModelInfo('gpt-3.5-turbo-0613', '', ModelTypeConst.LLM, azure_llm_model_credential,
                                    api_version='2023-07-01-preview'),
    'gpt-3.5-turbo-0301': ModelInfo('gpt-3.5-turbo-0301', '', ModelTypeConst.LLM, azure_llm_model_credential,
                                    api_version='2023-07-01-preview'),
    'gpt-3.5-turbo-16k-0613': ModelInfo('gpt-3.5-turbo-16k-0613', '', ModelTypeConst.LLM, azure_llm_model_credential,
                                        api_version='2023-07-01-preview'),
    'gpt-4-0613': ModelInfo('gpt-4-0613', '', ModelTypeConst.LLM, azure_llm_model_credential,
                            api_version='2023-07-01-preview'),
}


class AzureModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> AzureChatOpenAI:
        model_info: ModelInfo = model_dict.get(model_name)
        azure_chat_open_ai = AzureChatModel(
            azure_endpoint=model_credential.get('api_base'),
            openai_api_version=model_info.api_version if model_name in model_dict else model_credential.get(
                'api_version'),
            deployment_name=model_credential.get('deployment_name'),
            openai_api_key=model_credential.get('api_key'),
            openai_api_type="azure"
        )
        return azure_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return base_azure_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_azure_provider', name='Azure OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'azure_model_provider', 'icon',
                         'azure_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, 'Models cannot be empty.')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "The big language model.", 'value': "LLM"}]
