# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： i_generate_human_message_step.py
    @date：2024/1/9 18:15
    @desc: Create a dialogue template.
"""
from abc import abstractmethod
from typing import Type, List

from langchain.schema import BaseMessage
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.models import ChatRecord
from application.serializers.application_serializers import NoReferencesSetting
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class IGenerateHumanMessageStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # The problem
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.char("The problem"))
        # List of paragraphs
        paragraph_list = serializers.ListField(child=InstanceField(model_type=ParagraphPipelineModel, required=True),
                                               error_messages=ErrMessage.list("List of paragraphs"))
        # History Answer
        history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                    error_messages=ErrMessage.list("History Answer"))
        # The number of conversations.
        dialogue_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("The number of conversations."))
        # Maximum carrying knowledge base paragraph length
        max_paragraph_char_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer(
            "Maximum carrying knowledge base paragraph length"))
        # The template
        prompt = serializers.CharField(required=True, error_messages=ErrMessage.char("Suggestions"))
        # Complete the problem.
        padding_problem_text = serializers.CharField(required=False, error_messages=ErrMessage.char("Complete the problem."))
        # No queries for reference.
        no_references_setting = NoReferencesSetting(required=True, error_messages=ErrMessage.base("No reference to setup."))

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        message_list = self.execute(**self.context['step_args'])
        manage.context['message_list'] = message_list

    @abstractmethod
    def execute(self,
                problem_text: str,
                paragraph_list: List[ParagraphPipelineModel],
                history_chat_record: List[ChatRecord],
                dialogue_number: int,
                max_paragraph_char_number: int,
                prompt: str,
                padding_problem_text: str = None,
                no_references_setting=None,
                **kwargs) -> List[BaseMessage]:
        """

        :param problem_text:               Original question text.
        :param paragraph_list:             List of paragraphs
        :param history_chat_record:        History of Dialogue
        :param dialogue_number:            The number of conversations.
        :param max_paragraph_char_number:  The maximum length.
        :param prompt:                     The template
        :param padding_problem_text        Users modify text
        :param kwargs:                     Other parameters
        :param no_references_setting:     No reference to setup.
        :return:
        """
        pass
