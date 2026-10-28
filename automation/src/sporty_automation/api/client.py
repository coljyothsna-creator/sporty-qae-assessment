"""Small endpoint client that preserves responses for negative tests."""

import logging

import requests

from sporty_automation.config import Settings

LOGGER = logging.getLogger(__name__)


class BettingApi:
    def __init__(
        self,
        session: requests.Session,
        settings: Settings,
        user_id: str,
    ) -> None:
        if not user_id.strip():
            raise ValueError("user_id must not be blank")
        self._session = session
        self._settings = settings
        self._headers = {"x-user-id": user_id}

    def get_matches(self) -> requests.Response:
        return self._request("GET", "/api/matches")

    def get_balance(self) -> requests.Response:
        return self._request("GET", "/api/balance")

    def place_bet(
        self, match_id: str, selection: str, stake: float
    ) -> requests.Response:
        return self._request(
            "POST",
            "/api/place-bet",
            payload={
                "matchId": match_id,
                "selection": selection,
                "stake": stake,
            },
        )

    def reset_balance(self) -> requests.Response:
        return self._request("POST", "/api/reset-balance")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> requests.Response:
        LOGGER.info("%s %s", method, path)
        response = self._session.request(
            method,
            f"{self._settings.base_url}{path}",
            headers=self._headers,
            json=payload,
            timeout=self._settings.api_timeout,
        )
        LOGGER.info("%s %s returned HTTP %s", method, path, response.status_code)
        return response
