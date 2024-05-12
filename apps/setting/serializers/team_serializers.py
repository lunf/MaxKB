# coding=utf-8
"""
    @project: qabot
    @Author：The Tiger
    @file： team_serializers.py
    @date：2023/9/5 16:32
    @desc:
"""
import itertools
import json
import os
import uuid
from typing import Dict, List

from django.core import cache
from django.db import transaction
from django.db.models import QuerySet, Q
from drf_yasg import openapi
from rest_framework import serializers

from common.constants.permission_constants import Operate
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.response.result import get_api_response
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from setting.models import TeamMember, TeamMemberPermission, Team
from smartdoc.conf import PROJECT_DIR
from users.models.user import User
from users.serializers.user_serializers import UserSerializer

user_cache = cache.caches['user_cache']


def get_response_body_api():
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'username', 'email', 'role', 'is_active', 'team_id', 'member_id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, title="Usersid", description="Usersid"),
            'username': openapi.Schema(type=openapi.TYPE_STRING, title="User Name", description="User Name"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, title="The mailbox", description="The mailbox address."),
            'role': openapi.Schema(type=openapi.TYPE_STRING, title="The role", description="The role"),
            'is_active': openapi.Schema(type=openapi.TYPE_STRING, title="Is Available", description="Is Available"),
            'team_id': openapi.Schema(type=openapi.TYPE_STRING, title="The teamid", description="The teamid"),
            'member_id': openapi.Schema(type=openapi.TYPE_STRING, title="Membersid", description="Membersid"),
        }
    )


class TeamMemberPermissionOperate(ApiMixin, serializers.Serializer):
    USE = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("Use of"))
    MANAGE = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("management"))

    def get_request_body_api(self):
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="Type of",
                              description="Operating authorityUSE,MANAGEAuthority",
                              properties={
                                  'USE': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                        title="Use of permits",
                                                        description="Use of permits True|False"),
                                  'MANAGE': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                           title="Authority of management",
                                                           description="Authority of management True|False")
                              }
                              )


class UpdateTeamMemberItemPermissionSerializer(ApiMixin, serializers.Serializer):
    target_id = serializers.CharField(required=True, error_messages=ErrMessage.char("The goalid"))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char("Type of Target"))
    operate = TeamMemberPermissionOperate(required=True, many=False)

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'type', 'operate'],
            properties={
                'target_id': openapi.Schema(type=openapi.TYPE_STRING, title="The knowledge base/Applicationsid",
                                            description="Knowledge Base or Applicationid"),
                'type': openapi.Schema(type=openapi.TYPE_STRING,
                                       title="Type of",
                                       description="DATASET|APPLICATION",
                                       ),
                'operate': TeamMemberPermissionOperate().get_request_body_api()
            }
        )


class UpdateTeamMemberPermissionSerializer(ApiMixin, serializers.Serializer):
    team_member_permission_list = UpdateTeamMemberItemPermissionSerializer(required=True, many=True)

    def is_valid(self, *, user_id=None):
        super().is_valid(raise_exception=True)
        permission_list = self.data.get("team_member_permission_list")
        illegal_target_id_list = select_list(
            get_file_content(
                os.path.join(PROJECT_DIR, "apps", "setting", 'sql', 'check_member_permission_target_exists.sql')),
            [json.dumps(permission_list), user_id, user_id])
        if illegal_target_id_list is not None and len(illegal_target_id_list) > 0:
            raise AppApiException(500, 'not existing. Applications|The knowledge baseid[' + str(illegal_target_id_list) + ']')

    def update_or_save(self, member_id: str):
        team_member_permission_list = self.data.get("team_member_permission_list")
        # Access to the database is permitted. To determine whether it is updated or added.
        team_member_permission_exist_list = QuerySet(TeamMemberPermission).filter(
            member_id=member_id)
        update_list = []
        save_list = []
        for item in team_member_permission_list:
            exist_list = list(
                filter(lambda use: str(use.target) == item.get('target_id'), team_member_permission_exist_list))
            if len(exist_list) > 0:
                exist_list[0].operate = list(
                    filter(lambda key: item.get('operate').get(key),
                           item.get('operate').keys()))
                update_list.append(exist_list[0])
            else:
                save_list.append(TeamMemberPermission(target=item.get('target_id'), auth_target_type=item.get('type'),
                                                      operate=list(
                                                          filter(lambda key: item.get('operate').get(key),
                                                                 item.get('operate').keys())),
                                                      member_id=member_id))
        # Mass Updates
        QuerySet(TeamMemberPermission).bulk_update(update_list, ['operate'])
        # Mass entrance.
        QuerySet(TeamMemberPermission).bulk_create(save_list)

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'team_member_permission_list':
                    openapi.Schema(type=openapi.TYPE_ARRAY, title="permission data",
                                   description="permission data",
                                   items=UpdateTeamMemberItemPermissionSerializer().get_request_body_api()
                                   ),
            }
        )


class TeamMemberSerializer(ApiMixin, serializers.Serializer):
    team_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("The teamid"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)

    @staticmethod
    def get_bach_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_ARRAY,
            title="UsersidList of",
            description="UsersidList of",
            items=openapi.Schema(type=openapi.TYPE_STRING)
        )

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username_or_email'],
            properties={
                'username_or_email': openapi.Schema(type=openapi.TYPE_STRING, title="User name or mailbox.",
                                                    description="User name or mailbox."),

            }
        )

    @transaction.atomic
    def batch_add_member(self, user_id_list: List[str], with_valid=True):
        """
        Adding members.
        :param user_id_list: UsersidList of
        :param with_valid:   is tested.
        :return:  List of Members
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        use_user_id_list = [str(u.id) for u in QuerySet(User).filter(id__in=user_id_list)]

        team_member_user_id_list = [str(team_member.user_id) for team_member in
                                    QuerySet(TeamMember).filter(team_id=self.data.get('team_id'))]
        team_id = self.data.get("team_id")
        create_team_member_list = [
            self.to_member_model(add_user_id, team_member_user_id_list, use_user_id_list, team_id) for add_user_id in
            user_id_list]
        QuerySet(TeamMember).bulk_create(create_team_member_list) if len(create_team_member_list) > 0 else None
        return TeamMemberSerializer(
            data={'team_id': self.data.get("team_id")}).list_member()

    def to_member_model(self, add_user_id, team_member_user_id_list, use_user_id_list, user_id):
        if use_user_id_list.__contains__(add_user_id):
            if team_member_user_id_list.__contains__(add_user_id) or user_id == add_user_id:
                raise AppApiException(500, "There are current members in the team.,Do not repeat adding.")
            else:
                return TeamMember(team_id=self.data.get("team_id"), user_id=add_user_id)
        else:
            raise AppApiException(500, "There are no users.")

    def add_member(self, username_or_email: str, with_valid=True):
        """
        Add a member.
        :param with_valid: Is the exam number?
        :param username_or_email: Add a member’s mailbox or user name
        :return: List of Members
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        if username_or_email is None:
            raise AppApiException(500, "User name or mailbox must be filled.")
        user = QuerySet(User).filter(
            Q(username=username_or_email) | Q(email=username_or_email)).first()
        if user is None:
            raise AppApiException(500, "There are no users.")
        if QuerySet(TeamMember).filter(Q(team_id=self.data.get('team_id')) & Q(user=user)).exists() or self.data.get(
                "team_id") == str(user.id):
            raise AppApiException(500, "There are current members in the team.,Do not repeat adding.")
        TeamMember(team_id=self.data.get("team_id"), user=user).save()
        return self.list_member(with_valid=False)

    def list_member(self, with_valid=True):
        """
        obtained List of members in the team
        :return: List of Members
        """
        if with_valid:
            self.is_valid(raise_exception=True)
        # Ordinary Members List
        member_list = list(map(lambda t: {"id": t.id, 'email': t.user.email, 'username': t.user.username,
                                          'team_id': self.data.get("team_id"), 'user_id': t.user.id,
                                          'type': 'member'},
                               QuerySet(TeamMember).filter(team_id=self.data.get("team_id"))))
        # Managers Members
        manage_member = QuerySet(User).get(id=self.data.get('team_id'))
        return [{'id': 'root', 'email': manage_member.email, 'username': manage_member.username,
                 'team_id': self.data.get("team_id"), 'user_id': manage_member.id, 'type': 'manage'
                 }, *member_list]

    def get_response_body_api(self):
        return get_api_response(openapi.Schema(
            type=openapi.TYPE_ARRAY, title="List of Members", description="List of Members",
            items=UserSerializer().get_response_body_api()
        ))

    class Operate(ApiMixin, serializers.Serializer):
        # The team Membersid
        member_id = serializers.CharField(required=True, error_messages=ErrMessage.char("Membersid"))
        # The teamid
        team_id = serializers.CharField(required=True, error_messages=ErrMessage.char("The teamid"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if self.data.get('member_id') != 'root' and not QuerySet(TeamMember).filter(
                    team_id=self.data.get('team_id'),
                    id=self.data.get('member_id')).exists():
                raise AppApiException(500, "Members that do not exist.,Please add members first.")

            return True

        def list_member_permission(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            team_id = self.data.get('team_id')
            member_id = self.data.get("member_id")
            # Find the permissions for all the knowledge bases and applications of current team members Attention operatefornullto establish authority. The default value isfalse
            member_permission_list = select_list(
                get_file_content(os.path.join(PROJECT_DIR, "apps", "setting", 'sql', 'get_member_permission.sql')),
                [team_id, team_id, (member_id if member_id != 'root' else uuid.uuid1())])

            # If you are a manager They have all powers. Prescribed value.
            if member_id == 'root':
                member_permission_list = list(
                    map(lambda row: {**row, 'operate': {Operate.USE.value: True, Operate.MANAGE.value: True}},
                        member_permission_list))
            # Divided by APPLICATION DATASETTwo groups.
            groups = itertools.groupby(
                sorted(list(map(lambda m: {**m, 'member_id': member_id,
                                           'operate': dict(
                                               map(lambda key: (key, True if m.get('operate') is not None and m.get(
                                                   'operate').__contains__(key) else False),
                                                   [Operate.USE.value, Operate.MANAGE.value]))},
                                member_permission_list)), key=lambda x: x.get('type')),
                key=lambda x: x.get('type'))
            return dict([(key, list(group)) for key, group in groups])

        def edit(self, member_permission: Dict):
            self.is_valid(raise_exception=True)
            member_id = self.data.get("member_id")
            if member_id == 'root':
                raise AppApiException(500, "The administrator authority does not allow modifications.")
            s = UpdateTeamMemberPermissionSerializer(data=member_permission)
            s.is_valid(user_id=self.data.get("team_id"))
            s.update_or_save(member_id)
            return self.list_member_permission(with_valid=False)

        def delete(self):
            """
            Removing Members
            :return:
            """
            self.is_valid(raise_exception=True)
            member_id = self.data.get("member_id")
            if member_id == 'root':
                raise AppApiException(500, "The team manager cannot be removed.")
            # Delete membership rights
            QuerySet(TeamMemberPermission).filter(member_id=member_id).delete()
            # Remove Members
            QuerySet(TeamMember).filter(id=member_id).delete()
            return True

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='member_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='Members of Teamid')]
