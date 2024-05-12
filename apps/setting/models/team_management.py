# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： team_management.py
    @date：2023/9/25 15:04
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.constants.permission_constants import Group, Operate
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class AuthTargetType(models.TextChoices):
    """Authorized objectives"""
    DATASET = Group.DATASET.value, 'The data collection'
    APPLICATION = Group.APPLICATION.value, 'Applications'


class AuthOperate(models.TextChoices):
    """authorized authority"""
    MANAGE = Operate.MANAGE.value, 'management'

    USE = Operate.USE.value, "Use of"


class Team(AppModelMixin):
    """
    The Team Table
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.DO_NOTHING, verbose_name="The team owners.")

    name = models.CharField(max_length=128, verbose_name="The Team Name")

    class Meta:
        db_table = "team"


class TeamMember(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, verbose_name="The teamid")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Member Usersid")

    class Meta:
        db_table = "team_member"


class TeamMemberPermission(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="The key.id")
    """
    Members of the team.
    """
    member = models.ForeignKey(TeamMember, on_delete=models.DO_NOTHING, verbose_name="Members of Team")

    auth_target_type = models.CharField(verbose_name='Authorized objectives', max_length=128, choices=AuthTargetType.choices,
                                        default=AuthTargetType.DATASET)

    target = models.UUIDField(max_length=128, verbose_name="The data collection/Applicationsid")

    operate = ArrayField(verbose_name="Authorization operating list",
                         base_field=models.CharField(max_length=256,
                                                     blank=True,
                                                     choices=AuthOperate.choices,
                                                     default=AuthOperate.USE),
                         )

    class Meta:
        db_table = "team_member_permission"
