"""Thin client for the CRM sandbox API."""
from __future__ import annotations

import time

import requests

from .config import API_BASE, CRM_TOKEN


class CRMError(RuntimeError):
    pass


class CRM:
    def __init__(self, token: str = CRM_TOKEN, base: str = API_BASE):
        if not token:
            raise CRMError("CRM_TOKEN is not set (put it in .env or the environment)")
        self.base = base.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})

    # GET and PATCH (absolute field values) are idempotent and safe to retry. POST is never
    # retried: a create that committed server-side but returned 5xx would be duplicated.
    RETRYABLE = {"GET", "PATCH"}

    def _req(self, method: str, path: str, **kw):
        tries = 3 if method in self.RETRYABLE else 1
        for attempt in range(tries):
            try:
                r = self.s.request(method, self.base + path, timeout=30, **kw)
            except requests.RequestException as e:
                if attempt < tries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise CRMError(f"{method} {path} -> network error: {e}") from e
            if r.status_code >= 500 and attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            if r.status_code >= 400:
                raise CRMError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
            return r.json()

    def _paged(self, path: str, **params) -> list[dict]:
        out, page = [], 1
        while True:
            body = self._req("GET", path, params={**params, "page": page, "page_size": 200})
            out.extend(body["data"])
            total = body.get("total")
            if not body["data"] or (total is not None and len(out) >= total):
                return out
            page += 1

    def accounts(self, **filters) -> list[dict]:
        return self._paged("/accounts", **filters)

    def contacts(self) -> list[dict]:
        return self._paged("/contacts")

    def account(self, account_id: str) -> dict:
        return self._req("GET", f"/accounts/{account_id}")

    def update_account(self, account_id: str, fields: dict) -> dict:
        return self._req("PATCH", f"/accounts/{account_id}", json=fields)

    def create_account(self, fields: dict) -> dict:
        return self._req("POST", "/accounts", json=fields)

    def contact(self, contact_id: str) -> dict:
        return self._req("GET", f"/contacts/{contact_id}")

    def update_contact(self, contact_id: str, fields: dict) -> dict:
        return self._req("PATCH", f"/contacts/{contact_id}", json=fields)
