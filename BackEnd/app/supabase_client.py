from urllib.parse import urlencode

import requests
from flask import current_app, g

from .utils.errors import APIError


class SupabaseRestClient:
    """Small PostgREST client that forwards the user's JWT so RLS applies."""

    def __init__(self, access_token=None, use_service_role=False):
        self.supabase_url = current_app.config["SUPABASE_URL"].rstrip("/")
        self.anon_key = current_app.config["SUPABASE_ANON_KEY"]
        self.service_role_key = current_app.config["SUPABASE_SERVICE_ROLE_KEY"]
        self.timeout = current_app.config["REQUEST_TIMEOUT_SECONDS"]

        if not self.supabase_url or not self.anon_key:
            raise APIError("SERVER_NOT_CONFIGURED", "Supabase is not configured", 500)

        if use_service_role:
            if not self.service_role_key:
                raise APIError("SERVER_NOT_CONFIGURED", "Supabase service role key is not configured", 500)
            bearer = self.service_role_key
            apikey = self.service_role_key
        else:
            bearer = access_token or getattr(g, "access_token", None)
            if not bearer:
                raise APIError("UNAUTHORIZED", "Unauthorized", 401)
            apikey = self.anon_key

        self.headers = {
            "apikey": apikey,
            "Authorization": f"Bearer {bearer}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _url(self, table, params=None):
        url = f"{self.supabase_url}/rest/v1/{table}"
        if params:
            url = f"{url}?{urlencode(params, doseq=True)}"
        return url

    def request(self, method, table, params=None, json=None, prefer=None):
        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer

        response = requests.request(
            method,
            self._url(table, params),
            headers=headers,
            json=json,
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = {"message": response.text}
            message = detail.get("message") or detail.get("error") or "Supabase request failed"
            raise APIError("SUPABASE_ERROR", message, min(response.status_code, 500))

        if not response.text:
            return None
        return response.json()

    def select(self, table, params=None):
        return self.request("GET", table, params=params)

    def insert(self, table, payload, params=None):
        return self.request("POST", table, params=params, json=payload, prefer="return=representation")

    def update(self, table, payload, params=None):
        return self.request("PATCH", table, params=params, json=payload, prefer="return=representation")

    def delete(self, table, params=None):
        return self.request("DELETE", table, params=params, prefer="return=representation")


def get_supabase_client(access_token=None, use_service_role=False):
    return SupabaseRestClient(access_token=access_token, use_service_role=use_service_role)
