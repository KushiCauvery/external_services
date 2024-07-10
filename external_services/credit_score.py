import requests
from . import constants as config
from shared_config.exceptions import GenericException
from shared_config.exception_constants import NONRETRYABLE_CODE, STATUS_TYPE
from shared_config.logging import custom_log
from .models import ApiExternalLog

class CrifScore:
    def prepare_request_data(self, name, mobile):
        payload = '<REQUEST-REQUEST-FILE><HEADER-SEGMENT><PRODUCT-TYP>FUSION</PRODUCT-TYP><PRODUCT-VER>2.0</PRODUCT-VER><REQ-MBR>{customer_id}</REQ-MBR><SUB-MBR-ID>{sub_mbr_id}</SUB-MBR-ID><INQ-DT-TM>03-02-2022</INQ-DT-TM><REQ-VOL-TYP>C01</REQ-VOL-TYP><REQ-ACTN-TYP>AT01</REQ-ACTN-TYP><TEST-FLG>HMTEST</TEST-FLG><AUTH-FLG>Y</AUTH-FLG><RES-FRMT>XML</RES-FRMT><LOS-NAME>INHOUSE</LOS-NAME><REQ-SERVICE-TYPE>CB SCORE|INCOME SEGMENT|DEMOG</REQ-SERVICE-TYPE></HEADER-SEGMENT><INQUIRY><APPLICANT-SEGMENT><NAME>{name}</NAME><DOB-DATE></DOB-DATE><PAN></PAN><UID></UID><VOTER-ID></VOTER-ID><ADDRESSES><ADDRESS><TYPE></TYPE><ADDRESS-1></ADDRESS-1><CITY></CITY><STATE></STATE><PIN></PIN></ADDRESS></ADDRESSES><PHONE>{mobile}</PHONE><EMAIL></EMAIL><RELATION-TYPE></RELATION-TYPE><RELATION-VALUE></RELATION-VALUE><NOMINEE-TYPE></NOMINEE-TYPE><NOMINEE-VALUE></NOMINEE-VALUE><GENDER-TYPE>G02</GENDER-TYPE></APPLICANT-SEGMENT><APPLICATION-SEGMENT><INQUIRY-UNIQUE-REF-NO></INQUIRY-UNIQUE-REF-NO><CREDT-RPT-ID></CREDT-RPT-ID><CREDT-REQ-TYP>INDV</CREDT-REQ-TYP><CREDT-INQ-PURPS-TYP>CP12</CREDT-INQ-PURPS-TYP><CREDT-INQ-PURPS-TYP-DESC>ACCT-ORIG</CREDT-INQ-PURPS-TYP-DESC><CLIENT-CUSTOMER-ID></CLIENT-CUSTOMER-ID><BRANCH-ID></BRANCH-ID><APP-ID></APP-ID><AMOUNT></AMOUNT></APPLICATION-SEGMENT></INQUIRY></REQUEST-REQUEST-FILE>'
        return payload.format(name=name, mobile=mobile, sub_mbr_id=config.SUB_MBR_ID, customer_id=config.CUSTOMER_ID)

    def fetch_data(self):
        payload={}
        url = config.CRIF_URL
        name = "Tia"
        mobile = 8999999999
        requestXML = self.prepare_request_data(name, mobile)
        headers = {
            'Content-Type': 'application/xml',
            'requestXML': requestXML,
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
                #request_log=log_obj, #need to check this while integrating the api
                service_name='CRIF',
                service_url=url,
                request_body=requestXML,
            )
            response = requests.request("POST", url, headers=headers, data=payload)
            external_log.response = response.text
            external_log.status_code = response.status_code
            external_log.save()
        except requests.exceptions.RequestException:
            error_msg = "Unable to fetch data from crif"
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail=error_msg, response_msg=error_msg)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()

class ExperianScore:
    def prepare_request_data(self, name, mobile):
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
        payload={}
        url = config.EXPERIAN_URL
        name = "Tia"
        mobile = 8999999999
        payload = self.prepare_request_data(name, mobile)
        headers = {
            'Content-Type': 'application/xml'
        }
        try:
            custom_log(level="info", params={"message": "Logging request body", "body": payload})
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response)
        except requests.exceptions.RequestException:
            error_msg = "Unable to fetch data from experian"
            raise GenericException(status_type=STATUS_TYPE["APP"],
                                   exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail=error_msg, response_msg=error_msg)
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()

