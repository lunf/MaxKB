# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: ollama_model_provider.py
    @date:2024/3/5 17:23
    @desc:
"""
import json
import os
from typing import Dict, Iterator
from urllib.parse import urlparse, ParseResult

import requests
from langchain.chat_models.base import BaseChatModel

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    BaseModelCredential, DownModelChunk, DownModelChunkStatus, ValidCode
from setting.models_provider.impl.ollama_model_provider.model.ollama_chat_model import OllamaChatModel
from smartdoc.conf import PROJECT_DIR

""


class OllamaLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = OllamaModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')
        try:
            model_list = OllamaModelProvider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, "API Domain Name Invalid")
        exist = [model for model in model_list.get('models') if
                 model.get('model') == model_name or model.get('model').replace(":latest", "") == model_name]
        if len(exist) == 0:
            raise AppApiException(ValidCode.model_not_fount, "The model does not exist.,Please download the model.")
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} Fields to fill fields.')
        self.api_key = model_info.get('api_key')
        return self

    api_base = forms.TextInputField('API Domain Name', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)


ollama_llm_model_credential = OllamaLLMModelCredential()

model_dict = {
    'llama2': ModelInfo(
        'llama2',
        'Llama 2 A set of pre-trained and micronutrated text models. The size from 70 Millions to 700 Millions are not waiting. This is 7B Pre-training model storage. Links to other models can be found in the index below. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2:13b': ModelInfo(
        'llama2:13b',
        'Llama 2 A set of pre-trained and micronutrated text models. The size from 70 Millions to 700 Millions are not waiting. This is 13B Pre-training model storage. Links to other models can be found in the index below. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2:70b': ModelInfo(
        'llama2:70b',
        'Llama 2 A set of pre-trained and micronutrated text models. The size from 70 Millions to 700 Millions are not waiting. This is 70B Pre-training model storage. Links to other models can be found in the index below. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2-chinese:13b': ModelInfo(
        'llama2-chinese:13b',
        'Because ofLlama2The Chinese is weak. We use Chinese instructions. Yesmeta-llama/Llama-2-13b-chat-hfperformedLoRAMinecraft, It has a strong Chinese dialogue ability. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama3:8b': ModelInfo(
        'llama3:8b',
        'Meta Llama 3:The most capable open products so farLLM. 8Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama3:70b': ModelInfo(
        'llama3:70b',
        'Meta Llama 3:The most capable open products so farLLM. 70Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:0.5b': ModelInfo(
        'qwen:0.5b',
        'qwen 1.5 0.5b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 0.5Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:1.8b': ModelInfo(
        'qwen:1.8b',
        'qwen 1.5 1.8b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 1.8Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:4b': ModelInfo(
        'qwen:4b',
        'qwen 1.5 4b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 4Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:7b': ModelInfo(
        'qwen:7b',
        'qwen 1.5 7b Compared to previous versions. The degree of conformity of the model with human preferences and multi-language1The ability to speak has been significantly enhanced. All sizes are supported.32768onetokensThe length of the above. 7Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:14b': ModelInfo(
        'qwen:14b',
        'qwen 1.5 14b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 14Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:32b': ModelInfo(
        'qwen:32b',
        'qwen 1.5 32b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 32Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:72b': ModelInfo(
        'qwen:72b',
        'qwen 1.5 72b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 72Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'qwen:110b': ModelInfo(
        'qwen:110b',
        'qwen 1.5 110b Compared to previous versions. The degree of compatibility with the human preferences and the multi-language processing ability has been significantly improved. All sizes are supported.32768onetokensThe length of the above. 110Millions of parameters. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'phi3': ModelInfo(
        'phi3',
        'Phi-3 MiniisMicrosoftof3.8BParameters, The light level. The most advanced open model. ',
        ModelTypeConst.LLM, ollama_llm_model_credential),
}


def get_base_url(url: str):
    parse = urlparse(url)
    return ParseResult(scheme=parse.scheme, netloc=parse.netloc, path='', params='',
                       query='',
                       fragment='').geturl()


def convert_to_down_model_chunk(row_str: str, chunk_index: int):
    row = json.loads(row_str)
    status = DownModelChunkStatus.unknown
    digest = ""
    progress = 100
    if 'status' in row:
        digest = row.get('status')
        if row.get('status') == 'success':
            status = DownModelChunkStatus.success
        if row.get('status').__contains__("pulling"):
            progress = 0
            status = DownModelChunkStatus.pulling
            if 'total' in row and 'completed' in row:
                progress = (row.get('completed') / row.get('total') * 100)
    elif 'error' in row:
        status = DownModelChunkStatus.error
        digest = row.get('error')
    return DownModelChunk(status=status, digest=digest, progress=progress, details=row_str, index=chunk_index)


def convert(response_stream) -> Iterator[DownModelChunk]:
    temp = ""
    index = 0
    for c in response_stream:
        index += 1
        row_content = c.decode()
        temp += row_content
        if row_content.endswith('}') or row_content.endswith('\n'):
            rows = [t for t in temp.split("\n") if len(t) > 0]
            for row in rows:
                yield convert_to_down_model_chunk(row, index)
            temp = ""

    if len(temp) > 0:
        print(temp)
        rows = [t for t in temp.split("\n") if len(t) > 0]
        for row in rows:
            yield convert_to_down_model_chunk(row, index)


class OllamaModelProvider(IModelProvider):
    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_ollama_provider', name='Ollama', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'ollama_model_provider', 'icon',
                         'ollama_icon_svg')))

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
        # If the model is not in configuration.,Use the default certification.
        return ollama_llm_model_credential

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseChatModel:
        api_base = model_credential.get('api_base')
        base_url = get_base_url(api_base)
        return OllamaChatModel(model=model_name, openai_api_base=(base_url + '/v1'),
                               openai_api_key=model_credential.get('api_key'))

    def get_dialogue_number(self):
        return 2

    @staticmethod
    def get_base_model_list(api_base):
        base_url = get_base_url(api_base)
        r = requests.request(method="GET", url=f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        return r.json()

    def down_model(self, model_type: str, model_name, model_credential: Dict[str, object]) -> Iterator[DownModelChunk]:
        api_base = model_credential.get('api_base')
        base_url = get_base_url(api_base)
        r = requests.request(
            method="POST",
            url=f"{base_url}/api/pull",
            data=json.dumps({"name": model_name}).encode(),
            stream=True,
        )
        return convert(r)
