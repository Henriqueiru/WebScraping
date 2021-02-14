import ujson as json

from pygoclient.http import HttpRequest


class WebSocketRequest:
    def __init__(self, id: str, request: HttpRequest):
        self.Id: str = id
        self.Request: HttpRequest = request

    def to_json(self):
        #print("Done with request "+self.Request.to_json_dict()['Url'])
        return json.dumps({
            'Id': self.Id,
            'Request': self.Request.to_json_dict()
        })