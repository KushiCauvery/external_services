"""
Module for fetching various policy related data through API calls.
"""

import json
from datetime import datetime
import requests
from shared_config import constants
from . import constants as config

class ReceiptAccessToken:
    """
    Fetches receipt access token for API calls.
    """
    def fetch_data(self):
        """
        Fetches data using receipt access token.
        """
        url = config.RECEIPT_ACCESS_TOKEN_URL
        headers = {'x-api-key': config.RECEIPT_X_API_KEY, 'Content-Type': 'application/json'}
        request_data = {
            "head": {
                "userid": config.RECEIPT_TXN_ID_PREFIX,
                "source": config.RECEIPT_TXN_ID_PREFIX,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0")
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class ReceiptDetails:
    """
    Fetches detailed receipt information.
    """
    def fetch_data(self, payload, headers):
        """
        Fetches receipt details using provided payload and headers.
        """
        url = config.RECIEPT_DETAILS_URL
        policy_no = payload["policy_no"]
        client_id = payload["client_id"]
        request_data = {
            "head": {
                "apiname": config.RECEIPT_DETAIL_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "policyno": policy_no,
                "clientid": client_id,
                "estatementtype": config.RECEIPT_ESTATEMENT_TYPE
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class ReceiptDetailsPdf:
    """
    Fetches PDF receipt details.
    """
    def fetch_data(self, payload, headers):
        """
        Fetches PDF receipt details using provided payload and headers.
        """
        url = config.RECIEPT_PDF_URL
        request_data = {
            "head": {
                "apiname": config.RECEIPT_PDF_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "policyno": payload["policy_no"],
                "clientid": payload["client_id"],
                "receiptno": payload["receipt_no"],
                "modeofcomm": "View",
                "estatementtype": config.RECEIPT_PDF_ESTATEMENT_TYPE
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class AnnualPremiumStatement:
    """
    Fetches annual premium statement.
    """
    def fetch_data(self, payload, headers):
        """
        Fetches annual premium statement using provided payload and headers.
        """
        url = config.ANNUAL_PREMIUM_STATEMENT_URL
        request_data = {
            "head": {
                "apiname": config.RECEIPT_APS_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "adhoctype": "",
                "clientid": payload["client_id"],
                "policyno": payload["policy_no"],
                "year": payload["year"],
                "modeofcomm": payload["mode_of_comm"],
                "estatementtype": config.RECEIPT_APS_ESTATEMENT_TYPE,
                "fromdate": "",
                "todate": ""
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response

class UnitStatement:
    """
    Fetches unit statement.
    """
    def fetch_data(self, payload, headers):
        """
        Fetches unit statement using provided payload and headers.
        """
        url = config.UNIT_STATEMENT_URL
        request_data = {
            "head": {
                "apiname": config.RECEIPT_APS_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "policyno": payload["policy_no"],
                "fromdate": payload["from_date"],
                "todate": payload["to_date"],
                "adhoctype": "S",
                "modeofcomm": payload["mode_of_comm"],
                "estatementtype": "Adhoc_Stmt",
                "year": ""
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers,
                                 timeout=constants.DEFAULT_TIMEOUT)
        return response
