import json
import requests

class DiaramaAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.diaramastudio.ru"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json; charset=utf-8"
        }

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        r = requests.get(url, headers=self.headers, params=params)
        r.raise_for_status()

        try:
            return r.json()
        except ValueError:
            content_type = r.headers.get("Content-Type", "")
            if "text" in content_type or "json" in content_type or "utf" in content_type:
                return {"content": r.text}
            else:
                return r.content

    def _post(self, endpoint, data=None, files=None):
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()

        if files:
            headers.pop("Content-Type", None)
            r = requests.post(url, headers=headers, files=files, data=data)
        else:
            r = requests.post(url, headers=headers, json=data)

        r.raise_for_status()
        return r.json()

    def _put(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        if data:
            r = requests.put(url, headers=self.headers, json=data)
        else:
            r = requests.put(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def _delete(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        r = requests.delete(url, headers=self.headers, params=params)
        if r.status_code in [200, 204]:
            try:
                return r.json()
            except:
                return {"success": True}
        else:
            r.raise_for_status()