import os


CRM_MS_TOKEN_GEN_URL = 'https://login.microsoftonline.com/b699289e-9677-4e1a-a46e-3b73acdcefe9/oauth2/token'
CRM_MS_TOKEN_GEN_PARAMS = {
    'resource': 'https://hdfclife-uat.crm8.dynamics.com',
    'client_id': '90e1d560-4007-4e4e-a258-02bd34d91173',
    'client_secret': 'kdA8Q~MK5TB9G9No1hwywTaXZlF_ZPnMsQ6PKa7R',
    'grant_type': 'client_credentials'
}
CRM_LEADS_API_URL = 'https://hdfclife-uat.crm8.dynamics.com/api/data/v9.2/hdfc_leadintegration'
CSC_WEB_SERVICE_URL = 'https://soauat2.hdfclife.com/TEBT_TPSL_ExternalInteraction_ModuleWeb/sca/BillJunctionWebServiceSoapWSDLExport'
CUSTOMER_PORTAL_API_TIME_OUT = 60  # in seconds
POLICY_PREMIUM_DETAILS_INPUT = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hdf="http://www.hdfcinsurance.com/">
  <soapenv:Header/>
  <soapenv:Body>
     <hdf:GetPolicyPremiumDetails_Health>
        <hdf:strUserId>%s</hdf:strUserId>
        <hdf:BJRefNo>%s</hdf:BJRefNo>
        <hdf:PolicyNo>%s</hdf:PolicyNo>
        <hdf:AppNo>%s</hdf:AppNo>
        <hdf:DOB>%s</hdf:DOB>
     </hdf:GetPolicyPremiumDetails_Health>
  </soapenv:Body>
</soapenv:Envelope>
"""
MOBILE_CRM_LEADS_API_URL = 'https://hdfclife-uat.crm8.dynamics.com/api/data/v9.2/hdfc_leadintegration'
MOBILE_CRM_MS_TOKEN_GEN_PARAMS = {
    'resource': 'https://hdfclife-uat.crm8.dynamics.com',
    'client_id': '90e1d560-4007-4e4e-a258-02bd34d91173',
    'client_secret': 'kdA8Q~MK5TB9G9No1hwywTaXZlF_ZPnMsQ6PKa7R',
    'grant_type': 'client_credentials'
}

#=================================My Account portal===================================
GET_TOKEN_URL = "https://myaccountnew-uat.hdfclife.com/portal/config/auth/v1/getToken"
SSO_VALIDATE_TOKEN_URL = "https://myaccountnew-uat.hdfclife.com/portal/config/auth/v1/validateToken?source=CS_APP&token="
MY_ACCOUNT_XRFKEY = "CSPS-HDFC_001"
GENERATE_TOKEN_URL = "https://soauat2.hdfclife.com/TEBT_ExternalInvocation_ESB_ModuleWeb/TEBT_AuthTokenManagementExport/generateToken"
AUTH_TOKEN_FOR_GENERATE_TOKEN = "Basic ZXlBaWRYTmxjbWxrSWpvaVozVndjMmgxY0NJc0lDSmhZMk5sYzNOMGJ5STZJbGRCVFZORVEwRk1URTlRVkVsT0lpd2dJbUZqWTJWemMzUnBiV1VpT2lJeE5Ua3hOakV4TmpnM05qa3hJbjA9OkZLWnl2cW5NSW94NWFQaXVBTEU0N2NtWkx1UzNFdGhlL0RSTUpzYXdidHlDTlB4aEI0TE1LSGZHNGwvUUZiTG1IemRNNmhrekx3Rm1sdVAxOTZ2ZWhPUXdIR3Y3Y0NRVys2dTlRekhoTkxLUXMrbVF6ZDBwMUsyYkdPSzhWTHJx"
CP_APP_LOGIN_URL = "https://soauat2.hdfclife.com/TEBT_CP_App_Migration_ModuleWeb/TEBT_CP_App_Migration_Module_HTTP_JSON_Export/CpAppESBInterface"

#=============================Policy Receipt=========================================
RECEIPT_ACCESS_TOKEN_URL = 'https://integrate-u.hdfclife.com/uatp/auth/token/'
RECIEPT_DETAILS_URL = 'https://integrate-u.hdfclife.com/uatp/cspsapi/estatement/premiumreceiptdetailsvendor'
RECIEPT_PDF_URL = 'https://integrate-u.hdfclife.com/uatp/cspsapi/estatement/premiumreceiptpdfvendor'
ANNUAL_PREMIUM_STATEMENT_URL = 'https://integrate-u.hdfclife.com/uatp/cspsapi/estatement/annualpsvendor'
UNIT_STATEMENT_URL = 'https://integrate-u.hdfclife.com/uatp/cspsapi/estatement/annualpsvendor'

RECEIPT_X_API_KEY = "dysbmVZ4Mb1P97Lj54ey824WAL4217sI5dZ9Ahti"
RECEIPT_TXN_ID_PREFIX = "CPAPP"
RECEIPT_SOURCE = "TOUCHPOINT_CUSTOMER_APP"
RECEIPT_VERSION = "1.0"
RECEIPT_DETAIL_API_NAME = "getReceiptDetail"
RECEIPT_ESTATEMENT_TYPE = "ReceiptDtls"
RECEIPT_APS_ESTATEMENT_TYPE = "APS_Stmt"
RECEIPT_APS_API_NAME = "getAdhocAps"
RECEIPT_PDF_ESTATEMENT_TYPE = "PRS"
RECEIPT_PDF_API_NAME = "getReceiptPdfMail"

#=================================CRIF Integration===================================
CRIF_URL = "https://test.crifhighmark.com/InquiryAgentOriginal/doGetFusionSync.service/fusionSync"
CRIF_USER = "balaji.m21@hdfclife.com"
CRIF_PASSWORD = "+GW1NiOxIf007lQmx5Llwzr4wic="
SUB_MBR_ID = "HDFC Life"
CUSTOMER_ID = "INS0000001"

#=================================Experian Integration===================================
EXPERIAN_URL = "https://connectuat.experian.in:8443/ngwsconnect/ngws"
EXPERIAN_USER = "cpu2hdfclife_uat05"
EXPERIAN_PASSWORD = "Kuliz@301"
EXPERIAN_PROCEED_AT_EXACT_MATCH = True
EXPERIAN_REPORT_VALIDITY = 60

#==============================Dedupe api urls=======================================
DEDUPE_GENERATE_TOKEN_URL = "https://customer-uat-public.api-hdfclife.com/v1/external/login"
DEDUPE_REFRESH_TOKEN_URL = "https://customer-uat-public.api-hdfclife.com/v1/external/refresh"
DEDUPE_API_URL = "https://customer-uat-public.api-hdfclife.com/v1/customers/dedupes"
DEDUPE_USERID="hdfc_capp"
DEDUPE_PASSWORD="HdfcApp@2023"

# Google Recaptcha Settings
GOOGLE_RECAPTCHA_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_SECRET_KEY")
GOOGLE_RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
GOOGLE_RECAPTCHA_TIMEOUT = 30
GOOGLE_RECAPTCHA_V3 = '3'
GOOGLE_RECAPTCHA_V3_SECRET_KEY = os.getenv("GOOGLE_RECAPTCHA_V3_SECRET_KEY")

#=================================Cloudflare Settings===================================
CF_PURGE_CALL = False
ZONE_ID = os.getenv("ZONE_ID")
AUTH_EMAIL = os.getenv("AUTH_EMAIL")
GLOBAL_API_KEY = os.getenv("GLOBAL_API_KEY")
ORIGIN_CA_KEY = os.getenv("ORIGIN_CA_KEY")
CF_BASE_URL = "https://api.cloudflare.com/client/v4/zones/%s/purge_cache" % (ZONE_ID, )
CF_WEBSITE_DOMAIN = 'www.hdfclife.com'
CF_API_DOMIAN = "api.hdfclife.com"
CF_MOBILE_DOMIAN = "mobapp.hdfclife.com"

TEBT_BASE_URL = 'http://124.30.32.37:9082/'
TEBT_PAN_VALIDATION = TEBT_BASE_URL + 'TEBT_CommonValidationsWeb/TEBT_CommonValidationsExport/validatepan'
TEBT_GET_QUOTE_URL = TEBT_BASE_URL + 'TEBT_QuoteGenerationWeb/sca/QuoteGeneration_ThirdPartyExport?wsdl'

GOOGLE_AUTH_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
FACEBOOK_AUTH_ENDPOINT = "https://graph.facebook.com/me"
APPLE_KEY_ENDPOINT = "https://appleid.apple.com/auth/keys"
APPLE_AUDIENCE = "com.hdfc.comwithAppleSignIn"

WSDL_SUCCESS_STATUS_CODE = 200
REQUEST_TIMEOUT = 60
WSDL_CACHE_POLICY_VALUE = 1
CACHE_DURATION = 3600

