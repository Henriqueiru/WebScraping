from urllib.parse import urlparse
from pygoclient.http import HttpRequest, Proxy


class RequestBuilder:
    def __init__(self):
        self.request = HttpRequest()
        self.headers = {}

    def set_http_version(self, version: int):
        if version > 2:
            raise Exception("HTTP version " + str(version) + " not supported!")

        self.request.HttpVersion = version

        return self

    def set_url(self, url: str):
        self.request.Url = url

        if ":authority" in self.headers:
            self.headers[":authority"] = urlparse(url).netloc
        if ":path" in self.headers:
            self.headers[":path"] = f"{urlparse(url).path}?{urlparse(url).query}"
        if ":scheme" in self.headers:
            self.headers[":scheme"] = urlparse(url).scheme

        return self

    def set_method(self, method: str):
        method = method.upper()

        if method not in ["GET", "POST", "PATCH", "PUT", "DELETE", "HEAD"]:
            raise Exception(f"invalid HTTP method {method}!")

        if ":method" in self.headers:
            self.headers[":method"] = method

        self.request.Method = method

        return self

    def add_header(self, header: str, value: str):
        self.headers[header] = value
        return self

    def set_header(self, header: str, value: str):
        return self.add_header(header, value)

    def set_headers(self, headers: dict):
        self.headers = headers
        return self

    def remove_header(self, header):
        del self.headers[header]
        return self

    def _build_headers(self):
        self.request.Headers = "\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        return self

    def set_body(self, body: str):
        self.request.Body = body
        return self

    def set_proxy(self, proxy: Proxy):
        self.request.Proxy = proxy
        return self

    def set_fingerprint(self, fp: str):
        self.request.Fingerprint = fp
        return self

    def set_timeout(self, timeout: int, proxy_timeout: int = None):
        self.request.Timeout = timeout

        if proxy_timeout is not None:
            self.request.ProxyTimeout = proxy_timeout

        return self

    def debug(self, enable: bool = True, debug_response: bool = False):
        self.request.Debug = enable
        self.request.DebugResponse = debug_response
        return self

    def set_alpn_protocols(self, *alpn_protocols: str):
        self.request.AlpnProtocols = ",".join(alpn_protocols)
        return self

    def transfer_encoding_identity(self, enable: bool = True):
        self.request.TransferEncodingIdentity = enable
        return self

    def to_json(self):
        return self.request.to_json()

    def build(self):
        self._build_headers()
        return self.request
