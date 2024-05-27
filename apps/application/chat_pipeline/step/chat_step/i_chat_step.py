# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: i_chat_step.py
    @date:2024/1/9 18:17
    @desc: Dialogue
"""
from abc import abstractmethod
from typing import Type, List

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.serializers.application_serializers import NoReferencesSetting
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class ModelField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, BaseChatModel):
            self.fail('Model type errors', value=data)
        return data

    def to_representation(self, value):
        return value


class MessageField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, BaseMessage):
            self.fail('messageType of error', value=data)
        return data

    def to_representation(self, value):
        return value


class PostResponseHandler:
    @abstractmethod
    def handler(self, chat_id, chat_record_id, paragraph_list: List[ParagraphPipelineModel], problem_text: str,
                answer_text,
                manage, step, padding_problem_text: str = None, client_id=None, **kwargs):
        pass


class IChatStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # List of Dialogue
        message_list = serializers.ListField(required=True, child=MessageField(required=True),
                                             error_messages=ErrMessage.list("List of Dialogue"))
        # The big language model.
        chat_model = ModelField(required=False, allow_null=True, error_messages=ErrMessage.list("The big language model."))
        # List of paragraphs
        paragraph_list = serializers.ListField(error_messages=ErrMessage.list("List of paragraphs"))
        # Dialogueid
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("Dialogueid"))
        # User Problems
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.uuid("User Problems"))
        # The back processor.
        post_response_handler = InstanceField(model_type=PostResponseHandler,
                                              error_messages=ErrMessage.base("User Problems"))
        # Complete the problem.
        padding_problem_text = serializers.CharField(required=False, error_messages=ErrMessage.base("Complete the problem."))
        # Use the flow form of output
        stream = serializers.BooleanField(required=False, error_messages=ErrMessage.base("flow output."))
        client_id = serializers.CharField(required=True, error_messages=ErrMessage.char("The clientid"))
        client_type = serializers.CharField(required=True, error_messages=ErrMessage.char("Type of client"))
        # No queries for reference.
        no_references_setting = NoReferencesSetting(required=True, error_messages=ErrMessage.base("No reference to setup."))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            message_list: List = self.initial_data.get('message_list')
            for message in message_list:
                if not isinstance(message, BaseMessage):
                    raise Exception("message Type of error")

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        chat_result = self.execute(**self.context['step_args'], manage=manage)
        manage.context['chat_result'] = chat_result

    @abstractmethod
    def execute(self, message_list: List[BaseMessage],
                chat_id, problem_text,
                post_response_handler: PostResponseHandler,
                chat_model: BaseChatModel = None,
                paragraph_list=None,
                manage: PipelineManage = None,
                padding_problem_text: str = None, stream: bool = True, client_id=None, client_type=None,
                no_references_setting=None, **kwargs):
        pass
