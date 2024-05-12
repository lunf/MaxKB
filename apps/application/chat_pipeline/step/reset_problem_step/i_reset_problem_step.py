# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： i_reset_problem_step.py
    @date：2024/1/9 18:12
    @desc: Repeat the problem.
"""
from abc import abstractmethod
from typing import Type, List

from langchain.chat_models.base import BaseChatModel
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import ModelField
from application.models import ChatRecord
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class IResetProblemStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # The question text.
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.float("The question text."))
        # History Answer
        history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                    error_messages=ErrMessage.list("History Answer"))
        # The big language model.
        chat_model = ModelField(required=False, allow_null=True, error_messages=ErrMessage.base("The big language model."))

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        padding_problem = self.execute(**self.context.get('step_args'))
        # User input problem.
        source_problem_text = self.context.get('step_args').get('problem_text')
        self.context['problem_text'] = source_problem_text
        self.context['padding_problem_text'] = padding_problem
        manage.context['problem_text'] = source_problem_text
        manage.context['padding_problem_text'] = padding_problem
        # and aggregatetokens
        manage.context['message_tokens'] = manage.context['message_tokens'] + self.context.get('message_tokens')
        manage.context['answer_tokens'] = manage.context['answer_tokens'] + self.context.get('answer_tokens')

    @abstractmethod
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, chat_model: BaseChatModel = None,
                **kwargs):
        pass
