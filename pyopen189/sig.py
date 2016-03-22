#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import hashlib
import hmac

import six

from .util import force_binary


def transform_payload(d):
    '''Transforms payload for request signature generation.

    Meant for internal use; don't call this manually.

        >>> from __future__ import print_function, unicode_literals
        >>> import six
        >>> s = transform_payload({'k1': 'v1', 'k2': 'v2', 'k3': 'v3', })
        >>> isinstance(s, six.binary_type)
        True
        >>> print(s)
        k1=v1&k2=v2&k3=v3

    '''

    params = []

    keys = [force_binary(k) for k in six.iterkeys(d)]
    keys.sort()

    for k_bin in keys:
        v_bin = force_binary(d[k_bin])

        params.append(b'%s=%s' % (k_bin, v_bin))

    return b'&'.join(params)


def sign(d, secret):
    '''Generates signature for the given payload and app secret.

    Meant for internal use; don't call this manually.

        >>> from __future__ import print_function, unicode_literals
        >>> payload = {'k1': 'v1', 'k2': 'v2', 'k3': 'v3', }
        >>> print(sign(payload, b'012345'))
        8802a919bf62f04298f2ae073df88c75f6f6ece3

    '''

    payload = transform_payload(d)

    # NOTE: secret is expected to be binary
    return base64.b64encode(hmac.new(secret, payload, hashlib.sha1).digest())
