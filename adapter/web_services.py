"""
Module: web_services

This module defines classes for interacting with various external web services
such as CSC Web Service, token generation, Google reCAPTCHA validation,
CloudFlare interaction, OAuth authentication with Google, Facebook, and Apple.

Classes:
- CscWebUrl: Fetches data from CSC web service.
- GetTokenUrl: Retrieves tokens from an external service.
- GoogleRecaptcha: Validates Google reCAPTCHA responses.
- CloudFlare: Interacts with CloudFlare services.
- GoogleAuth: Authenticates using Google OAuth.
- FacebookAuth: Authenticates using Facebook OAuth.
- AppleAuth: Authenticates using Apple OAuth.
- SsoToken: Handles SSO token related operations.

Exceptions:
- GenericException: Custom exception for handling application-specific errors.

Constants:
- Various constants imported from shared_config.

"""
import json
import re
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from shared_config.exceptions import GenericException
from shared_config.logging import custom_log
from shared_config.exception_constants import NONRETRYABLE_CODE, STATUS_TYPE
from shared_config import constants
from . import constants as config

class CscWebUrl:
    """
    Class for fetching data from CSC web service.
    """
    def fetch_data(self, payload):
        """
        Fetch data from CSC web service.
        """
        url = config.CSC_WEB_SERVICE_URL
        payload = config.POLICY_PREMIUM_DETAILS_INPUT % (
            payload.get('bj_user_id', ''),
            payload.get('bj_ref_number', ''),
            payload.get('policy_no', ''), 'NA',
            payload.get('str_dob', '')
        )
        response = requests.post(url=url, data=payload, timeout=config.CUSTOMER_PORTAL_API_TIME_OUT,
                                 headers={"Content-Type": "text/plain"})
        return response

class GetTokenUrl:
    """
    Class for fetching token from external service.
    """
    def fetch_data(self, payload):
        """
        Fetch token from external service.
        """
        url = config.GET_TOKEN_URL
        request = payload
        headers = {'Content-type': 'application/json', 'x-csps-xrfkey': config.MY_ACCOUNT_XRFKEY}
        params = {
            "head": {
                "apiname": "getToken",
                "source": "CS_APP",
                "xrfkey": config.MY_ACCOUNT_XRFKEY
            },
            "body": {
                "clientId": payload["client_id"]
            }
        }
        params_str = json.dumps(params)
        try:
            resp = requests.post(url, data=params_str.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        except Exception as e:
            custom_log(level='error', request=request, params={'body': {'request': params},
                                                                'detail': str(e)})
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail="Error while generating token", request=request) from e

        if resp.status_code != 200:
            custom_log(level='info', request=request, params={'body': {'request': params,
                                                                       'response': resp.text}, 
                                    'detail': 'Not received response from SSO get token API'})
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail="Error while generating token", request=request)

        custom_log(level='info', request=request, params={'body': {'request': params,
                                                                   'response': resp.text},
                                          'detail': 'Received response from SSO get token API'})
        resp = json.loads(resp.text)
        return resp

class GoogleRecaptcha:
    """
    Class for validating Google reCAPTCHA.
    """
    def fetch_data(self, payload):
        """
        Validate Google reCAPTCHA.
        """
        secret_key = config.GOOGLE_RECAPTCHA_SECRET_KEY
        recaptcha_response = payload['recaptcha_response']
        recaptcha_version = payload['recaptcha_version']
        if recaptcha_version and recaptcha_version == config.GOOGLE_RECAPTCHA_V3:
            secret_key = config.GOOGLE_RECAPTCHA_V3_SECRET_KEY
        values = '?secret=' + str(secret_key) + '&response=' + str(recaptcha_response)
        try:
            response = requests.post(config.GOOGLE_RECAPTCHA_VERIFY_URL + values, {}, verify=False,
                                     timeout=config.GOOGLE_RECAPTCHA_TIMEOUT).json()
        except Exception as e:
            custom_log(level="info", request=None, params=
                       {"detail": "Error while captcha validation", "message": repr(e)})
            raise GenericException(STATUS_TYPE["APP"], NONRETRYABLE_CODE["BAD_REQUEST"],
                                   response_msg="Something went wrong",
                                   detail="Something went wrong", request=None) from e
        if not response.get('success'):
            raise GenericException(STATUS_TYPE['APP'], NONRETRYABLE_CODE['BAD_REQUEST'],
                                   request=None, detail='Recaptcha validation failed.',
                                   response_msg='Recaptcha validation failed.')

class CloudFlare:
    """
    Class for interacting with CloudFlare service.
    """
    def fetch_data(self, payload):
        """
        Fetch data from CloudFlare.
        """
        response = requests.post(config.CF_BASE_URL, json=payload,
                                 headers={"X-Auth-Email": config.AUTH_EMAIL,
                                  "X-Auth-Key": config.GLOBAL_API_KEY}, timeout=constants.DEFAULT_TIMEOUT)
        return response

class GoogleAuth:
    """
    Class for authenticating via Google OAuth.
    """
    def fetch_data(self, payload):
        """
        Authenticate using Google OAuth.
        """
        access_token = payload["access_token"]
        google_url = config.GOOGLE_AUTH_ENDPOINT + "?access_token=" + access_token
        response = requests.get(google_url, timeout=constants.DEFAULT_TIMEOUT)
        return response

class FacebookAuth:
    """
    Class for authenticating via Facebook OAuth.
    """
    def fetch_data(self, payload):
        """
        Authenticate using Facebook OAuth.
        """
        access_token = payload["access_token"]
        try:
            fb_url = (
                config.FACEBOOK_AUTH_ENDPOINT +
                "?fields=id,name,email,picture{url}&access_token=" +
                access_token
            )
            response = requests.get(fb_url, timeout=constants.DEFAULT_TIMEOUT, verify=False)
            return response
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail="Error while validating facebook user info " + repr(e),
                                   response_msg='Error while validating facebook user info',
                                   request=payload) from e

class AppleAuth:
    """
    Class for authenticating via Apple OAuth.
    """
    def fetch_data(self, payload):
        """
        Authenticate using Apple OAuth.
        """
        access_token = payload["access_token"]
        request = payload
        try:
            url = config.APPLE_KEY_ENDPOINT
            header_data = jwt.get_unverified_header(access_token)
            response = requests.get(url, timeout=constants.DEFAULT_TIMEOUT)
            res = json.loads(response.text)
            key_data = {}
            for data in res["keys"]:
                apple_data_sanitization(data, request)
                if data.get('kid') == header_data.get("kid"):
                    key_data = data
            public_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
            result = jwt.decode(access_token, public_key, audience=config.APPLE_AUDIENCE,
                                algorithms=header_data.get("alg"))
            apple_data_sanitization(result, request)
            return result
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail="Error while validating apple user info" + repr(e),
                                   response_msg='Error while validating apple user info',
                                    request=request) from e

def apple_data_sanitization(data_dict, request):
    """
    Sanitize Apple user data.
    """
    for key, value in data_dict.items():
        if isinstance(value, str):
            if re.search(value, constants.BLACKLISTED_CHARS):
                raise GenericException(status_type=STATUS_TYPE["APP"],
                                       exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                       detail="Error while validating apple user info",
                                       response_msg='Error while validating apple user info',
                                       request=request)

class SsoToken:
    """
    Class for handling SSO token.
    """
    def fetch_data(self, payload):
        """
        Fetch SSO token data.
        """
        access_token = payload
        return config.SSO_VALIDATE_TOKEN_URL + access_token
