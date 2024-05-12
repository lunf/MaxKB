# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： data_set.py
    @date：2023/9/21 9:35
    @desc: The data collection
"""
import uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Status(models.TextChoices):
    """Type of Order"""
    embedding = 0, 'In the import.'
    success = 1, 'has completed'
    error = 2, 'Introduction Failure'


class Type(models.TextChoices):
    base = 0, 'General Types'

    web = 1, 'webType of site'


class HitHandlingMethod(models.TextChoices):
    optimization = 'optimization', 'Models optimized'
    directly_return = 'directly_return', 'Return directly.'


class DataSet(AppModelMixin):
    """
    The data collection
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    name = models.CharField(max_length=150, verbose_name="Name of data")
    desc = models.CharField(max_length=256, verbose_name="Database Description")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="The User")
    type = models.CharField(verbose_name='Type of', max_length=1, choices=Type.choices,
                            default=Type.base)

    meta = models.JSONField(verbose_name="The data", default=dict)

    class Meta:
        db_table = "dataset"


class Document(AppModelMixin):
    """
    The documentary
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150, verbose_name="Name of documentation")
    char_length = models.IntegerField(verbose_name="Number of documents. The remaining field.")
    status = models.CharField(verbose_name='state of', max_length=1, choices=Status.choices,
                              default=Status.embedding)
    is_active = models.BooleanField(default=True)

    type = models.CharField(verbose_name='Type of', max_length=1, choices=Type.choices,
                            default=Type.base)
    hit_handling_method = models.CharField(verbose_name='Method of Treatment', max_length=20,
                                           choices=HitHandlingMethod.choices,
                                           default=HitHandlingMethod.optimization)

    meta = models.JSONField(verbose_name="The data", default=dict)

    class Meta:
        db_table = "document"


class Paragraph(AppModelMixin):
    """
    Table of paragraphs
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=4096, verbose_name="Contents of paragraph")
    title = models.CharField(max_length=256, verbose_name="The title", default="")
    status = models.CharField(verbose_name='state of', max_length=1, choices=Status.choices,
                              default=Status.embedding)
    hit_num = models.IntegerField(verbose_name="Number of fate.", default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "paragraph"


class Problem(AppModelMixin):
    """
    The question table
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="The content of the question")
    hit_num = models.IntegerField(verbose_name="Number of fate.", default=0)

    class Meta:
        db_table = "problem"


class ProblemParagraphMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING, db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        db_table = "problem_paragraph_mapping"


class Image(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    image = models.BinaryField(verbose_name="Image data")
    image_name = models.CharField(max_length=256, verbose_name="Name of image", default="")

    class Meta:
        db_table = "image"
