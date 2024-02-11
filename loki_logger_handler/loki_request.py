import requests
import gzip


class LokiRequest:
    def __init__(self, url, compressed=False, additional_headers=dict()):
        self.url = url
        self.compressed = compressed
        self.headers = additional_headers
        self.headers["Content-type"] = "application/json"
        self.session = requests.Session()

    def send(self, data):
        response = None
        try:
            if self.compressed:
                self.headers["Content-Encoding"] = "gzip"
                data = gzip.compress(bytes(data, "utf-8"))

            response = self.session.post(self.url, data=data, headers=self.headers)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Error while sending logs: {e}")

        finally:
            if response:
                response.close()
