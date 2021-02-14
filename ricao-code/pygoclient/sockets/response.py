import ujson as json

from pygoclient.http import HttpResponse


class WebSocketResponse:
    def __init__(self, id: str, response: dict = None, error: str = None):
        err_exists = error is not None and error != ""
        self.Error = error if err_exists else None
        self.Id = id
        self.Response: HttpResponse = None if err_exists else HttpResponse(response)

    def to_json(self):
        return json.dumps(self.__dict__)
