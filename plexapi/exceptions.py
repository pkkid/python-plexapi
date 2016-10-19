# -*- coding: utf-8 -*-
# flake8:noqa
"""
PlexAPI Exceptions
"""

class PlexApiException(Exception):
    pass

class BadRequest(PlexApiException):
    pass

class NotFound(PlexApiException):
    pass

class UnknownType(PlexApiException):
    pass

class Unsupported(PlexApiException):
    pass

class Unauthorized(PlexApiException):
    pass
