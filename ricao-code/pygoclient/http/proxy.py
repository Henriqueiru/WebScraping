import ujson as json


class Proxy:
    def __init__(self, host: str, port: int, username: str = None, password: str = None):
        self.Host = host
        self.Port = port
        self.Username = username
        self.Password = password
        self.Protocol = "http"

    def to_json(self):
        return json.dumps(self.__dict__)
