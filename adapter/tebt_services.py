"""
Module: tebt_services.py

This module contains classes and functions to interact with various services provided by TEBT.

Classes:
- TokenUrl: Handles fetching of token from a specified URL.
- AppLogin: Handles login to the application.
- TebtPanValidate: Handles validation of PAN numbers with TEBT service.
- ValidSoapResponse: Handles SOAP message plugin for validating SOAP responses.
- TebtQuote: Handles fetching quotes from TEBT service.
- TebtPayment: Handles posting payments to TEBT service.

Functions:
- get_wsdl_endpoint_url(wsdl_url, request): Retrieves the endpoint URL for a given WSDL URL.

Constants:
- Various constants imported from the config module for configuration purposes.

Exceptions:
- GenericException: Custom exception for handling API errors specific to TEBT services.
"""

import json
import sys
import requests
from shared_config import constants
from shared_config.logging import custom_log
from shared_config.exceptions import GenericException
from shared_config.exception_constants import STATUS_TYPE, RETRYABLE_CODE
from shared_config import utils as api_utils
from custom_suds.client import Client as suds_client
from custom_suds.plugin import MessagePlugin
from custom_suds.cache import ObjectCache
from . import constants as config

class TokenUrl:
    """Handles fetching of token from a specified URL."""

    def fetch_data(self):
        """Fetches token from the generate token URL.

        Returns:
            requests.Response: Response object from the API call.
        """
        url = config.GENERATE_TOKEN_URL
        headers = {'Content-type': 'application/json',
                   'Authorization': config.AUTH_TOKEN_FOR_GENERATE_TOKEN}
        response = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        return response

class AppLogin:
    """Handles login to the application."""

    def fetch_data(self, payload, headers):
        """Performs application login.

        Args:
            payload (dict): Login payload.
            headers (dict): Headers for the request.

        Returns:
            requests.Response: Response object from the API call.
        """
        url = config.CP_APP_LOGIN_URL
        params_str = json.dumps(payload)
        response = requests.post(url=url, data=params_str.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class TebtPanValidate:
    """Handles validation of PAN numbers with TEBT service."""

    def fetch_data(self, payload):
        """Validates PAN number with TEBT service.

        Args:
            payload (dict): Payload containing PAN number.

        Returns:
            requests.Response: Response object from the API call.
        """
        url = config.TEBT_PAN_VALIDATION
        request_data = {
            "head": {
                "source": "",
                "userid": "",
                "txnid": "",
                "version": "1",
                "ptnrid": "",
                "chnlid": "",
                "subchnlid": "",
            },
            "panreq": {
                "pandetails": [
                    {
                        "pannumber": payload['pan_no'],
                        "partyrk": ""
                    }
                ]
            }
        }
        response = requests.get(url, data=json.dumps(request_data), timeout=config.REQUEST_TIMEOUT)
        return response

class ValidSoapResponse(MessagePlugin):
    """Handles SOAP message plugin for validating SOAP responses."""

    def __init__(self, *args, **kwargs):
        """Initializes the ValidSoapResponse plugin.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.kwargs = kwargs

    def sending(self, context):
        """Handles sending SOAP requests.

        Args:
            context (object): Context object for SOAP request.
        """
        xml_req = str(context.envelope)
        params = {'body': str(xml_req), 'detail': "Request successfully sent to TEBT server"}
        custom_log('info', request=self.kwargs['request'], params=params)
        sys.stdout.flush()

    def received(self, context):
        """Handles receiving SOAP responses.

        Args:
            context (object): Context object for SOAP response.
        """
        xml_res = context.reply
        params = {'body': str(xml_res), 'detail': "Response obtained from TEBT server"}
        custom_log('info', request=self.kwargs['request'], params=params)
        sys.stdout.flush()

        answer_decoded = xml_res.decode()
        if config.SOAP_URL_START in answer_decoded:
            header_split = answer_decoded.split(config.SOAP_URL_START)
            header_split_msg = config.SOAP_URL_START + header_split[1]

            footer_split = header_split_msg.split('</soapenv:Envelope>')
            reply_final = footer_split[0] + '</soapenv:Envelope>'
        else:
            header_split = answer_decoded.split('<soap:Envelope')
            header_split_msg = '<soap:Envelope' + header_split[1]

            footer_split = header_split_msg.split('</soap:Envelope>')
            reply_final = footer_split[0] + '</soap:Envelope>'

        reply_final_decoded = reply_final.encode()
        context.reply = reply_final_decoded

cache = ObjectCache()
cache.setduration(seconds=config.CACHE_DURATION)

class TebtQuote:
    """Handles fetching quotes from TEBT service."""

    def fetch_data(self, request):
        """Fetches quote data from TEBT service.

        Args:
            request: Request object.

        Returns:
            suds_client: SOAP client object.
        """
        plugin = ValidSoapResponse(request=request)
        proxy = api_utils.get_proxy(request=request)
        url = config.TEBT_GET_QUOTE_URL
        try:
            client = suds_client(get_wsdl_endpoint_url(url, request), plugins=[plugin], cache=cache,
                                 cachingpolicy=config.WSDL_CACHE_POLICY_VALUE, proxy=proxy)
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE['TEBT'],
                                   exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                                   detail=f'TEBT services down. {repr(e)}',
                                   response_msg=config.WEBSITE_ERROR,
                                   body=None, url=url) from e
        client.set_options(timeout=config.REQUEST_TIMEOUT)
        return client

def get_wsdl_endpoint_url(wsdl_url, request):
    """Gets the endpoint URL for the given WSDL URL.

    Args:
        wsdl_url (str): WSDL URL of the service.
        request: Request object.

    Returns:
        str: Endpoint URL.
    """
    custom_log('info', request,
               {'detail': 'In get_wsdl_endpoint_url function. Fetching endpoint url.',
                                 'body': {'params': {}}})
    try:
        response = requests.get(wsdl_url, timeout=config.REQUEST_TIMEOUT)
    except Exception as e:
        custom_log(level='info', request=request,
                   params={'detail': 'Error from tebt.', 'body': {'error_msg': repr(e)}})
        raise GenericException(status_type=STATUS_TYPE['TEBT'],
                               exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                               detail=f'TEBT services down. {repr(e)}',
                               response_msg=config.WEBSITE_ERROR,
                               request=request, url=wsdl_url) from e
    custom_log('info', request, {'detail': 'Response received from wsdl service.',
                                 'body': {'params': {}}})
    if response.status_code == config.WSDL_SUCCESS_STATUS_CODE:
        custom_log('info', request, {'detail': 'Endpoint url fetched.', 'body': {'params': {}}})
        return response.url
    raise GenericException(status_type=STATUS_TYPE['TEBT'],
                    exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                    detail=f'TEBT services down due to get_wsdl_endpoint_url function and its status code: {response.status_code}',
                    response_msg=config.WEBSITE_ERROR,
                    request=request, url=wsdl_url)

class TebtPayment:
    """Handles posting payments to TEBT service."""

    def fetch_data(self, payload):
        """Posts payment data to TEBT service.

        Args:
            payload (dict): Payment payload.

        Returns:
            requests.Response: Response object from the API call.
        """
        url = config.TEBT_PAYMENT_RECEPT_POSTING_URL
        response = requests.post(url=url, data=payload, timeout=config.CUSTOMER_PORTAL_API_TIME_OUT)
        return response
