#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import datetime
import os

import six
import pytz

OPEN189_TZ = pytz.timezone('Asia/Shanghai')


def force_binary(s, enc='utf-8'):
    '''Forces the input parameter into binary type of current Python. The input
    parameter is assumed to be either str or unicode.

    >>> from __future__ import unicode_literals
    >>> import six
    >>> isinstance(force_binary('abc'), six.binary_type)
    True
    >>> isinstance(force_binary(b'abc'), six.binary_type)
    True

    '''

    if isinstance(s, six.binary_type):
        return s
    return s.encode(enc)


def get_timestamp():
    '''Generates a timestamp suitable for the open.189.cn platform.'''

    # NOTE: it seems the platform implicitly requires a timestamp in
    # Asia/Shanghai, as the documentation made no mention of timezones.
    dt = OPEN189_TZ.localize(datetime.datetime.now())
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_random_state_str():
    '''Generates a (sufficiently) random string for tracking OAuth requests.'''

    return base64.b64encode(os.urandom(30))
