import requests
import json
from shared_config import constants
from . import constants as config

class MsTokenGen:
    def fetch_data(self, payload):
        url =  config.CRM_MS_TOKEN_GEN_URL
        updated_payload = config.CRM_MS_TOKEN_GEN_PARAMS
        if payload == "MobileCRMLead":
            updated_payload =  config.MOBILE_CRM_MS_TOKEN_GEN_PARAMS
        response = requests.post(url, data=updated_payload, timeout=constants.DEFAULT_TIMEOUT)
        return response

class CrmLeadUrl:
    def fetch_data(self, payload, headers):
        url =  config.CRM_LEADS_API_URL
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        return response

class MobileCrmLeadUrl:
    def fetch_data(self, payload, headers):
        url =  config.MOBILE_CRM_LEADS_API_URL
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        return response
