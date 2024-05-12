from typing import List

from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework import status


class Page(dict):
    """
    Page Objects
    """

    def __init__(self, total: int, records: List, current_page: int, page_size: int, **kwargs):
        super().__init__(**{'total': total, 'records': records, 'current': current_page, 'size': page_size})


class Result(JsonResponse):
    """
     Connect to return objects.
    """

    def __init__(self, code=200, message="Successful", data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status, **kwargs)


def get_page_request_params(other_request_params=None):
    if other_request_params is None:
        other_request_params = []
    current_page = openapi.Parameter(name='current_page',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_INTEGER,
                                     required=True,
                                     description='Current page')

    page_size = openapi.Parameter(name='page_size',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_INTEGER,
                                  required=True,
                                  description='Size of each page.')
    result = [current_page, page_size]
    for other_request_param in other_request_params:
        result.append(other_request_param)
    return result


def get_page_api_response(response_data_schema: openapi.Schema):
    """
        Get the unification back. ReplyApi
    """
    return openapi.Responses(responses={200: openapi.Response(description="Response to Parameters",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="The response code",
                                                                          default=200,
                                                                          description="Successful:200 Failure:Other"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="The Tip",
                                                                          default='Successful',
                                                                          description="The wrong advice."),
                                                                      "data": openapi.Schema(
                                                                          type=openapi.TYPE_OBJECT,
                                                                          properties={
                                                                              'total': openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="Total number",
                                                                                  default=1,
                                                                                  description="Total number of data"),
                                                                              "records": openapi.Schema(
                                                                                  type=openapi.TYPE_ARRAY,
                                                                                  items=response_data_schema),
                                                                              "current": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="Current page",
                                                                                  default=1,
                                                                                  description="Current page"),
                                                                              "size": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="Size of each page.",
                                                                                  default=10,
                                                                                  description="Size of each page.")

                                                                          }
                                                                      )

                                                                  }
                                                              ),
                                                              )})


def get_api_response(response_data_schema: openapi.Schema):
    """
    Get the unification back. ReplyApi
    """
    return openapi.Responses(responses={200: openapi.Response(description="Response to Parameters",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="The response code",
                                                                          default=200,
                                                                          description="Successful:200 Failure:Other"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="The Tip",
                                                                          default='Successful',
                                                                          description="The wrong advice."),
                                                                      "data": response_data_schema

                                                                  }
                                                              ),
                                                              )})


def get_default_response():
    return get_api_response(openapi.Schema(type=openapi.TYPE_BOOLEAN))


def get_api_array_response(response_data_schema: openapi.Schema):
    """
    Get the unification back. ReplyApi
    """
    return openapi.Responses(responses={200: openapi.Response(description="Response to Parameters",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="The response code",
                                                                          default=200,
                                                                          description="Successful:200 Failure:Other"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="The Tip",
                                                                          default='Successful',
                                                                          description="The wrong advice."),
                                                                      "data": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                                             items=response_data_schema)

                                                                  }
                                                              ),
                                                              )})


def success(data, **kwargs):
    """
    Obtaining a Successful Reaction Object
    :param data: Interface Response Data
    :return: Reply to requests
    """
    return Result(data=data, **kwargs)


def error(message):
    """
    Obtaining a Failed Reaction Object
    :param message: The wrong advice.
    :return: Interface Response Objects
    """
    return Result(code=500, message=message)
