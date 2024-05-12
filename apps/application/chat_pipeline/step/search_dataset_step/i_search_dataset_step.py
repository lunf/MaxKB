# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： i_search_dataset_step.py
    @date：2024/1/9 18:10
    @desc: The knowledge base.
"""
import re
from abc import abstractmethod
from typing import List, Type

from django.core import validators
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from common.util.field_message import ErrMessage


class ISearchDatasetStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # Original question text.
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.char("The problem"))
        # System Complete Problems
        padding_problem_text = serializers.CharField(required=False, error_messages=ErrMessage.char("System Complete Problems"))
        # Datasets required for query.idList of
        dataset_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                error_messages=ErrMessage.list("The data collectionidList of"))
        # Documents required to be removed.id
        exclude_document_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                         error_messages=ErrMessage.list("Excluded documentsidList of"))
        # Need to eliminate the quantity.id
        exclude_paragraph_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                          error_messages=ErrMessage.list("Excluding the quantityidList of"))
        # Number of requests.
        top_n = serializers.IntegerField(required=True,
                                         error_messages=ErrMessage.integer("Reference to the number of points."))
        # similarity 0-1Between
        similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                            error_messages=ErrMessage.float("Reference to the number of points."))
        search_mode = serializers.CharField(required=True, validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message="Type only supports.register|reset_password", code=500)
        ], error_messages=ErrMessage.char("The search model."))

    def get_step_serializer(self, manage: PipelineManage) -> Type[InstanceSerializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        paragraph_list = self.execute(**self.context['step_args'])
        manage.context['paragraph_list'] = paragraph_list
        self.context['paragraph_list'] = paragraph_list

    @abstractmethod
    def execute(self, problem_text: str, dataset_id_list: list[str], exclude_document_id_list: list[str],
                exclude_paragraph_id_list: list[str], top_n: int, similarity: float, padding_problem_text: str = None,
                search_mode: str = None,
                **kwargs) -> List[ParagraphPipelineModel]:
        """
        About Users and Complete Problems explained: Repeat the question if there is to use the complementary question to investigate. Ask the original user question.
        :param similarity:                         Related
        :param top_n:                              How many requests.
        :param problem_text:                       User Problems
        :param dataset_id_list:                    Datasets required for query.idList of
        :param exclude_document_id_list:           Documents required to be removed.id
        :param exclude_paragraph_id_list:          It is necessary to exclude paragraphs.id
        :param padding_problem_text                Complete the problem.
        :param search_mode                         The search model.
        :return: List of paragraphs
        """
        pass
