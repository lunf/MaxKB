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
from setting.models_provider.impl.gemini_model_provider.model.gemini_chat_model import GeminiChatModel
from smartdoc.conf import PROJECT_DIR


class GeminiLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = GeminiModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} Models are not supported.')

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} Fields to fill fields.')
                else:
                    return False
        try:
            model = GeminiModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='Hello Hello')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'Study Failure,Please check if the parameters are correct.  {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_key = forms.PasswordInputField('API Key', required=True)



gemini_llm_model_credential = GeminiLLMModelCredential()

model_dict = {
    'gemini-1.5-pro': ModelInfo('gemini-1.5-pro', '', ModelTypeConst.LLM, gemini_llm_model_credential,),
    'gemini-1.5-flash': ModelInfo('gemini-1.5-flash', '', ModelTypeConst.LLM, gemini_llm_model_credential,),
    'gemini-1.0-pro': ModelInfo('gemini-1.0-pro', '', ModelTypeConst.LLM, gemini_llm_model_credential,),
    'gemini-pro-vision': ModelInfo('gemini-pro-vision', '', ModelTypeConst.LLM, gemini_llm_model_credential,),
}


class GeminiModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> GeminiChatModel:
        os.environ["GOOGLE_API_KEY"] = model_credential.get('api_key')
        gemini_chat_model = GeminiChatModel(
            model=model_name,
        )
        return gemini_chat_model

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return gemini_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_gemini_provider', name='Google Gemini', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'gemini_model_provider', 'icon',
                         'gemini_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, 'Models cannot be empty.')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "The big language model.", 'value': "LLM"}]
