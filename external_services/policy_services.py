import json
import requests
from shared_config import constants
from . import constants as config
from datetime import datetime

class ReceiptAccessToken:
    def fetch_data(self):
        url = config.RECEIPT_ACCESS_TOKEN_URL
        headers = {'x-api-key': config.RECEIPT_X_API_KEY, 'Content-Type': 'application/json'}
        request_data = {"head":
            {
                "userid": config.RECEIPT_TXN_ID_PREFIX,
                "source": config.RECEIPT_TXN_ID_PREFIX,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0")
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        response = requests.post(url, payload.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class ReceiptDetails:
    def fetch_data(self, payload):
        url = config.RECIEPT_DETAILS_URL
        body = payload.get("body", {})
        policy_no = body.get("policyno", "")
        client_id = body.get("clientid", "")
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
        receipt_access_token = ReceiptAccessToken()
        access_token_data = receipt_access_token.fetch_data()
        access_token = access_token_data['body']['authtoken']
        headers = {'accesstoken': access_token,
                   'x-api-key': config.RECEIPT_X_API_KEY}
        response = requests.post(url, payload.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class ReceiptDetailsPdf:
    def fetch_data(self, payload):
        url = config.RECIEPT_PDF_URL
        data = payload.get("body", {})
        request_data = {
        "head": {
                "apiname": config.RECEIPT_PDF_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "policyno": data.get("policyno", ""),
                "clientid": data.get("clientid", ""),
                "receiptno": data.get("receiptno", ""),
                "modeofcomm": "View",
                "estatementtype": config.RECEIPT_PDF_ESTATEMENT_TYPE
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        receipt_access_token = ReceiptAccessToken()
        access_token_data = receipt_access_token.fetch_data()
        access_token = access_token_data['body']['authtoken']
        headers = {'accesstoken': access_token,
                   'x-api-key': config.RECEIPT_X_API_KEY}
        response = requests.post(url, payload.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class AnnualPremiumStatement:
    def fetch_data(self, payload):
        url = config.ANNUAL_PREMIUM_STATEMENT_URL
        data = payload.get("body", {})
        request_data = {
            "head": {
                "apiname": config.RECEIPT_APS_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "adhoctype": "",
                "clientid": data.get("client_id", ""),
                "policyno": data.get("policy_no", ""),
                "year": data.get("year", ""),
                "modeofcomm": data.get("mode_of_comm"),
                "estatementtype": config.RECEIPT_APS_ESTATEMENT_TYPE,
                "fromdate": "",
                "todate": ""
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        receipt_access_token = ReceiptAccessToken()
        access_token_data = receipt_access_token.fetch_data()
        access_token = access_token_data['body']['authtoken']
        headers = {'accesstoken': access_token,
                   'x-api-key': config.RECEIPT_X_API_KEY}
        response = requests.post(url, payload.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

class UnitStatement:
    def fetch_data(self, payload):
        url = config.UNIT_STATEMENT_URL
        data = payload.get("body", {})
        request_data = {
            "head": {
                "apiname": config.RECEIPT_APS_API_NAME,
                "source": config.RECEIPT_SOURCE,
                "txnid": config.RECEIPT_TXN_ID_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S0"),
                "version": config.RECEIPT_VERSION
            },
            "body": {
                "policyno": data.get("policy_no", ""),
                "fromdate": data.get("from_date", ""),
                "todate": data.get("to_date", ""),
                "adhoctype": "S",
                "modeofcomm": data.get("mode_of_comm"),
                "estatementtype": "Adhoc_Stmt",
                "year": ""
            }
        }
        payload = json.dumps(request_data, separators=(',', ':'))
        receipt_access_token = ReceiptAccessToken()
        access_token_data = receipt_access_token.fetch_data()
        access_token = access_token_data['body']['authtoken']
        headers = {'accesstoken': access_token,
                   'x-api-key': config.RECEIPT_X_API_KEY}
        response = requests.post(url, payload.encode('utf-8'), headers=headers, timeout=constants.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
