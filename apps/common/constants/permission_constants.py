"""
    @project: qabot
    @Author:The Tiger
    @file: permission_constants.py
    @date:2023/9/13 18:23
    @desc: Authority,The role Permanent
"""
from enum import Enum
from typing import List


class Group(Enum):
    """
    Authority Group A group usually corresponds to the front of a menu.
    """
    USER = "USER"

    DATASET = "DATASET"

    APPLICATION = "APPLICATION"

    SETTING = "SETTING"

    MODEL = "MODEL"

    TEAM = "TEAM"


class Operate(Enum):
    """
     Operating authority of a authority group
    """
    READ = 'READ'
    EDIT = "EDIT"
    CREATE = "CREATE"
    DELETE = "DELETE"
    """
    Authority of management
    """
    MANAGE = "MANAGE"
    """
    Use of permits
    """
    USE = "USE"


class RoleGroup(Enum):
    USER = 'USER'
    APPLICATION_KEY = "APPLICATION_KEY"
    APPLICATION_ACCESS_TOKEN = "APPLICATION_ACCESS_TOKEN"


class Role:
    def __init__(self, name: str, decs: str, group: RoleGroup):
        self.name = name
        self.decs = decs
        self.group = group


class RoleConstants(Enum):
    ADMIN = Role("Managers", "Managers,Preparation is currently not used.", RoleGroup.USER)
    USER = Role("Users", "All user permissions", RoleGroup.USER)
    APPLICATION_ACCESS_TOKEN = Role("Meeting", "Only the application session box interface permits.", RoleGroup.APPLICATION_ACCESS_TOKEN),
    APPLICATION_KEY = Role("Apply the private key.", "Apply the private key.", RoleGroup.APPLICATION_KEY)


class Permission:
    """
    Authority Information
    """

    def __init__(self, group: Group, operate: Operate, roles=None, dynamic_tag=None):
        if roles is None:
            roles = []
        self.group = group
        self.operate = operate
        self.roleList = roles
        self.dynamic_tag = dynamic_tag

    def __str__(self):
        return self.group.value + ":" + self.operate.value + (
            (":" + self.dynamic_tag) if self.dynamic_tag is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class PermissionConstants(Enum):
    """
     The authority.
    """
    USER_READ = Permission(group=Group.USER, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])
    USER_EDIT = Permission(group=Group.USER, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])
    USER_DELETE = Permission(group=Group.USER, operate=Operate.DELETE, roles=[RoleConstants.USER])

    DATASET_CREATE = Permission(group=Group.DATASET, operate=Operate.CREATE,
                                roles=[RoleConstants.ADMIN, RoleConstants.USER])

    DATASET_READ = Permission(group=Group.DATASET, operate=Operate.READ,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    DATASET_EDIT = Permission(group=Group.DATASET, operate=Operate.EDIT,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_READ = Permission(group=Group.APPLICATION, operate=Operate.READ,
                                  roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_CREATE = Permission(group=Group.APPLICATION, operate=Operate.CREATE,
                                    roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_DELETE = Permission(group=Group.APPLICATION, operate=Operate.DELETE,
                                    roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_EDIT = Permission(group=Group.APPLICATION, operate=Operate.EDIT,
                                  roles=[RoleConstants.ADMIN, RoleConstants.USER])

    SETTING_READ = Permission(group=Group.SETTING, operate=Operate.READ,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_READ = Permission(group=Group.MODEL, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_EDIT = Permission(group=Group.MODEL, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_DELETE = Permission(group=Group.MODEL, operate=Operate.DELETE,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])
    MODEL_CREATE = Permission(group=Group.MODEL, operate=Operate.CREATE,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_READ = Permission(group=Group.TEAM, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_CREATE = Permission(group=Group.TEAM, operate=Operate.CREATE, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_DELETE = Permission(group=Group.TEAM, operate=Operate.DELETE, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_EDIT = Permission(group=Group.TEAM, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])


def get_permission_list_by_role(role: RoleConstants):
    """
    According to the role Obtaining the right to match the role
    :param role: The role
    :return: Authority
    """
    return list(map(lambda k: PermissionConstants[k],
                    list(filter(lambda k: PermissionConstants[k].value.roleList.__contains__(role),
                                PermissionConstants.__members__))))


class Auth:
    """
     Storage of current users' roles and permissions
    """

    def __init__(self, role_list: List[RoleConstants], permission_list: List[PermissionConstants | Permission]
                 , client_id, client_type, current_role: RoleConstants, **keywords):
        self.role_list = role_list
        self.permission_list = permission_list
        self.client_id = client_id
        self.client_type = client_type
        self.keywords = keywords
        self.current_role = current_role


class CompareConstants(Enum):
    # or
    OR = "OR"
    # and
    AND = "AND"


class ViewPermission:
    def __init__(self, roleList: List[RoleConstants], permissionList: List[PermissionConstants | object],
                 compare=CompareConstants.OR):
        self.roleList = roleList
        self.permissionList = permissionList
        self.compare = compare
