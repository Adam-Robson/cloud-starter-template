from typing import Any


class HttpClientError(Exception):
    '''Base for every error raised by an HTTP client.'''


class HttpStatusError(HttpClientError):
    '''The upstream service answered with a non-2xx status.'''

    def __init__(
        self, method: str, url: str, status_code: int, body: Any
    ) -> None:
        super().__init__(f'{method} {url} returned {status_code}')
        self.method = method
        self.url = url
        self.status_code = status_code
        self.body = body


class HttpTransportError(HttpClientError):
    '''The request never got a response (timeout, connection failure).'''

    def __init__(self, method: str, url: str, cause: Exception) -> None:
        super().__init__(f'{method} {url} failed: {cause}')
        self.method = method
        self.url = url
