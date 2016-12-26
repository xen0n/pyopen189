#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
try:
    from typing import Any, AnyStr, Text, MutableMapping, Optional, Union
except ImportError:
    pass

import six
import requests

from . import sig
from . import util

__version__ = '0.4.dev0'


class Open189Error(RuntimeError):
    def __init__(self, status_code, res_code, message):
        # type: (int, int, Text) -> None
        msg = '[HTTP {} res_code {}] {}'.format(status_code, res_code, message)
        super(Open189Error, self).__init__(msg)
        self.status_code = status_code
        self.res_code = res_code


def _process_response(res):
    # type: (requests.models.Response) -> Any
    '''Processes the API response, raising exception if that's the case.'''

    result = res.json()
    res_code = int(result.get('res_code', -1))  # fxxk this can be string
    if res.status_code != 200 or res_code != 0:
        raise Open189Error(
                res.status_code,
                res_code,
                result.get('res_message', None),
                )

    return result


class Open189App(object):
    '''SDK client for the open.189.cn platform.'''

    def __init__(self, app_id, secret, access_token=None):
        # type: (AnyStr, AnyStr, AnyStr) -> None
        self._app_id = util.force_binary(app_id)  # type: bytes
        self._secret = util.force_binary(secret)  # type: bytes
        if access_token is not None:
            self._access_token = util.force_binary(access_token)  # type: Optional[bytes]
        else:
            self._access_token = None  # type: Optional[bytes]

    @property
    def app_id(self):
        # type: () -> bytes
        return self._app_id

    @property
    def secret(self):
        # type: () -> bytes
        return self._secret

    @property
    def access_token(self):
        # type: () -> Optional[bytes]
        return self._access_token

    @access_token.setter
    def access_token(self, v):
        # type: (AnyStr) -> None
        self._access_token = util.force_binary(v)  # type: Optional[bytes]

    def _prepare_request_params(self, params):
        # type: (dict) -> dict
        '''Prepares request parameters for sending (not needed for OAuth
        requests).

        Note that the method is destructive; the parameters dict is modified
        along the way. Since the params dict is never meant to be re-used, this
        is considered somewhat acceptable.

        '''

        params['app_id'] = self.app_id
        # NOTE: requests wouldn't add the field if value is None, so we can
        # blindly pass the value.
        params['access_token'] = self.access_token
        params['timestamp'] = util.get_timestamp()

        # sign the request
        sign = sig.sign(params, self.secret)
        params['sign'] = sign

        return params

    def _perform_get_sync(self, url, params, prepare=True):
        # type: (Text, dict, bool) -> Any
        '''Performs a blocking API GET request to the specified endpoint with
        the specified parameters, raising exceptions appropriately.'''

        data = self._prepare_request_params(params) if prepare else params
        return _process_response(requests.get(url, params=data))

    def _perform_post_sync(self, url, params, prepare=True):
        # type: (Text, dict, bool) -> Any
        '''Performs a blocking API POST request to the specified endpoint with
        the specified parameters, raising exceptions appropriately.'''

        data = self._prepare_request_params(params) if prepare else params
        return _process_response(requests.post(url, data=data))

    def _perform_access_token_req(self, **kwargs):
        # type: (**Union[bytes, str]) -> Any
        kwargs['app_id'] = self.app_id
        kwargs['app_secret'] = self.secret
        kwargs['state'] = util.get_random_state_str()

        return self._perform_post_sync(
                'https://oauth.api.189.cn/emp/oauth2/v3/access_token',
                kwargs,
                False,
                )

    def get_access_token_ac(self, code, redirect_uri):
        # type: (AnyStr, AnyStr) -> Any
        '''Gets an access token with the Authorization Code flow.

        Access token parameter is ignored.

        '''

        return self._perform_access_token_req(
                grant_type='authorization_code',
                code=code,
                redirect_uri=redirect_uri,
                )

    def get_access_token_cc(self):
        # type: () -> Any
        '''Gets a user-independent access token with the Client Credentials
        flow.

        Access token parameter is ignored.

        '''

        return self._perform_access_token_req(
                grant_type='client_credentials',
                )

    def refresh_access_token(self, refresh_token):
        # type: (AnyStr) -> Any
        '''Refresh access token using a previously returned refresh token.

        Access token parameter is ignored.

        '''

        return self._perform_access_token_req(
                grant_type='refresh_token',
                refresh_token=refresh_token,
                )

    def sms_get_token(self):
        # type: () -> Any
        '''Gets a token for sending verification SMS.

        Access token is required.

        '''

        return self._perform_get_sync(
                'http://api.189.cn/v2/dm/randcode/token',
                {},
                )

    def sms_send_verification_sms(
            self,
            token,  # type: AnyStr
            phone,  # type: AnyStr
            code=None,  # type: AnyStr
            callback_url=None,  # type: AnyStr
            exp_time_min=None,  # type: int
            ):
        # type: (...) -> Any
        '''Sends a verification SMS to the specified phone.

        Needs a token obtained with :meth:`sms_get_token`. Expiry time is in
        minutes; defaults to 5 minutes if not specified.

        The platform supports both platform-generated and custom verification
        codes. For the platform to generate the code for you, set the code
        parameter to ``None`` and provide a callback URL for receiving the
        generated code. Otherwise a string comprised of 6 digits must be
        provided, and the callback URL is ignored.

        Access token is required.

        '''

        params = {
                'token': token,
                'phone': phone,
                }
        if exp_time_min is not None:
            params['exp_time'] = str(exp_time_min)

        if code is None:
            if callback_url is None:
                raise ValueError(
                        'callback URL is required for platform-generated '
                        'verification code'
                        )

            endpoint = 'http://api.189.cn/v2/dm/randcode/send'
            params['url'] = callback_url
        else:
            if len(code) != 6 or not code.isdigit():
                raise ValueError('only 6-digit string code is supported')

            endpoint = 'http://api.189.cn/v2/dm/randcode/sendSms'
            params['randcode'] = code

        return self._perform_post_sync(
                endpoint,
                params,
                )

    def sms_send_template(self, phone, template_id, template_params):
        # type: (AnyStr, AnyStr, object) -> Any
        '''Sends a template SMS to the specified phone.

        Access token is required.

        '''

        template_params_json = util.json_dumps_compact(template_params)
        params = {
                'acceptor_tel': phone,
                'template_id': template_id,
                'template_param': template_params_json,
                }

        return self._perform_post_sync(
                'http://api.189.cn/v2/emp/templateSms/sendSms',
                params,
                )
