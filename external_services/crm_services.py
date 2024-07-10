import requests
import json
from shared_config import constants
from . import constants as config

class MsTokenGen:
    def fetch_data(self, payload):
        url =  config.CRM_MS_TOKEN_GEN_URL
        updated_payload = config.CRM_MS_TOKEN_GEN_PARAMS
        if payload == "mobile":
            updated_payload =  config.MOBILE_CRM_MS_TOKEN_GEN_PARAMS
        response = requests.post(url, data=updated_payload, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class CrmLeadUrl:
    def fetch_data(self, payload, headers):
        url =  config.CRM_LEADS_API_URL
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class MobileCrmLeadUrl:
    def fetch_data(self, payload, headers):
        url =  config.MOBILE_CRM_LEADS_API_URL
        response = requests.post(url=url, data=json.dumps(payload), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


