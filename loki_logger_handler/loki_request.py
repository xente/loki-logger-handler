import requests
import gzip
import sys

try:
    from io import BytesIO as IO  # For Python 3
except ImportError:
    from StringIO import StringIO as IO  # For Python 2


class LokiRequest:
    """
    A class to send logs to a Loki server, with optional compression and custom headers.

    Attributes:
        url (str): The URL of the Loki server.
        compressed (bool): Whether to compress the logs using gzip.
        headers (dict): Additional headers to include in the request.
        session (requests.Session): The session used for making HTTP requests.
    """
    def __init__(self, url, compressed=False, additional_headers=None):
        """
        Initialize the LokiRequest object with the server URL, compression option, and additional headers.

        Args:
            url (str): The URL of the Loki server.
            compressed (bool, optional): Whether to compress the logs using gzip. Defaults to False.
            additional_headers (dict, optional): Additional headers to include in the request.
            Defaults to an empty dictionary.
        """
        self.url = url
        self.compressed = compressed
        self.headers = additional_headers if additional_headers is not None else {}
        self.headers["Content-Type"] = "application/json"
        self.session = requests.Session()

    def send(self, data):
        """
        Send the log data to the Loki server.

        Args:
            data (str): The log data to be sent.

        Raises:
            requests.RequestException: If the request fails.
        """
        response = None
        try:
            if self.compressed:
                self.headers["Content-Encoding"] = "gzip"
                buf = IO()
                with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                    f.write(data.encode("utf-8"))
                data = buf.getvalue()

            response = self.session.post(self.url, data=data, headers=self.headers)
            response.raise_for_status()

        except requests.RequestException as e:
            sys.stderr.write("Error while sending logs: {}\n".format(e))
            if response is not None:
                sys.stderr.write(
                    "Response status code: {}, "
                    "response text: {}, "
                    "post request URL: {}\n".format(
                        response.status_code, response.text, response.request.url
                    )
                )

        finally:
            if response:
                response.close()
