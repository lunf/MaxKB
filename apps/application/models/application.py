# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： application.py
    @date：2023/9/25 14:24
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from langchain.schema import HumanMessage, AIMessage

from common.mixins.app_model_mixin import AppModelMixin
from dataset.models.data_set import DataSet
from setting.models.model_management import Model
from users.models import User


def get_dataset_setting_dict():
    return {'top_n': 3, 'similarity': 0.6, 'max_paragraph_char_number': 5000, 'search_mode': 'embedding',
            'no_references_setting': {
                'status': 'ai_questioning',
                'value': '{question}'
            }}


def get_model_setting_dict():
    return {'prompt': Application.get_default_model_prompt()}


class Application(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    name = models.CharField(max_length=128, verbose_name="Application Name")
    desc = models.CharField(max_length=512, verbose_name="Citation of description", default="")
    prologue = models.CharField(max_length=1024, verbose_name="Opening White.", default="")
    dialogue_number = models.IntegerField(default=0, verbose_name="Number of meetings")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    dataset_setting = models.JSONField(verbose_name="Set up the data set.", default=get_dataset_setting_dict)
    model_setting = models.JSONField(verbose_name="Model parameters related settings", default=get_model_setting_dict)
    problem_optimization = models.BooleanField(verbose_name="Problems optimized", default=False)
    icon = models.CharField(max_length=256, verbose_name="Applicationsicon", default="/ui/favicon.ico")

    @staticmethod
    def get_default_model_prompt():
        return ('known information：'
                '\n{data}'
                '\nReply to Request：'
                '\n- If you don’t know the answer or don’t get the answer.，Please answer“No information found in the knowledge base.，Consulting relevant technical support or reference to official documents for operation”。'
                '\n- Avoid mention that you are from<data></data>Knowledge obtained in。'
                '\n- Please keep the answer and<data></data>The description is consistent.。'
                '\n- Please usemarkdown Optimization of Answer Formats。'
                '\n- <data></data>The image link.、Link address and script language please return.。'
                '\n- Please use the same language to answer the question.。'
                '\nThe problem：'
                '\n{question}')

    class Meta:
        db_table = "application"


class ApplicationDatasetMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)

    class Meta:
        db_table = "application_dataset_mapping"


class Chat(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    abstract = models.CharField(max_length=1024, verbose_name="The summary")
    client_id = models.UUIDField(verbose_name="The clientid", default=None, null=True)

    class Meta:
        db_table = "application_chat"


class VoteChoices(models.TextChoices):
    """Type of Order"""
    UN_VOTE = -1, 'not voted.'
    STAR = 0, 'agreed'
    TRAMPLE = 1, 'opposed'


class ChatRecord(AppModelMixin):
    """
    Dialogues Details
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    vote_status = models.CharField(verbose_name='Voting', max_length=10, choices=VoteChoices.choices,
                                   default=VoteChoices.UN_VOTE)
    problem_text = models.CharField(max_length=1024, verbose_name="The problem")
    answer_text = models.CharField(max_length=40960, verbose_name="The Answer")
    message_tokens = models.IntegerField(verbose_name="requestedtokenNumber of", default=0)
    answer_tokens = models.IntegerField(verbose_name="ReplytokenNumber of", default=0)
    const = models.IntegerField(verbose_name="Total costs", default=0)
    details = models.JSONField(verbose_name="Details of Dialogue", default=dict)
    improve_paragraph_id_list = ArrayField(verbose_name="Improve the list of notes",
                                           base_field=models.UUIDField(max_length=128, blank=True)
                                           , default=list)
    run_time = models.FloatField(verbose_name="Working long.", default=0)
    index = models.IntegerField(verbose_name="The dialogue.")

    def get_human_message(self):
        if 'problem_padding' in self.details:
            return HumanMessage(content=self.details.get('problem_padding').get('padding_problem_text'))
        return HumanMessage(content=self.problem_text)

    def get_ai_message(self):
        return AIMessage(content=self.answer_text)

    class Meta:
        db_table = "application_chat_record"
