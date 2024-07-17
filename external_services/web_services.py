import json
import re
import jwt
import requests
from . import constants as config
from shared_config.exceptions import GenericException
from shared_config.logging import custom_log
from shared_config.exception_constants import NONRETRYABLE_CODE, STATUS_TYPE
from shared_config import constants
from jwt.algorithms import RSAAlgorithm

class CscWebUrl:
    def fetch_data(self, payload):
        url =  config.CSC_WEB_SERVICE_URL
        print(payload)
        payload = config.POLICY_PREMIUM_DETAILS_INPUT % (payload.get('bj_user_id', ''),
                                                                     payload.get('bj_ref_number', ''),
                                                                     payload.get('policy_no', ''), 'NA',
                                                                     payload.get('str_dob', ''))
        print(payload)
        
        response = requests.post(url=url, data=payload, timeout=config.CUSTOMER_PORTAL_API_TIME_OUT,
                             headers={"Content-Type": "text/plain"})
        # if response.status_code == 200:
        #     return response.text
        # else:
        #     response.raise_for_status()

class GetTokenUrl:
    def fetch_data(self, payload):
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
        # print(params_str)
        # resp = requests.post(url, data=params_str.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        # print(resp) #504
        # return resp
        try:
            resp = requests.post(url, data=params_str.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        except Exception as e:
            custom_log(level='error', request=request, params={'body': {'request': params},
                                                            'detail': str(e)})
            raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                detail="Error while generating token", request=request)

        if resp.status_code != 200:
            custom_log(level='info', request=request, params={'body': {'request': params, 'response': resp.text},
                                                            'detail': 'Not received response from my account portal SSO get token API'})
            raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                detail="Error while generating token", request=request)

        custom_log(level='info', request=request, params={'body': {'request': params, 'response': resp.text},
                                                            'detail': 'Received response from my account portal SSO get token API'})
        resp = json.loads(resp.text)
        return resp
    
class GoogleRecaptcha:
    def fetch_data(self, payload):
        secret_key=config.GOOGLE_RECAPTCHA_SECRET_KEY
        recaptcha_response = payload['recaptcha_response'] 
        recaptcha_version = payload['recaptcha_version']
        if recaptcha_version and recaptcha_version == config.GOOGLE_RECAPTCHA_V3:
            secret_key=config.GOOGLE_RECAPTCHA_V3_SECRET_KEY
        
        values = '?secret=' + str(secret_key) + '&response=' + str(recaptcha_response)
        try:
            response = requests.post(config.GOOGLE_RECAPTCHA_VERIFY_URL + values, {}, verify=False,
                                timeout=config.GOOGLE_RECAPTCHA_TIMEOUT).json()
        except Exception as e:
            custom_log(level="info", request=None, params={"detail": "Error while captcha validation", "message": repr(e)})
            raise GenericException(STATUS_TYPE["APP"], NONRETRYABLE_CODE["BAD_REQUEST"], response_msg="Something went wrong",
                            detail="Something went wrong", request=None)
        if not response.get('success'):
            raise GenericException(STATUS_TYPE['APP'], NONRETRYABLE_CODE['BAD_REQUEST'], request=None,
                            detail='Recaptcha validation failed.', response_msg='Recaptcha validation failed.')

class CloudFlare:
    def fetch_data(self, payload):
        response = requests.post(config.CF_BASE_URL, json=payload, headers={"X-Auth-Email": config.AUTH_EMAIL,
                                                                            "X-Auth-Key": config.GLOBAL_API_KEY})
        return response
    
class GoogleAuth:
    def fetch_data(self, payload):
        access_token = payload["access_token"]
        google_url = config.GOOGLE_AUTH_ENDPOINT + "?access_token=" + access_token
        #custom_log(level='info', request=payload, params={'body': {'google_url': google_url}, 'detail': 'calling google for data.'})
        response = requests.get(google_url, timeout=constants.DEFAULT_TIMEOUT)
        return response
    
class FacebookAuth:
    def fetch_data(self, payload):
        access_token = payload["access_token"]
        try:
            fb_url = config.FACEBOOK_AUTH_ENDPOINT + "?fields=id,name,email,picture{url}&access_token=" + access_token
            response = requests.get(fb_url, timeout=constants.DEFAULT_TIMEOUT, verify=False)
            #custom_log(level='info', request=payload, params={'body': json.loads(response.text), 'detail': 'Data returned from facebook.'})
            return response
        except:
            raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"], detail="Error while validating facebook user info", response_msg='Error while validating facebook user info', request=payload)
        
class AppleAuth:
    def fetch_data(self, payload):
        access_token = payload["access_token"]
        request  = payload
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
        except:
            raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                detail="Error while validating apple user info",
                                response_msg='Error while validating apple user info', request=request)

def apple_data_sanitization(data_dict, request):
    for key, value in data_dict.items():
        if isinstance(value, int):
            pass
        elif isinstance(value, str):
            if re.search(value, constants.BLACKLISTED_CHARS):
                raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                       detail="Error while validating apple user info",
                                       response_msg='Error while validating apple user info', request=request)
        elif isinstance(value, bool):
            pass

class SsoToken:
    def fetch_data(self, payload):
        access_token = payload#["access_token"]
        return config.SSO_VALIDATE_TOKEN_URL + access_token
