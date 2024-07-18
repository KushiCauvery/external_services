"""
This module provides classes and methods for integrating with CRM services.
It includes functionalities for generating tokens and posting leads data.
Classes:
    MsTokenGen: Handles the token generation for CRM services.
    CrmLeadUrl: Posts lead data to the CRM leads API.
    MobileCrmLeadUrl: Posts lead data to the mobile CRM leads API.
"""

import json
import requests
from shared_config import constants
from . import constants as config

class MsTokenGen:
    """
    Handles the token generation for CRM services.
    """
    def fetch_data(self, payload):
        """
        Fetches the token from the CRM token generation URL.
        Args:
            payload (str): The type of CRM service requesting the token.
        Returns:
            requests.Response: The response from the token generation API.
        """
        url = config.CRM_MS_TOKEN_GEN_URL
        updated_payload = config.CRM_MS_TOKEN_GEN_PARAMS
        if payload == "MobileCRMLead":
            updated_payload = config.MOBILE_CRM_MS_TOKEN_GEN_PARAMS
        response = requests.post(url, data=updated_payload, timeout=constants.DEFAULT_TIMEOUT)
        return response

class CrmLeadUrl:
    """
    Posts lead data to the CRM leads API.
    """
    def fetch_data(self, payload, headers):
        """
        Posts the lead data to the CRM leads API.
        Args:
            payload (dict): The lead data to be posted.
            headers (dict): The headers for the API request.
        Returns:
            requests.Response: The response from the CRM leads API.
        """
        url = config.CRM_LEADS_API_URL
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=headers,
            timeout=constants.DEFAULT_TIMEOUT
        )
        return response

class MobileCrmLeadUrl:
    """
    Posts lead data to the mobile CRM leads API.
    """
    def fetch_data(self, payload, headers):
        """
        Posts the lead data to the mobile CRM leads API.
        Args:
            payload (dict): The lead data to be posted.
            headers (dict): The headers for the API request.
        Returns:
            requests.Response: The response from the mobile CRM leads API.
        """
        url = config.MOBILE_CRM_LEADS_API_URL
        response = requests.post(
            url=url,
            data=json.dumps(payload),
            headers=headers,
            timeout=constants.DEFAULT_TIMEOUT
        )
        return response
