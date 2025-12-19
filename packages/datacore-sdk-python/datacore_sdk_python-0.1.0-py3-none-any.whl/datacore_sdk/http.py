from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from .exceptions import APIError


@dataclass
class AuthConfig:
    api_key: str | None = None
    bearer_token: str | None = None

    def __post_init__(self) -> None:
        # Enforce mutual exclusivity: only one of api_key or bearer_token may be provided
        if self.api_key and self.bearer_token:
            raise ValueError("Provide either 'api_key' or 'bearer_token', not both.")


class HttpClient:
    """Thin HTTP client wrapper around `requests`.

    Handles base URL, auth headers, and error mapping.
    """

    def __init__(self, base_url: str, auth: AuthConfig | None = None, timeout: float | None = 30.0):
        self.base_url = base_url.rstrip("/")
        self.auth = auth or AuthConfig()
        self.timeout = timeout
        # Session is created lazily on first request to avoid hard dependency during import/instantiation
        self._session = None  # type: ignore

    def _headers(self, extra: Mapping[str, str] | None = None) -> MutableMapping[str, str]:
        headers: dict[str, str] = {
            "Accept": "text/plain",
            "User-Agent": "datacore-sdk-python/0.1.0",
            "Customer": "tachcorp",
        }
        # Auth headers: prefer bearer token if provided, otherwise api key header
        if self.auth.bearer_token:
            headers["Authorization"] = f"Bearer {self.auth.bearer_token}"
        elif self.auth.api_key:
            headers["x-api-key"] = f"{self.auth.api_key}"
        if extra:
            headers.update(extra)
        return headers

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def _handle_response(self, resp: Any) -> Any:
        if 200 <= resp.status_code < 300:
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return resp.json()
            return resp.text
        try:
            payload = resp.json()
            message = payload.get("message") or payload.get("error") or resp.reason
        except Exception:
            payload = None
            message = resp.text or resp.reason
        raise APIError(resp.status_code, message, details=payload if isinstance(payload, dict) else None)

    def _get_session(self):
        if self._session is None:
            try:
                import requests  # type: ignore
            except Exception as exc:
                raise RuntimeError(
                    "The 'requests' package is required to perform HTTP calls. Install with 'pip install requests'."
                ) from exc
            self._session = requests.Session()
        return self._session

    def get(self, path: str, *, params: Mapping[str, Any] | None = None, headers: Mapping[str, str] | None = None) -> Any:
        session = self._get_session()
        resp = session.get(self._url(path), params=params, headers=self._headers(headers), timeout=self.timeout)
        return self._handle_response(resp)

    def post(self, path: str, *, json: Any | None = None, headers: Mapping[str, str] | None = None) -> Any:
        session = self._get_session()
        resp = session.post(self._url(path), json=json, headers=self._headers(headers), timeout=self.timeout)
        return self._handle_response(resp)

    def put(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        session = self._get_session()
        resp = session.put(self._url(path), json=json, headers=self._headers(headers), timeout=self.timeout)
        return self._handle_response(resp)

    def delete(
        self,
        path: str,
        *,
        json: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        session = self._get_session()
        resp = session.delete(self._url(path), json=json, headers=self._headers(headers), timeout=self.timeout)
        return self._handle_response(resp)
