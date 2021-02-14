import ujson as json
from typing import Union


class HttpResponse:
    def __init__(self, raw_response: dict):
        self.StatusCode: int = raw_response["StatusCode"]
        self.Headers: str = raw_response["Headers"]
        self.headers = self._parse_headers(self.Headers)
        self.body: Union[str, dict] = json.loads(raw_response["Body"]) if raw_response["Body"].startswith("{") else raw_response["Body"]

    def _parse_headers(self, raw_headers: str):
        headers = {}

        splitted_headers = raw_headers.split("\n")
        for header in splitted_headers:
            header = header.strip()

            if header == "":
                continue

            splitted = header.split(':')
            if header.startswith(':'):
                key = ":" + splitted[1]
                splitted.pop(1)
            else:
                key = splitted[0]
            splitted.pop(0)
            # some headers my include ':' idk just to be safe
            value = ":".join(splitted)

            if key in headers.keys():
                headers[key] = f"{headers[key]} {value.strip()}"
            else:
                headers[key] = value.strip()

        return headers

    def to_json(self):
        return json.dumps(self.__dict__)
