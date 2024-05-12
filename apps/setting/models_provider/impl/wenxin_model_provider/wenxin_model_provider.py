# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： wenxin_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain_community.chat_models import QianfanChatEndpoint
from qianfan import ChatCompletion

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, BaseModelCredential, \
    ModelInfo, IModelProvider, ValidCode
from setting.models_provider.impl.wenxin_model_provider.model.qian_fan_chat_model import QianfanChatModel
from smartdoc.conf import PROJECT_DIR


class WenxinLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = WenxinModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')
        model_info = [model.lower() for model in ChatCompletion.models()]
        if not model_info.__contains__(model_name.lower()):
            raise AppApiException(ValidCode.valid_error.value, f'{model_name} Models are not supported.')
        for key in ['api_key', 'secret_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            WenxinModelProvider().get_model(model_type, model_name, model_credential).invoke(
                [HumanMessage(content='Hello Hello')])
        except Exception as e:
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'secret_key': super().encryption(model_info.get('secret_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'secret_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} Fields to fill fields.')
        self.api_key = model_info.get('api_key')
        self.secret_key = model_info.get('secret_key')
        return self

    api_key = forms.PasswordInputField('API Key', required=True)

    secret_key = forms.PasswordInputField("Secret Key", required=True)


win_xin_llm_model_credential = WenxinLLMModelCredential()
model_dict = {
    'ERNIE-Bot-4': ModelInfo('ERNIE-Bot-4',
                             'ERNIE-Bot-4It is a large language model developed by itself.，Coverage of Chinese data，Have a stronger dialogue.、The ability to create content.。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential),

    'ERNIE-Bot': ModelInfo('ERNIE-Bot',
                           'ERNIE-BotIt is a large language model developed by itself.，Coverage of Chinese data，Have a stronger dialogue.、The ability to create content.。',
                           ModelTypeConst.LLM, win_xin_llm_model_credential),

    'ERNIE-Bot-turbo': ModelInfo('ERNIE-Bot-turbo',
                                 'ERNIE-Bot-turboIt is a large language model developed by itself.，Coverage of Chinese data，Have a stronger dialogue.、The ability to create content.，Reacting faster.。',
                                 ModelTypeConst.LLM, win_xin_llm_model_credential),

    'BLOOMZ-7B': ModelInfo('BLOOMZ-7B',
                           'BLOOMZ-7BIt is a great language model in the industry.，byBigScienceDevelopment and Open Source，can be46Languages and13Programming language text output。',
                           ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-7b-chat': ModelInfo('Llama-2-7b-chat',
                                 'Llama-2-7b-chatbyMeta AIDevelopment and Open Source，in coding.、Excellent scenes such as reasoning and knowledge application.，Llama-2-7b-chatHigh-performance original open source version.，Applied to the dialogue scene.。',
                                 ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-13b-chat': ModelInfo('Llama-2-13b-chat',
                                  'Llama-2-13b-chatbyMeta AIDevelopment and Open Source，in coding.、Excellent scenes such as reasoning and knowledge application.，Llama-2-13b-chatIt is an original open source version that balances performance and performance.，Applied to the dialogue scene.。',
                                  ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Llama-2-70b-chat': ModelInfo('Llama-2-70b-chat',
                                  'Llama-2-70b-chatbyMeta AIDevelopment and Open Source，in coding.、Excellent scenes such as reasoning and knowledge application.，Llama-2-70b-chatIt is an original open source version with high precision effect.。',
                                  ModelTypeConst.LLM, win_xin_llm_model_credential),

    'Qianfan-Chinese-Llama-2-7B': ModelInfo('Qianfan-Chinese-Llama-2-7B',
                                            'Thousands of teams.Llama-2-7bEnhanced Chinese version based on，inCMMLU、C-EVALExcellent performance in the Chinese knowledge base.。',
                                            ModelTypeConst.LLM, win_xin_llm_model_credential)
}


class WenxinModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 2

    def get_model(self, model_type, model_name, model_credential: Dict[str, object],
                  **model_kwargs) -> QianfanChatEndpoint:
        return QianfanChatModel(model=model_name,
                                qianfan_ak=model_credential.get('api_key'),
                                qianfan_sk=model_credential.get('secret_key'),
                                streaming=model_kwargs.get('streaming', False))

    def get_model_type_list(self):
        return [{'key': "The big language model.", 'value': "LLM"}]

    def get_model_list(self, model_type):
        if model_type is None:
            raise AppApiException(500, 'Models cannot be empty.')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return win_xin_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_wenxin_provider', name='A thousand model.', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'wenxin_model_provider', 'icon',
                         'azure_icon_svg')))
