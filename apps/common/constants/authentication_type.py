# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： authentication_type.py
    @date：2023/11/14 20:03
    @desc:
"""
from enum import Enum


class AuthenticationType(Enum):
    # Ordinary Users
    USER = "USER"
    # Public access link
    APPLICATION_ACCESS_TOKEN = "APPLICATION_ACCESS_TOKEN"
    # key API
    API_KEY = "API_KEY"
