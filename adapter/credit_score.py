"""
This module provides classes and methods for integrating with external credit score services
such as CRIF and Experian, and BankCloud payment integration.

Classes:
    CrifScore: Handles the preparation and fetching of CRIF credit score data.
    ExperianScore: Handles the preparation and fetching of Experian credit score data.
    BankCloudUrl: Handles the fetching of data from BankCloud.
    BankCloudToken: Manages token generation for BankCloud transactions.
"""
import json
import base64
import hashlib
import hmac
import math
from datetime import datetime
import uuid
import requests
from shared_config.exceptions import GenericException
from shared_config.exception_constants import NONRETRYABLE_CODE, STATUS_TYPE
from shared_config.logging import custom_log
from .models import ApiExternalLog
from . import constants as config

class CrifScore:
    """
    A class to interact with the CRIF API for fetching credit scores.

    Methods
    -------
    prepare_request_data(name, mobile)
        Prepares the request XML payload with the provided user details.
    fetch_data(payload)
        Sends the request to the CRIF API and logs the request and response.
    """

    def prepare_request_data(self, name, mobile):
        """
        Prepares the request XML payload with the provided user details.

        Parameters
        ----------
        name : str
            The name of the user.
        mobile : str
            The mobile number of the user.

        Returns
        -------
        str
            The formatted XML payload.
        """
        payload = '<REQUEST-REQUEST-FILE><HEADER-SEGMENT><PRODUCT-TYP>FUSION</PRODUCT-TYP><PRODUCT-VER>2.0</PRODUCT-VER><REQ-MBR>{customer_id}</REQ-MBR><SUB-MBR-ID>{sub_mbr_id}</SUB-MBR-ID><INQ-DT-TM>03-02-2022</INQ-DT-TM><REQ-VOL-TYP>C01</REQ-VOL-TYP><REQ-ACTN-TYP>AT01</REQ-ACTN-TYP><TEST-FLG>HMTEST</TEST-FLG><AUTH-FLG>Y</AUTH-FLG><RES-FRMT>XML</RES-FRMT><LOS-NAME>INHOUSE</LOS-NAME><REQ-SERVICE-TYPE>CB SCORE|INCOME SEGMENT|DEMOG</REQ-SERVICE-TYPE></HEADER-SEGMENT><INQUIRY><APPLICANT-SEGMENT><NAME>{name}</NAME><DOB-DATE></DOB-DATE><PAN></PAN><UID></UID><VOTER-ID></VOTER-ID><ADDRESSES><ADDRESS><TYPE></TYPE><ADDRESS-1></ADDRESS-1><CITY></CITY><STATE></STATE><PIN></PIN></ADDRESS></ADDRESSES><PHONE>{mobile}</PHONE><EMAIL></EMAIL><RELATION-TYPE></RELATION-TYPE><RELATION-VALUE></RELATION-VALUE><NOMINEE-TYPE></NOMINEE-TYPE><NOMINEE-VALUE></NOMINEE-VALUE><GENDER-TYPE>G02</GENDER-TYPE></APPLICANT-SEGMENT><APPLICATION-SEGMENT><INQUIRY-UNIQUE-REF-NO></INQUIRY-UNIQUE-REF-NO><CREDT-RPT-ID></CREDT-RPT-ID><CREDT-REQ-TYP>INDV</CREDT-REQ-TYP><CREDT-INQ-PURPS-TYP>CP12</CREDT-INQ-PURPS-TYP><CREDT-INQ-PURPS-TYP-DESC>ACCT-ORIG</CREDT-INQ-PURPS-TYP-DESC><CLIENT-CUSTOMER-ID></CLIENT-CUSTOMER-ID><BRANCH-ID></BRANCH-ID><APP-ID></APP-ID><AMOUNT></AMOUNT></APPLICATION-SEGMENT></INQUIRY></REQUEST-REQUEST-FILE>'
        return payload.format(name=name, mobile=mobile, sub_mbr_id=config.SUB_MBR_ID,
                              customer_id=config.CUSTOMER_ID)

    def fetch_data(self, payload):
        """
        Sends the request to the CRIF API and logs the request and response.

        Parameters
        ----------
        payload : dict
            The payload containing the user details.

        Returns
        -------
        dict
            The response from the CRIF API.
        """
        url = config.CRIF_URL
        name = payload["name"]
        mobile = payload["mobile"]
        request_xml = self.prepare_request_data(name, mobile)
        headers = {
            'Content-Type': 'application/xml',
            'requestXML': request_xml,
            'userId': config.CRIF_USER,
            'password': config.CRIF_PASSWORD,
            'mbrid': 'INS0000001',
            'productType': 'FUSION',
            'productVersion': '2.0',
            'reqVolType': 'INDV'
        }
        try:
            custom_log(level="info", params={"message": "Logging request body", "body": payload})
            external_log = ApiExternalLog.objects.create(
                request_log=payload["log_obj"],  # need to check this while integrating the api
                service_name='CRIF',
                service_url=url,
                request_body=request_xml,
            )
            response = requests.request("POST", url, headers=headers, data=payload,
                                        timeout=config.REQUEST_TIMEOUT)
            external_log.response = response.text
            external_log.status_code = response.status_code
            external_log.save()
        except requests.exceptions.RequestException:
            error_msg = "Unable to fetch data from crif"
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail=error_msg, response_msg=error_msg)
        response = {"response": response, "headers": headers}
        return response

class ExperianScore:
    """
    A class to interact with the Experian API for fetching credit scores.

    Methods
    -------
    prepare_request_data(name, mobile)
        Prepares the request XML payload with the provided user details.
    fetch_data()
        Sends the request to the Experian API and logs the request and response.
    """

    def prepare_request_data(self, name, mobile):
        """
        Prepares the request XML payload with the provided user details.

        Parameters
        ----------
        name : str
            The name of the user.
        mobile : str
            The mobile number of the user.

        Returns
        -------
        str
            The formatted XML payload.
        """
        payload = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" ' \
                  'xmlns:urn="http://nextgenws.ngwsconnect.experian.com">\n<soapenv:Header/>\n' \
                  '<soapenv:Body>\n<urn:process>\n' \
                  '<urn:cbv2String>><![CDATA[' \
                  '<INProfileRequest>\n<Identification>\n' \
                  '<XMLUser>{user}</XMLUser>\n' \
                  '<XMLPassword>{password}</XMLPassword>\n' \
                  '</Identification>\n' \
                  '<Application>\n' \
                  '<ScoreFlag>1</ScoreFlag>\n' \
                  '<PSVFlag>12</PSVFlag>\n' \
                  '</Application>\n' \
                  '<Applicant>\n<Surname></Surname>\n' \
                  '<FirstName>{name}</FirstName>\n' \
                  '<MobilePhone>{mobile}</MobilePhone>\n' \
                  '</Applicant>\n\n' \
                  '</INProfileRequest>\n]]>\n' \
                  '</urn:cbv2String>\n</urn:process>\n</soapenv:Body>\n</soapenv:Envelope>'
        return payload.format(name=name, mobile=mobile, user=config.EXPERIAN_USER,
                              password=config.EXPERIAN_PASSWORD)

    def fetch_data(self):
        """
        Sends the request to the Experian API and logs the request and response.

        Parameters
        ----------
        payload : dict
            The payload containing the user details.

        Returns
        -------
        dict
            The response from the Experian API.
        """
        payload = {}
        url = config.EXPERIAN_URL
        name = payload["name"]
        mobile = payload["mobile"]
        payload = self.prepare_request_data(name, mobile)
        headers = {
            'Content-Type': 'application/xml'
        }
        try:
            custom_log(level="info", params={"message": "Logging request body", "body": payload})
            external_log = ApiExternalLog.objects.create(
                request_log=payload["log_obj"],
                service_name='Experian',
                service_url=url,
                request_body=payload,
            )
            response = requests.request("POST", url, headers=headers, data=payload,
                                        timeout=config.REQUEST_TIMEOUT)
            external_log.response = response.text
            external_log.status_code = response.status_code
            external_log.save()
        except requests.exceptions.RequestException:
            error_msg = "Unable to fetch data from experian"
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail=error_msg, response_msg=error_msg)
        response = {"response": response, "external_log": external_log}
        return response

class BankCloudUrl:
    """
    A class to interact with the BankCloud API for fetching data.

    Methods
    -------
    fetch_data(payload)
        Sends the request to the BankCloud API and returns the response.
    """

    def fetch_data(self, payload):
        """
        Sends the request to the BankCloud API and returns the response.

        Parameters
        ----------
        payload : dict
            The payload containing the data to be sent to the API.

        Returns
        -------
        dict
            The response from the BankCloud API.
        """
        url = config.BANKCLOUD_FETCH_URL
        payload_str = json.dumps(payload, separators=(',', ':'))
        headers = {
            'Authorization': generate_hash(self, payload_str, url),
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=payload_str.encode('utf-8'), headers=headers,
                                 timeout=config.REQUEST_TIMEOUT)
        print(response.text)
        return response

def generate_hash(self, payload_str, request_url):
    """
    Generates a hash for the BankCloud API request.

    Parameters
    ----------
    payload_str : str
        The JSON string payload to be sent to the API.
    request_url : str
        The URL of the API endpoint.

    Returns
    -------
    str
        The generated authorization token.
    """
    user_secret = config.BANKCLOUD_USER_SECRET
    user_token = config.BANKCLOUD_USER_TOKEN
    byte_array = payload_str.encode('UTF-8')
    data_bytes = hashlib.sha256(byte_array)
    base64string = base64.b64encode(data_bytes.digest()).decode()
    nonce = uuid.uuid4().hex
    current_ts = math.floor(datetime.now().timestamp())
    request_data = str(current_ts) + nonce + base64string + request_url
    signature = request_data.encode('utf-8')
    secret_key_bytes = user_secret.encode('ascii')
    signature_bytes = hmac.new(secret_key_bytes, signature, digestmod=hashlib.sha256).digest()
    base64_request_data = base64.b64encode(signature_bytes).decode()
    auth_token_str = base64_request_data + ":" + nonce + ":" + str(current_ts) + ":" + user_token
    plain_text_bytes = auth_token_str.encode('utf-8')
    auth_token = base64.b64encode(plain_text_bytes).decode()
    return auth_token

class BankCloudToken:
    """
    A class to interact with the BankCloud API for generating tokens.

    Attributes
    ----------
    request : request
        The request object.
    policy_no : str
        The policy number.
    payment_data : dict
        The payment data.
    txn_id : str
        The transaction ID.

    Methods
    -------
    fetch_data()
        Sends the request to the BankCloud API to generate a token.
    request_paylaod()
        Prepares the request payload with the provided data.
    """

    def __init__(self, request=None, policy_no=None, payment_data=None, txn_id=None):
        """
        Constructs all the necessary attributes for the BankCloudToken object.

        Parameters
        ----------
        request : request
            The request object.
        policy_no : str
            The policy number.
        payment_data : dict
            The payment data.
        txn_id : str
            The transaction ID.
        """
        self.request = request
        self.policy_no = policy_no
        self.payload = None
        self.payment_data = payment_data
        self.txn_id = txn_id

    def fetch_data(self):
        """
        Sends the request to the BankCloud API to generate a token.

        Returns
        -------
        Response
            The response from the BankCloud API.
        """
        request_timeout = 10
        payload_str = self.request_paylaod()
        request_url = config.BANKCLOUD_GENERATE_ORDER_URL
        hash_request = generate_hash(self, payload_str, request_url)
        headers = {
            'Authorization': hash_request,
            'Content-Type': 'application/json'
        }
        payload = self.request_paylaod()
        response = requests.post(request_url, data=payload.encode('utf-8'), headers=headers,
                                 timeout=request_timeout)
        return response        

    def request_paylaod(self):
        """
        Prepares the request payload with the provided data.

        Returns
        -------
        str
            The JSON string payload.
        """
        route_id_ulip = config.ULIP_ROUTE_ID
        route_id_conventional = config.CONVENTIONAL_ROUTE_ID
        product_type_dict = {"Conventional": "CL", "Unit linked": "UL"}
        product_type = product_type_dict[self.payment_data["message"]["product_type"]]
        if not self.payload:
            payload = {
                "route": route_id_ulip if product_type == "UL" else route_id_conventional,
                "producttype": product_type,
                "paymentjourney": 1,
                "lob": "Quick Pay",
                "collectiontype": "Sample",
                "consumerData": {
                    "urn": self.txn_id,
                    "requestreftype": "PolicyNo",
                    "requestrefno": self.policy_no,
                    "custname": self.payment_data["message"]["Full_name"],
                    "custmobile": self.payment_data["message"]["mobile"],
                    "custemail": self.payment_data["message"]["email"],
                    "dueamount": self.payment_data["message"]["Insurance_premium"],
                },
                "redirect_url_fail": "https://Checkout/QuickPayFailure",
                "redirect_url_success": "https://Checkout/QuickPaySuccess"
            }
            self.payload = json.dumps(payload, separators=(',', ':'))
        return self.payload
