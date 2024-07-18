"""
Module for interacting with Dedupe API to fetch customer data and policy details.
"""

from datetime import datetime
import requests
from django.core.cache import caches
from rest_framework import status
from rest_framework.exceptions import APIException
from shared_config import utils as api_utils
from . import constants as settings

class DedupeService:
    """
    Service class for Dedupe API interactions.
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
        """
        Generates a token for accessing the Dedupe API.
        """
        payload = {
            "userId": settings.DEDUPE_USERID,
            "password": settings.DEDUPE_PASSWORD
        }
        try:
            resp = requests.post(self.GENERATE_TOKEN_URL, data=payload, proxies=self.proxy,
                                  timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            raise APIException("Error fetching data from external API") from exc
        if resp.status_code != status.HTTP_200_OK:
            raise APIException(settings.ERROR_FETCH)
        token = resp.json()["data"]["token"]
        self._store_token(token)
        return token

    def _refresh_token(self):
        """
        Refreshes the token for accessing the Dedupe API.
        """
        if self.TOKEN_CACHE_KEY not in self.cache:
            self._generate_token()
        token = self.cache.get(self.TOKEN_CACHE_KEY)
        headers = {
            "Authorization": settings.BEARER_VALUE % token
        }
        payload = {
            "projectCode": "customer_app"
        }
        try:
            resp = requests.post(self.REFRESH_TOKEN_URL, headers=headers, data=payload,
                                 proxies=self.proxy, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            raise APIException("Error fetching data from external API") from exc
        if resp.status_code != status.HTTP_200_OK:
            raise APIException(settings.ERROR_FETCH)
        token = resp.json()["data"]["token"]
        self._store_token(token)
        return token

    def _store_token(self, token):
        """
        Stores the token in the cache with a timeout.
        """
        self.cache.set(self.TOKEN_CACHE_KEY, token, timeout=self.TOKEN_CACHE_TIMEOUT)

    def _get_token(self):
        """
        Retrieves the token from the cache, generating a new one if necessary.
        """
        if self.TOKEN_CACHE_KEY in self.cache:
            token = self.cache.get(self.TOKEN_CACHE_KEY)
        else:
            token = self._generate_token()
        return token

    def fetch_customer_data_from_dedupe(self, user):
        """
        Fetches customer data from the Dedupe API.
        """
        token = self._get_token()
        headers = {
            "Authorization": settings.BEARER_VALUE % token
        }
        payload = {
            "projectCode": "customer_app",
            "phone-no": user.phone,
            "email-id": user.email,
            "fields": "policy,profile"
        }
        try:
            resp = requests.post(self.DEDUPE_API_URL, headers=headers, data=payload,
                                 proxies=self.proxy, timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            raise APIException("Something went wrong") from exc
        if resp.status_code != status.HTTP_200_OK:
            raise APIException(settings.ERROR_FETCH)
        return resp.json()["data"]

    def fetch_data(self, user):
        """
        Wrapper method to fetch customer data.
        """
        return self.fetch_customer_data_from_dedupe(user)

    def get_customer_client_ids(self, user):
        """
        Retrieves client IDs associated with the customer.
        """
        client_id_list = []
        user_identifier = [user.phone, user.country_code + user.phone]
        response_data = self.fetch_customer_data_from_dedupe(user)
        added_clients = []
        for data in response_data:
            client_id = {}
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
        Fetches Exide Life policy details associated with the customer.
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
                policy_master_data = {
                    "source": "exide_life",
                    "first_name": data.get("customer_first_name"),
                    "last_name": data.get("customer_last_name"),
                    "dob": dob
                }
                for policy in data.get("policy_details", []):
                    policy_data = policy_master_data.copy()
                    policy_data.update({
                        "policy_name": policy.get("product_description"),
                        "policy_no": policy.get("policy_id"),
                        "policy_clientid": policy.get("customer_id"),
                        "policy_start_date": policy.get("issue_date"),
                        "premium_value": policy.get("annual_premium"),
                        "status": policy.get("policy_status", "")
                    })
                    excide_policy.append(policy_data)
        return excide_policy

    def get_customer_details_by_policy_id(self, policy_id):
        """
        Retrieves customer details based on policy ID.
        """
        token = self._get_token()
        headers = {
            "Authorization": settings.BEARER_VALUE % token
        }
        payload = {
            "projectCode": "qr_service",
            "policyId": policy_id,
            "fields": "policy,profile"
        }
        try:
            resp = requests.post(self.DEDUPE_API_URL, headers=headers, data=payload,
                                 proxies=self.proxy,
                                 timeout=self.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            raise APIException("Something went wrong") from exc
        if resp.status_code != status.HTTP_200_OK:
            raise APIException(settings.ERROR_FETCH)
        response_data = resp.json()["data"]
        result = {}
        for data in response_data:
            if "customer_id" in data:
                result.update({
                    'email': data.get("email_id"),
                    'phone': [data.get("phone_no"), data.get('phone-no'), data.get('phone01')],
                    'dob': datetime.strptime(data.get("date_of_birth"), '%Y%m%d').strftime('%d-%m-%Y'),
                    'first_name': data.get("customer_first_name"),
                    'last_name': data.get("customer_last_name"),
                    'is_nri': data.get("nri_indicator")
                })
                break
        return result

    def validate_dedupe_user_data(self, compare_key_list, params, user_data):
        """
        Validates user data from Dedupe against provided parameters.
        """
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
