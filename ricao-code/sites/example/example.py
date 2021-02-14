import re
import ujson as json
import uuid
import random
from time import sleep
from typing import Optional

from pygoclient.http import HttpResponse, Proxy
from pygoclient.http.requestbuilder import RequestBuilder
from pygoclient.log import log_status
from pygoclient.webtask import WebTask

from random import randint

class Example(WebTask):
    def __init__(self, var_global, id):
        super().__init__(var_global)
        self.name = "Example"
        self.task_id = str(randint(0,999))
        self.task_id_main = id
       # self.var_global = var_global

        self.request = RequestBuilder() \
            .set_fingerprint("Chrome_83") \
            .set_http_version(2) \
            .set_headers({
                ":method": "GET",
                ":authority": "www.offspring.co.uk",
                ":scheme": "https",
                ":path": "/",
                "upgrade-insecure-requests": 1,
                "dnt": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
                "accept": "*/*",
                "origin": "https://www.offspring.co.uk",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-language": "*/*"
            })

    # overrides parent stop() method just so we can log to console
    def stop(self):
        self._stop = True
        log_status('Task Stopped', 'FAILED', self.name, self.task_id)

    # entrypoint
    def run(self):
        log_status('Starting Task', 'INITIALIZING', self.name, self.task_id)
        self.schedule(self.example_request)
        

    def example_request(self, response: Optional[HttpResponse] = None):
        if response is None:
            return self.request \
                .set_url("https://www.offspring.co.uk/") \
                .set_method("GET") \
                .build()
            
            
        log_status('Task Completed Request', 'FINISHED', self.name, self.task_id)
        return self.schedule(self.example_request)