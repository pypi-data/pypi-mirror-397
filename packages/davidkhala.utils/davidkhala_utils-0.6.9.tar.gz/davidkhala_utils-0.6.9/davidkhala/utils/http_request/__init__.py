import requests
from requests import Session
from requests.auth import HTTPBasicAuth


def default_on_response(response: requests.Response) -> dict | None:
    """
    :param response:
    :return: the input response
    :raise HTTPError: if not response.ok
    """
    if response.ok:
        if response.text: return response.json()
        return None
    else:
        return response.raise_for_status()


class Request:
    def __init__(self, auth: dict = None, on_response=default_on_response):
        self.options: dict = {"headers": {}}
        if auth is not None:
            bearer = auth.get("bearer")
            if bearer is not None:
                self.options["headers"]["Authorization"] = f"Bearer {bearer}"
                del auth["bearer"]
            else:
                self.options["auth"] = HTTPBasicAuth(auth["username"], auth["password"])
        self.session: Session | None = None
        self.on_response = on_response

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        del self.session

    def request(self, url, method: str, params=None, data=None, json=None) -> dict:
        if self.session:
            response = self.session.request(method, url, params=params, data=data, json=json, **self.options)
        else:
            response = requests.request(
                method, url, params=params, data=data, json=json, **self.options
            )
        return self.on_response(response)
