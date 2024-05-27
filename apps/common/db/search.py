# coding=utf-8
"""
    @project: maxkb
    @Author:The Tiger
    @file: search.py
    @date:2023/10/7 18:20
    @desc:
"""
from typing import Dict, Any

from django.db import DEFAULT_DB_ALIAS, models, connections
from django.db.models import QuerySet

from common.db.compiler import AppSQLCompiler
from common.db.sql_execute import select_one, select_list
from common.response.result import Page


def get_dynamics_model(attr: dict, table_name='dynamics'):
    """
    Get a dynamic.djangoThe model
    :param attr:       Model Fields
    :param table_name: Name of
    :return: django The model
    """
    attributes = {
        "__module__": "dataset.models",
        "Meta": type("Meta", (), {'db_table': table_name}),
        **attr
    }
    return type('Dynamics', (models.Model,), attributes)


def generate_sql_by_query_dict(queryset_dict: Dict[str, QuerySet], select_string: str,
                               field_replace_dict: None | Dict[str, Dict[str, str]] = None, with_table_name=False):
    """
    produced The querysql
    :param with_table_name:
    :param queryset_dict: Multiple conditions Conditions of Question
    :param select_string: The querysql
    :param field_replace_dict:  Requirements to replace polls.,There is no need to enter if there is a special need to enter.
    :return: sql:Required inquiry.sql params: sql Parameters
    """

    params_dict: Dict[int, Any] = {}
    result_params = []
    for key in queryset_dict.keys():
        value = queryset_dict.get(key)
        sql, params = compiler_queryset(value, None if field_replace_dict is None else field_replace_dict.get(key),
                                        with_table_name)
        params_dict = {**params_dict, select_string.index("${" + key + "}"): params}
        select_string = select_string.replace("${" + key + "}", sql)

    for key in sorted(list(params_dict.keys())):
        result_params = [*result_params, *params_dict.get(key)]
    return select_string, result_params


def generate_sql_by_query(queryset: QuerySet, select_string: str,
                          field_replace_dict: None | Dict[str, str] = None, with_table_name=False):
    """
    produced The querysql
    :param queryset:            Conditions of Question
    :param select_string:       Primarysql
    :param field_replace_dict:  Requirements to replace polls.,There is no need to enter if there is a special need to enter.
    :return:  sql:Required inquiry.sql params: sql Parameters
    """
    sql, params = compiler_queryset(queryset, field_replace_dict, with_table_name)
    return select_string + " " + sql, params


def compiler_queryset(queryset: QuerySet, field_replace_dict: None | Dict[str, str] = None, with_table_name=False):
    """
    Analysis querysetQuestion of objects.
    :param with_table_name:
    :param queryset:            Question of objects.
    :param field_replace_dict:  Requirements to replace polls.,There is no need to enter if there is a special need to enter.
    :return: sql:Required inquiry.sql params: sql Parameters
    """
    q = queryset.query
    compiler = q.get_compiler(DEFAULT_DB_ALIAS)
    if field_replace_dict is None:
        field_replace_dict = get_field_replace_dict(queryset)
    app_sql_compiler = AppSQLCompiler(q, using=DEFAULT_DB_ALIAS, connection=compiler.connection,
                                      field_replace_dict=field_replace_dict)
    sql, params = app_sql_compiler.get_query_str(with_table_name=with_table_name)
    return sql, params


def native_search(queryset: QuerySet | Dict[str, QuerySet], select_string: str,
                  field_replace_dict: None | Dict[str, Dict[str, str]] | Dict[str, str] = None,
                  with_search_one=False, with_table_name=False):
    """
    Complex inquiries
    :param with_table_name:     producedsqlIncludes the name.
    :param queryset:            Conducting Conditions Constructor
    :param select_string:       Inquiry in advance Not included where limit Wait for information
    :param field_replace_dict:  Fields needed to be replaced.
    :param with_search_one:     The query
    :return: Search Results
    """
    if isinstance(queryset, Dict):
        exec_sql, exec_params = generate_sql_by_query_dict(queryset, select_string, field_replace_dict, with_table_name)
    else:
        exec_sql, exec_params = generate_sql_by_query(queryset, select_string, field_replace_dict, with_table_name)
    if with_search_one:
        return select_one(exec_sql, exec_params)
    else:
        return select_list(exec_sql, exec_params)


def page_search(current_page: int, page_size: int, queryset: QuerySet, post_records_handler):
    """
    Page search.
    :param current_page:         Current page
    :param page_size:            Size of each page.
    :param queryset:             Conditions of Question
    :param post_records_handler: Data Processor
    :return:  Page Results
    """
    total = QuerySet(query=queryset.query.clone(), model=queryset.model).count()
    result = queryset.all()[((current_page - 1) * page_size):(current_page * page_size)]
    return Page(total, list(map(post_records_handler, result)), current_page, page_size)


def native_page_search(current_page: int, page_size: int, queryset: QuerySet | Dict[str, QuerySet], select_string: str,
                       field_replace_dict=None,
                       post_records_handler=lambda r: r,
                       with_table_name=False):
    """
    Complex page queries.
    :param with_table_name:
    :param current_page:          Current page
    :param page_size:             Size of each page.
    :param queryset:              Conditions of Question
    :param select_string:         The query
    :param field_replace_dict:    Special field replacement.
    :param post_records_handler:  The datarowProcessor
    :return: Page Results
    """
    if isinstance(queryset, Dict):
        exec_sql, exec_params = generate_sql_by_query_dict(queryset, select_string, field_replace_dict, with_table_name)
    else:
        exec_sql, exec_params = generate_sql_by_query(queryset, select_string, field_replace_dict, with_table_name)
    total_sql = "SELECT \"count\"(*) FROM (%s) temp" % exec_sql
    total = select_one(total_sql, exec_params)
    limit_sql = connections[DEFAULT_DB_ALIAS].ops.limit_offset_sql(
        ((current_page - 1) * page_size), (current_page * page_size)
    )
    page_sql = exec_sql + " " + limit_sql
    result = select_list(page_sql, exec_params)
    return Page(total.get("count"), list(map(post_records_handler, result)), current_page, page_size)


def get_field_replace_dict(queryset: QuerySet):
    """
    Find the fields needed to be replaced. presumed “xxx.xxx”Need to be replaced. “xxx”."xxx"
    :param queryset: Question of objects.
    :return: The dictionary needs to be replaced.
    """
    result = {}
    for field in queryset.model._meta.local_fields:
        if field.attname.__contains__("."):
            replace_field = to_replace_field(field.attname)
            result.__setitem__('"' + field.attname + '"', replace_field)
    return result


def to_replace_field(field: str):
    """
    willfield Convert to Need to be replaced.field  “xxx.xxx”Need to be replaced. “xxx”."xxx" Just replaced. fieldIncluded.The field.
    :param field: django fieldFields
    :return: Replace the field.
    """
    split_field = field.split(".")
    return ".".join(list(map(lambda sf: '"' + sf + '"', split_field)))
