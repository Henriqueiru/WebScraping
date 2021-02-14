import queue
import asyncio
from threading import Thread
from typing import Callable, Optional, Union
from uuid import uuid4

from pygoclient import RequestQueue, WebSocketResponse, WebSocketRequest
from pygoclient.http import HttpRequest, HttpResponse

class ResponseHandler:
    def __init__(self, id: str, callback: Callable[[HttpResponse], Optional[HttpRequest]],
                 error_handler: Callable[[str], None] = None):
        self.id = id
        self.response_callback = callback
        self.error_handler = error_handler


class TaskProcessor(Thread):
    def __init__(self, request_queue: RequestQueue, response_queue: queue.Queue):
        """
        Class that 'glues' request and response states together
        :param request_queue:
        :param response_queue:
        """
        super().__init__()
        self.daemon = True
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.response_handlers: list[ResponseHandler] = []
        self.unknown_response_handler: Optional[Callable[[WebSocketResponse], None]] = None

    def add(self, request: Union[HttpRequest, WebSocketRequest],
            response_callback: Callable[[HttpResponse], Optional[HttpRequest]],
            error_handler: Callable[[str], None] = None):
        """
        Add a request that should be processed by given response handler
        :param error_handler:
        :param request:
        :param response_callback:
        :return:
        """
        # create websocket request with random id if the request is a plain http request without identifier
        if isinstance(request, HttpRequest):
            id = str(uuid4())
            request = WebSocketRequest(id, request)
        if request:
            self.response_handlers.append(ResponseHandler(request.Id, response_callback, error_handler))
            self.request_queue.put(request)

    def set_unknown_response_handler(self, handler: Callable[[WebSocketResponse], None]):
        """
        Callback that will be called once a response has been received with an identifier that doesn't match
        any of the registered response handlers
        :param handler:
        :return:
        """
        self.unknown_response_handler = handler

    def run(self):
        while True:
            ws_response: WebSocketResponse = self.response_queue.get()

            id = ws_response.Id
            handler = next((handler for handler in self.response_handlers if handler.id == id), None)

            ws_response.Error = "Example" #Replicate error for example
            if handler is not None and ws_response.Error is not None:
                handler.error_handler(ws_response.Error, handler.response_callback)
            # execute response callback
            elif handler is not None:
                handler.response_callback(ws_response.Response)
                self.response_handlers.remove(handler)
            else:
                self.unknown_response_handler(ws_response)
