# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: I_base_chat_pipeline.py
    @date:2024/1/9 17:25
    @desc:
"""
import time
from abc import abstractmethod
from typing import Type

from rest_framework import serializers

from dataset.models import Paragraph


class ParagraphPipelineModel:

    def __init__(self, _id: str, document_id: str, dataset_id: str, content: str, title: str, status: str,
                 is_active: bool, comprehensive_score: float, similarity: float, dataset_name: str, document_name: str,
                 hit_handling_method: str, directly_return_similarity: float):
        self.id = _id
        self.document_id = document_id
        self.dataset_id = dataset_id
        self.content = content
        self.title = title
        self.status = status,
        self.is_active = is_active
        self.comprehensive_score = comprehensive_score
        self.similarity = similarity
        self.dataset_name = dataset_name
        self.document_name = document_name
        self.hit_handling_method = hit_handling_method
        self.directly_return_similarity = directly_return_similarity

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'dataset_id': self.dataset_id,
            'content': self.content,
            'title': self.title,
            'status': self.status,
            'is_active': self.is_active,
            'comprehensive_score': self.comprehensive_score,
            'similarity': self.similarity,
            'dataset_name': self.dataset_name,
            'document_name': self.document_name
        }

    class builder:
        def __init__(self):
            self.similarity = None
            self.paragraph = {}
            self.comprehensive_score = None
            self.document_name = None
            self.dataset_name = None
            self.hit_handling_method = None
            self.directly_return_similarity = 0.9

        def add_paragraph(self, paragraph):
            if isinstance(paragraph, Paragraph):
                self.paragraph = {'id': paragraph.id,
                                  'document_id': paragraph.document_id,
                                  'dataset_id': paragraph.dataset_id,
                                  'content': paragraph.content,
                                  'title': paragraph.title,
                                  'status': paragraph.status,
                                  'is_active': paragraph.is_active,
                                  }
            else:
                self.paragraph = paragraph
            return self

        def add_dataset_name(self, dataset_name):
            self.dataset_name = dataset_name
            return self

        def add_document_name(self, document_name):
            self.document_name = document_name
            return self

        def add_hit_handling_method(self, hit_handling_method):
            self.hit_handling_method = hit_handling_method
            return self

        def add_directly_return_similarity(self, directly_return_similarity):
            self.directly_return_similarity = directly_return_similarity
            return self

        def add_comprehensive_score(self, comprehensive_score: float):
            self.comprehensive_score = comprehensive_score
            return self

        def add_similarity(self, similarity: float):
            self.similarity = similarity
            return self

        def build(self):
            return ParagraphPipelineModel(str(self.paragraph.get('id')), str(self.paragraph.get('document_id')),
                                          str(self.paragraph.get('dataset_id')),
                                          self.paragraph.get('content'), self.paragraph.get('title'),
                                          self.paragraph.get('status'),
                                          self.paragraph.get('is_active'),
                                          self.comprehensive_score, self.similarity, self.dataset_name,
                                          self.document_name, self.hit_handling_method, self.directly_return_similarity)


class IBaseChatPipelineStep:
    def __init__(self):
        # The current step is down.,Storage of current step information
        self.context = {}

    @abstractmethod
    def get_step_serializer(self, manage) -> Type[serializers.Serializer]:
        pass

    def valid_args(self, manage):
        step_serializer_clazz = self.get_step_serializer(manage)
        step_serializer = step_serializer_clazz(data=manage.context)
        step_serializer.is_valid(raise_exception=True)
        self.context['step_args'] = step_serializer.data

    def run(self, manage):
        """

        :param manage:      Steps Manager
        :return: Execution Results
        """
        start_time = time.time()
        self.context['start_time'] = start_time
        # The exam parameters.,
        self.valid_args(manage)
        self._run(manage)
        self.context['run_time'] = time.time() - start_time

    def _run(self, manage):
        pass

    def execute(self, **kwargs):
        pass

    def get_details(self, manage, **kwargs):
        """
        Operating details.
        :return: Step details.
        """
        return None
