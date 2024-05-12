# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： sql_execute.py
    @date：2023/9/25 20:05
    @desc:
"""
from typing import List

from django.db import connection


def sql_execute(sql: str, params):
    """
    executing one.sql
    :param sql:     Needed to execute.sql
    :param params:  sqlParameters
    :return:        Execution Results
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = list(map(lambda d: d.name, cursor.description))
        res = cursor.fetchall()
        result = list(map(lambda row: dict(list(zip(columns, row))), res))
        cursor.close()
        return result


def update_execute(sql: str, params):
    """
      executing one.sql
      :param sql:     Needed to execute.sql
      :param params:  sqlParameters
      :return:        Execution Results
      """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        cursor.close()
        return None


def select_list(sql: str, params: List):
    """
    Executionsql Ask for list data
    :param sql:     Needed to execute.sql
    :param params:  sqlThe parameters.
    :return: Search Results
    """
    result_list = sql_execute(sql, params)
    if result_list is None:
        return []
    return result_list


def select_one(sql: str, params: List):
    """
    Executionsql Ask for a data.
    :param sql:     Needed to execute.sql
    :param params:  Parameters
    :return: Search Results
    """
    result_list = sql_execute(sql, params)
    if result_list is None or len(result_list) == 0:
        return None
    return result_list[0]
