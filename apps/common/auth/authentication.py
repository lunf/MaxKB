# coding=utf-8
"""
    @project: qabot
    @Author:The Tiger
    @file: authentication.py
    @date:2023/9/13 15:00
    @desc: the authority
"""
from typing import List

from common.constants.permission_constants import ViewPermission, CompareConstants, RoleConstants, PermissionConstants, \
    Permission
from common.exception.app_exception import AppUnauthorizedFailed


def exist_permissions_by_permission_constants(user_permission: List[PermissionConstants],
                                              permission_list: List[PermissionConstants]):
    """
    The user possesses permission_listof authority.
    :param user_permission:  User permits
    :param permission_list:  The required authority.
    :return: Is it possessed
    """
    return any(list(map(lambda up: permission_list.__contains__(up), user_permission)))


def exist_role_by_role_constants(user_role: List[RoleConstants],
                                 role_list: List[RoleConstants]):
    """
    Does the user have this role?
    :param user_role: User role
    :param role_list: The role you need.
    :return:  Is it possessed
    """
    return any(list(map(lambda up: role_list.__contains__(up), user_role)))


def exist_permissions_by_view_permission(user_role: List[RoleConstants],
                                         user_permission: List[PermissionConstants | object],
                                         permission: ViewPermission, request, **kwargs):
    """
    Does the user have these permissions?
    :param request:
    :param user_role:        User role
    :param user_permission:  User permits
    :param permission:       Authority that belongs
    :return:                 Is there existing True False
    """
    role_ok = any(list(map(lambda ur: permission.roleList.__contains__(ur), user_role)))
    permission_list = [user_p(request, kwargs) if callable(user_p) else user_p for user_p in
                       permission.permissionList
                       ]
    permission_ok = any(list(map(lambda up: permission_list.__contains__(up),
                                 user_permission)))
    return role_ok | permission_ok if permission.compare == CompareConstants.OR else role_ok & permission_ok


def exist_permissions(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request,
                      **kwargs):
    if isinstance(permission, ViewPermission):
        return exist_permissions_by_view_permission(user_role, user_permission, permission, request, **kwargs)
    elif isinstance(permission, RoleConstants):
        return exist_role_by_role_constants(user_role, [permission])
    elif isinstance(permission, PermissionConstants):
        return exist_permissions_by_permission_constants(user_permission, [permission])
    elif isinstance(permission, Permission):
        return user_permission.__contains__(permission)
    return False


def exist(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request, **kwargs):
    if callable(permission):
        p = permission(request, kwargs)
        return exist_permissions(user_role, user_permission, p, request)
    else:
        return exist_permissions(user_role, user_permission, permission, request, **kwargs)


def has_permissions(*permission, compare=CompareConstants.OR):
    """
    Authority role or permission
    :param compare:    compared symbols.
    :param permission: If it is a role role:roleId
    :return: Authorization of the decorator function.,To determine whether the user has access to the current interface.
    """

    def inner(func):
        def run(view, request, **kwargs):
            exit_list = list(
                map(lambda p: exist(request.auth.role_list, request.auth.permission_list, p, request, **kwargs),
                    permission))
            # Deciding whether there is authority.
            if any(exit_list) if compare == CompareConstants.OR else all(exit_list):
                return func(view, request, **kwargs)
            else:
                raise AppUnauthorizedFailed(403, "No access permission.")

        return run

    return inner
