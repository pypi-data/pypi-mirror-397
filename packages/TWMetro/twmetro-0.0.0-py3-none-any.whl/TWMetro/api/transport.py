import requests

class Transport:
    def __init__(self, base_url: str, timeout: int, token: str):
        self.base_url = base_url
        self.timeout = timeout
        self.token = token

    def get(self, endpoint: str) -> requests.Response:
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        if response.status_code == 401:
            raise PermissionError("Unauthorized: Invalid token.")
        elif response.status_code != 200:
            raise ValueError(f"Request to {endpoint} failed with status code {response.status_code}")

        return response