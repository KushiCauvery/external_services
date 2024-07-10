import requests
from .tebt_services import TokenUrl, AppLogin, TebtPanValidate, TebtQuote
from .web_services import CscWebUrl, GetTokenUrl, GoogleRecaptcha, CloudFlare, GoogleAuth, FacebookAuth, SsoToken, AppleAuth
from .crm_services import MsTokenGen, CrmLeadUrl, MobileCrmLeadUrl
from .policy_services import ReceiptAccessToken, ReceiptDetails, ReceiptDetailsPdf, AnnualPremiumStatement, UnitStatement
from .credit_score import CrifScore, ExperianScore
from .dedupe import DedupeService

class APIManager:
    def __init__(self, service_type, payload=None, headers=None):
        self.payload = payload
        self.headers = headers
        self.adapter = self.get_adapter(service_type)

    def get_adapter(self, service_type):
        adapters = {
            'CRM_MS_TOKEN_GEN_URL': MsTokenGen,
            'CRM_LEADS_API_URL': CrmLeadUrl,
            'MOBILE_CRM_LEADS_API_URL': MobileCrmLeadUrl, 
            'CSC_WEB_SERVICE_URL': CscWebUrl,
            'GENERATE_TOKEN_URL': TokenUrl,
            'CP_APP_LOGIN_URL': AppLogin,
            'RECEIPT_ACCESS_TOKEN_URL': ReceiptAccessToken,
            'RECIEPT_DETAILS_URL': ReceiptDetails,
            'RECIEPT_PDF_URL': ReceiptDetailsPdf,
            'ANNUAL_PREMIUM_STATEMENT_URL': AnnualPremiumStatement,
            'UNIT_STATEMENT_URL': UnitStatement,
            'CRIF_URL': CrifScore,
            'TEBT_PAN_VALIDATION': TebtPanValidate,
            'GET_TOKEN_URL': GetTokenUrl,
            'GOOGLE_RECAPTCHA_VERIFY_URL': GoogleRecaptcha,
            'SSO_VALIDATE_TOKEN_URL': SsoToken,
            'EXPERIAN_URL': ExperianScore,
            'CF_BASE_URL': CloudFlare,
            'GOOGLE_AUTH_ENDPOINT': GoogleAuth,
            'FACEBOOK_AUTH_ENDPOINT': FacebookAuth,
            'APPLE_KEY_ENDPOINT': AppleAuth,
            'TEBT_GET_QUOTE_URL': TebtQuote,
            'DedupeService': DedupeService
        }
        if service_type in adapters:
            return adapters[service_type]()
        else:
            raise ValueError(f"Unsupported service type: {service_type}")

    def get_data(self):
        try:
            if self.payload and self.headers:
                return self.adapter.fetch_data(self.payload, self.headers)
            elif self.payload:
                return self.adapter.fetch_data(self.payload)
            else:
                return self.adapter.fetch_data()
        except requests.RequestException as e:
            return {"error": str(e)}
