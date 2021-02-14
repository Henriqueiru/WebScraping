import ujson as json
from typing import Optional
from .proxy import Proxy


class HttpRequest:
    def __init__(self):
        self.HttpVersion: int = 2
        self.Url: str = ""
        self.Method: str = "GET"
        self.Headers: str = ""
        self.Body: str = ""
        self.Proxy: Optional[Proxy] = None
        self.Fingerprint: str = "Chrome83"
        self.Timeout: int = 15
        self.ProxyTimeout: int = 15
        self.Debug: bool = False
        self.DebugResponse: bool = False
        self.AlpnProtocols: str = ""
        self.TransferEncodingIdentity: bool = False

    def to_json_dict(self):
        if self.Debug:
            print(self.__dict__)
        if self.Proxy is not None:
            proxyJson = self.Proxy.__dict__
            requestJson = {**self.__dict__}
            del requestJson['Proxy']
            return {**requestJson, 'Proxy': proxyJson}

        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_json_dict())
