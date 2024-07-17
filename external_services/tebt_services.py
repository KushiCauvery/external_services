import requests
from . import constants as config
from shared_config import constants
from shared_config.logging import custom_log
from shared_config.exceptions import GenericException
from shared_config.exception_constants import STATUS_TYPE, RETRYABLE_CODE
from shared_config import utils as api_utils
import json
import sys
from custom_suds.client import Client as suds_client
from custom_suds.plugin import MessagePlugin
from custom_suds.cache import ObjectCache

class TokenUrl:
    def fetch_data(self):
        url =  config.GENERATE_TOKEN_URL
        headers = {'Content-type': 'application/json', 'Authorization': config.AUTH_TOKEN_FOR_GENERATE_TOKEN}
        response = requests.get(url, headers=headers)
        return response

class AppLogin:
    def fetch_data(self, payload, headers):
        url =  config.CP_APP_LOGIN_URL
        params_str = json.dumps(payload)
        response = requests.post(url=url, data=params_str.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class TebtPanValidate:
    def fetch_data(self, payload):
        url =  config.TEBT_PAN_VALIDATION
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
        response = requests.get(url, data=json.dumps(request_data))
        return response

class ValidSoapResponse(MessagePlugin):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def sending(self, context):
        xml_req = str(context.envelope)
        params = {}
        print(xml_req)
        params['body'] = str(xml_req)
        params['detail'] = "Request successfully sent to TEBT server"
        custom_log('info', request=self.kwargs['request'], params=params)
        sys.stdout.flush()

    def received(self, context):
        xml_res = context.reply
        answer = context.reply
        params = {}
        print(xml_res)
        params['body'] = str(xml_res)
        params['detail'] = "Response obtained from TEBT server"
        custom_log('info', request=self.kwargs['request'], params=params)
        sys.stdout.flush()
        answer_decoded = answer.decode()
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
    def fetch_data(self, request):
        plugin = ValidSoapResponse(request=request)
        proxy = api_utils.get_proxy(request=request)
        url = config.TEBT_GET_QUOTE_URL
        try:
            client = suds_client(get_wsdl_endpoint_url(url, request), plugins=[plugin], cache=cache, cachingpolicy=config.WSDL_CACHE_POLICY_VALUE, proxy=proxy)
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE['TEBT'], 
                                exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                                detail='TEBT services down. ' + repr(e),
                                response_msg=config.WEBSITE_ERROR,
                                body=None, url=url)
        client.set_options(timeout=config.REQUEST_TIMEOUT)
        return client
        
def get_wsdl_endpoint_url(wsdl_url, request):
    """
    utility to get wsdl endpoint for tebt services
    :param wsdl_url:the wsdl url of the service
    :param request:
    :return:
    """
    custom_log('info', request, {'detail': 'In get_wsdl_endpoint_url function. Fetching endpoint url.', 'body': {'params': {}}})
    try:
        response = requests.get(wsdl_url, timeout=constants.DEFAULT_TIMEOUT)
    except Exception as e:
        custom_log(level='info', request=request, params={'detail': 'Error from tebt.', 'body': {'error_msg': repr(e)}})
        raise GenericException(status_type=STATUS_TYPE['TEBT'], exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                               detail='TEBT services down.' + repr(e),
                               response_msg=config.WEBSITE_ERROR,
                               request=request, url=wsdl_url)
    custom_log('info', request, {'detail': 'Response received from wsdl service.', 'body': {'params': {}}})
    if response.status_code == config.WSDL_SUCCESS_STATUS_CODE:
        custom_log('info', request, {'detail': 'Endpoint url fetched.', 'body': {'params': {}}})
        return response.url
    else:
        raise GenericException(status_type=STATUS_TYPE['TEBT'], exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                               detail='TEBT services down due to get_wsdl_endpoint_url function and its status code: ' + str(
                                   response.status_code),
                               response_msg=config.WEBSITE_ERROR,
                               request=request, url=wsdl_url)
    
class TebtPayment:
    def fetch_data(self, payload):
        url = config.TEBT_PAYMENT_RECEPT_POSTING_URL
        response = requests.post(url=url, data=payload, timeout=config.CUSTOMER_PORTAL_API_TIME_OUT)
        return response