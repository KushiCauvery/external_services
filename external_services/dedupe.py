from datetime import datetime
import requests
from django.core.cache import caches
from rest_framework import status
from rest_framework.exceptions import APIException
from shared_config import utils as api_utils
from . import constants as settings


class DedupeService:
    """
    Calls dedupe api and save all client id's.
    """
    GENERATE_TOKEN_URL = settings.DEDUPE_GENERATE_TOKEN_URL
    REFRESH_TOKEN_URL = settings.DEDUPE_REFRESH_TOKEN_URL
    DEDUPE_API_URL = settings.DEDUPE_API_URL
    TOKEN_CACHE_KEY = "DEDUPE_API_TOKEN"
    TOKEN_CACHE_TIMEOUT = 500
    REQUEST_TIMEOUT = 20

    def __init__(self):
        self.cache = caches["api_v1"]
        self.proxy = api_utils.get_proxy()

    def _generate_token(self):
        payload = {
            "userId": settings.DEDUPE_USERID,
            "password": settings.DEDUPE_PASSWORD
        }
        try:
            resp = requests.post(self.GENERATE_TOKEN_URL, data=payload, proxies=self.proxy, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception:
            raise
        if resp.status_code != status.HTTP_200_OK:
            raise APIException("Error Fetching data")
        token = resp.json()["data"]["token"]
        self._store_token(token)
        return token

    def _refresh_token(self):
        if self.TOKEN_CACHE_KEY not in self.cache:
            self._generate_token()
        token = self.cache.get(self.TOKEN_CACHE_KEY)
        headers = {
            "Authorization": "Bearer %s" % token
        }
        payload = {
            "projectCode": "customer_app"
        }
        try:
            resp = requests.post(self.REFRESH_TOKEN_URL, headers=headers, data=payload, proxies=self.proxy, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception:
            raise
        if resp.status_code != status.HTTP_200_OK:
            raise APIException("Error Fetching data")
        token = resp.json()["data"]["token"]
        self._store_token(token)
        return token

    def _store_token(self, token):
        """
        saves token in redis cache till expiry.
        """
        # exp_in_second = jwt.decode(token, verify=False)['exp'] - int(datetime.now().timestamp())
        self.cache.set(self.TOKEN_CACHE_KEY, token, timeout=self.TOKEN_CACHE_TIMEOUT)

    def _get_token(self):
        """
        If token is not in cache, populate the cache and return the token.
        """
        if self.TOKEN_CACHE_KEY in self.cache:
            token = self.cache.get(self.TOKEN_CACHE_KEY)
        else:
            token = self._generate_token()
        return token

    def fetch_customer_data_from_dedupe(self, user):
        token = self._get_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        payload = {
            "projectCode": "customer_app",
            "phone-no": user.phone,
            "email-id": user.email,
            "fields": "policy,profile"
        }
        try:
            resp = requests.post(self.DEDUPE_API_URL, headers=headers, data=payload, proxies=self.proxy, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception:
            raise APIException("Something went wrong")
        if resp.status_code != status.HTTP_200_OK:
            raise APIException("Error Fetching data")
        return resp.json()["data"]

    def get_customer_client_ids(self, user):
        client_id_list = list()
        user_identifier = [user.phone, user.country_code + user.phone]
        response_data = self.fetch_customer_data_from_dedupe(user)

        # Filter out client id from response if email and phone matches
        added_clients = []
        for data in response_data:
            client_id = dict()
            data_identifier = [data.get("phone-no"), data.get("phone_no"), data.get("phone01")]
            is_valid_user_data = bool(set(user_identifier) & set(data_identifier))
            if "customer_id" in data and data.get("customer_id") not in added_clients \
                    and is_valid_user_data:
                client_id["client_id"] = data.get("customer_id")
                client_id["source"] = data.get("customer_source")
                added_clients.append(data.get("customer_id"))
                client_id_list.append(client_id)
        return client_id_list

    def get_exide_life_policy(self, user):
        """
        Fetch excide life policy details from dedupe.
        """
        excide_policy = []
        response_data = self.fetch_customer_data_from_dedupe(user)
        added_clients = []
        for data in response_data:
            if "customer_id" in data and data.get("customer_id") not in added_clients \
                    and user.phone == data.get("phone-no") and data.get("customer_source") == "Exide":
                dob = ""
                if data.get("date_of_birth"):
                    parsed_date = datetime.strptime(data.get("date_of_birth"), "%Y%m%d")
                    dob = parsed_date.strftime("%d/%m/%Y")

                policy_master_data = dict()
                policy_master_data["source"] = "exide_life"
                policy_master_data["first_name"] = data.get("customer_first_name")
                policy_master_data["last_name"] = data.get("customer_last_name")
                policy_master_data["dob"] = dob
                policy_master_data["source"] = "exide_life"

                for policy in data.get("policy_details", []):
                    policy_data = policy_master_data.copy()
                    policy_data["policy_name"] = policy.get("product_description")
                    policy_data["policy_no"] = policy.get("policy_id")
                    policy_data["policy_clientid"] = policy.get("customer_id")
                    policy_data["policy_start_date"] = policy.get("issue_date")
                    policy_data["premium_value"] = policy.get("annual_premium")
                    policy_data["status"] = policy.get("policy_status", "")
                    excide_policy.append(policy_data)
        return excide_policy

    def get_customer_details_by_policy_id(self, policy_id):
        token = self._get_token()
        headers = {
            "Authorization": "Bearer %s" % token
        }
        payload = {
            "projectCode": "qr_service",
            "policyId": policy_id,
            "fields": "policy,profile"
        }
        try:
            resp = requests.post(self.DEDUPE_API_URL, headers=headers, data=payload, proxies=self.proxy,
                                 timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception:
            raise APIException("Something went wrong")
        if resp.status_code != status.HTTP_200_OK:
            raise APIException("Error Fetching data")
        response_data = resp.json()["data"]
        result = dict()
        for data in response_data:
            if "customer_id" in data:
                result['email'] = data.get("email_id")
                result['phone'] = [data.get("phone_no"), data.get('phone-no'), data.get('phone01')]
                result['dob'] = datetime.strptime(data.get("date_of_birth"), '%Y%m%d').strftime('%d-%m-%Y')
                result['first_name'] = data.get("customer_first_name")
                result['last_name'] = data.get("customer_last_name")
                result['is_nri'] = data.get("nri_indicator")
                break
        return result


    def validate_dedupe_user_data(self, compare_key_list, params, user_data):
        try:
            for key in compare_key_list:
                if key == 'phone':
                    user_identifier = [str(params.get('phone')), str(params.get('country_code', '')) + str(params.get('phone'))]
                    if user_data.get("is_nri").lower() == "y":
                        user_identifier = [str(params.get('country_code', '')) + str(params.get('phone'))]
                    is_valid_user_data = bool(set(user_identifier) & set(user_data['phone']))
                    if not is_valid_user_data:
                        return False
                    continue
                if params[key] != user_data[key]:
                    return False
        except KeyError:
            return False
        return True