import logging

import requests

logger = logging.getLogger(__name__)


class RestClient:
    def __init__(
        self,
        endpoint: str,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
    ):
        self.endpoint = endpoint
        if not token and (username and password):
            self.token: str | None = self._get_token(username, password)
        else:
            self.token = token

    @property
    def default_headers(self) -> dict:
        return {"Authorization": f"Token {self.token}"}

    def _get_token(self, username: str, password: str) -> str:
        r = requests.post(
            f"{self.endpoint}/api-token-auth/",
            data={"username": username, "password": password},
        )

        assert r.status_code == 200
        return r.json()["token"]

    def post(self, url: str, data: dict, files=None) -> dict:
        if files:
            r = requests.post(
                f"{self.endpoint}/api/{url}/",
                headers=self.default_headers,
                data=data,
                files={"image": files},
            )
        else:
            r = requests.post(
                f"{self.endpoint}/api/{url}/", headers=self.default_headers, json=data
            )
        if r.status_code >= 400:
            logger.error("Post failed with: %s\n%s", r.status_code, r.text)
            r.raise_for_status()
        return r.json()

    def put_file(self, url: str, content, filename: str = ""):

        headers = self.default_headers

        if filename:
            headers["Content-Disposition"] = f"attachment; filename={filename}"

        r = requests.put(f"{self.endpoint}/api/{url}", headers=headers, data=content)
        if r.status_code >= 400:
            logger.error("Put file failed with: %s\n%s", r.status_code, r.text)
            r.raise_for_status()

    def patch(self, url: str, data: dict) -> dict:
        r = requests.patch(
            f"{self.endpoint}/api/{url}/", headers=self.default_headers, json=data
        )
        if r.status_code >= 400:
            logger.error("Patch failed with: %s\n%s", r.status_code, r.json())
            r.raise_for_status()
        return r.json()

    def get(self, url: str, query: str = "", fail_if_empty: bool = True) -> None | dict:
        r = requests.get(
            f"{self.endpoint}/api/{url}/{query}", headers=self.default_headers
        )
        if r.status_code == 404:
            if fail_if_empty:
                r.raise_for_status()
            return None
        if r.status_code >= 400:
            logger.error("Get failed with: %s\n%s", r.status_code, r.json())
            r.raise_for_status()
        return r.json()

    def delete(self, url: str):
        r = requests.delete(f"{self.endpoint}/api/{url}", headers=self.default_headers)
        if r.status_code >= 400:
            logger.error("Delete failed with: %s", r.status_code)
            r.raise_for_status()
