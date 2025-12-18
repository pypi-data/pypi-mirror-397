from time import time

import os
import requests


DEFAULT_FRONT_BASE_URL = "https://ps3838.com"


class PinnacleFrontClient:
    """Stateful PS3838 API client backed by ``requests.Session``."""

    def __init__(
        self,
        login: str | None = None,
        password: str | None = None,
        base_url: str = DEFAULT_FRONT_BASE_URL,
    ) -> None:
        self._login = login or os.environ.get("PS3838_LOGIN")
        self._password = password or os.environ.get("PS3838_PASSWORD")
        if not self._login or not self._password:
            raise ValueError(
                "PS3838_LOGIN and PS3838_PASSWORD must be provided either via "
                "Client() arguments or environment variables."
            )
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "*/*",
                "Origin": self._base_url,
                "Referer": f"{self._base_url}/",
            }
        )

    def authenticate(self, locale: str = "en_US"):
        ts = int(time() * 1000)

        url = f"{self._base_url}/member-auth/v2/authenticate"
        params = {
            "locale": locale,
            "_": ts,
            "withCredentials": "true",
        }
        data = {
            "captcha": "",
            "captchaToken": "",
            "loginId": self._login,
            "password": self._password,
        }

        r = self._session.post(url, params=params, data=data)
        r.raise_for_status()
        return r.json()
