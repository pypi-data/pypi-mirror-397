from __future__ import annotations

import requests

from .auth import AuthBase
from .config import WaypointConfig
from .error import WaypointHTTPError


class BaseClient:
    """
    Base for per-API clients.

    Holds shared config, auth strategy, and HTTP session.
    """

    def __init__(
        self,
        config: WaypointConfig,
        auth: AuthBase,
        session: requests.Session | None = None,
    ):
        self._config = config
        self._auth = auth
        self._session = session or requests.Session()

    @property
    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self._auth.apply_headers(headers)

        return headers

    def _url(self, path: str) -> str:
        return f"{self._config.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        url = self._url(path)
        return self._request_by_url(method, url, json=json, params=params)

    def _request_by_url(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        resp = self._session.request(
            method=method,
            url=url,
            headers=self._headers,
            json=json,
            params=params,
            timeout=self._config.timeout_seconds,
        )
        if not resp.ok:
            raise WaypointHTTPError(resp.status_code, resp.text)

        if resp.status_code == 204:
            return {}
        return resp.json()
