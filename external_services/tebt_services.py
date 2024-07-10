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
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            response.raise_for_status()

class AppLogin:
    def fetch_data(self, payload):
        url =  config.CP_APP_LOGIN_URL
        params_str = json.dumps(payload)
        token_url_instance = TokenUrl()  
        token_data = token_url_instance.fetch_data()  
        token = token_data.get("body").get("token")
        headers = {'Content-type': 'application/json', 'Authorization': 'Basic ' + token}
        response = requests.post(url=url, data=params_str.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            #return json.loads(response.text)
            return response.text
        else:
            response.raise_for_status()

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
        try:
            response = requests.get(url, data=json.dumps(request_data))
            if response.status_code == 200:
                response_json = response.json()
                if response_json['head']['status'] == 'Success' and \
                        response_json['panres']['pandtls'][0]['panstatus'] == 'E':
                    return True
            custom_log(level='info', request=None, params={'message': 'Failed to validate PAN number.', 'response': response.text})
        except Exception as e:
            custom_log(level='error', request=None, params={'message': 'Failed to validate PAN number.'})
        return False

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
        answerDecoded = answer.decode()
        if '<soapenv:Envelope' in answerDecoded:
            header_split = answerDecoded.split('<soapenv:Envelope')
            header_split_msg = '<soapenv:Envelope' + header_split[1]

            footer_split = header_split_msg.split('</soapenv:Envelope>')
            replyFinal = footer_split[0] + '</soapenv:Envelope>'
        else:
            header_split = answerDecoded.split('<soap:Envelope')
            header_split_msg = '<soap:Envelope' + header_split[1]

            footer_split = header_split_msg.split('</soap:Envelope>')
            replyFinal = footer_split[0] + '</soap:Envelope>'

        replyFinalDecoded = replyFinal.encode()
        context.reply = replyFinalDecoded


cache = ObjectCache()
cache.setduration(seconds=config.CACHE_DURATION)


class TebtQuote:
    def fetch_data(self, request):
        plugin = ValidSoapResponse(request=request)
        proxy = api_utils.get_proxy(request=request)
        url = config.TEBT_GET_QUOTE_URL

        try:
            client = suds_client(get_wsdl_endpoint_url(url, request), plugins=[plugin], cache=cache, cachingpolicy=config.WSDL_CACHE_POLICY_VALUE, proxy=proxy)
            client.set_options(timeout=config.REQUEST_TIMEOUT)
            return client
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE['TEBT'], 
                                exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                                detail='TEBT services down. ' + repr(e),
                                response_msg='The website encountered an unexpected error. Please try again later.',
                                body=None, url=url)
        
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
                               response_msg='The website encountered an unexpected error. Please try again later.',
                               request=request, url=wsdl_url)
    custom_log('info', request, {'detail': 'Response received from wsdl service.', 'body': {'params': {}}})
    if response.status_code == config.WSDL_SUCCESS_STATUS_CODE:
        custom_log('info', request, {'detail': 'Endpoint url fetched.', 'body': {'params': {}}})
        return response.url
    else:
        raise GenericException(status_type=STATUS_TYPE['TEBT'], exception_code=RETRYABLE_CODE['API_UNREACHABLE'],
                               detail='TEBT services down due to get_wsdl_endpoint_url function and its status code: ' + str(
                                   response.status_code),
                               response_msg='The website encountered an unexpected error. Please try again later.',
                               request=request, url=wsdl_url)