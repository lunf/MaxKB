# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： embedding.py
    @date：2023/9/21 15:46
    @desc:
"""
from django.db import models

from common.field.vector_field import VectorField
from dataset.models.data_set import Document, Paragraph, DataSet
from django.contrib.postgres.search import SearchVectorField


class SourceType(models.TextChoices):
    """Type of Order"""
    PROBLEM = 0, 'The problem'
    PARAGRAPH = 1, 'Paragraphs'
    TITLE = 2, 'The title'


class SearchMode(models.TextChoices):
    embedding = 'embedding'
    keywords = 'keywords'
    blend = 'blend'


class Embedding(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name="The key.id")

    source_id = models.CharField(max_length=128, verbose_name="Resourcesid")

    source_type = models.CharField(verbose_name='Type of Resource', max_length=5, choices=SourceType.choices,
                                   default=SourceType.PROBLEM)

    is_active = models.BooleanField(verbose_name="Is Available", max_length=1, default=True)

    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, verbose_name="Related Documents", db_constraint=False)

    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, verbose_name="Related Documents", db_constraint=False)

    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, verbose_name="Paragraphs related", db_constraint=False)

    embedding = VectorField(verbose_name="The quantity")

    search_vector = SearchVectorField(verbose_name="The word", default="")

    meta = models.JSONField(verbose_name="The data", default=dict)

    class Meta:
        db_table = "embedding"
        unique_together = ['source_id', 'source_type']
