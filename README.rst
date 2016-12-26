Unofficial Python client for open.189.cn (天翼开放平台)
=======================================================

License
-------

BSD-licensed


Implemented features
--------------------

* Access token requests
    - Authorization Code flow
    - Client Credentials flow
    - Refreshing
* SMS capabilities
    - SMS token request
    - Verification code sending; both platform- and self-generated codes supported
    - Template SMS sending


Example usage
-------------

First obtain an access token for the API. Note that you should **never**
attempt to get a token for *every request*, write a simple dedicated daemon
or use a cronjob for that instead::

    >>> import pyopen189
    >>> client = pyopen189.Open189App('your_app_id', 'your_app_secret')
    >>> at = client.get_access_token_cc()
    >>> at
    {'access_token': '<your-new-access-token>',
     'expires_in': 2592000,
     'res_code': '0',
     'res_message': 'Success',
     'state': 'p5RXKOQTelgHz+PE3zRoVl0fImmGR4G4s+K9Hq+r'}
    >>> # write the access token somewhere for your backend to pick up

Then transmit the token to your webapp backend somehow (Redis, sticky MQ message,
plain tempfile or anything, you name it). Now you can send your messages!

::

    >>> import pyopen189
    >>> at = fetch_access_token()  # get your AT from your token service
    >>> client = pyopen189.Open189App('your_app_id', 'your_app_secret', at)
    >>> sms_token = client.sms_get_token()
    >>> sms_token
    {'res_code': 0, 'token': '<some-random-token-here>'}
    >>> client.sms_send_verification_sms(
    ...         sms_token['token'],
    ...         '<your_phone_number>',
    ...         '456788',
    ...         exp_time_min=15,
    ...         )
    ...
    {'create_at': '1482752850', 'identifier': 'Gn0331', 'res_code': 0}
    >>> # now check your SMS inbox!


TODO features
-------------

All the remaining endpoints ;-) Pull requests are welcome.
