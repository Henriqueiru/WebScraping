import os
from subprocess import Popen, PIPE
from get_port import get_port

import ujson as json
from typing import Optional

import websockets

from pygoclient.sockets import WebSocketRequest, WebSocketResponse

from random import randint


class GoClient:
    port: Optional[int] = None

    def __init__(self, path: str = None):
        self.serverExePath = path
        self.conn: Optional[websockets.WebSocketClientProtocol] = None
        self.host = "localhost"
        if GoClient.port is None:
            GoClient.port = get_port(randint(8500,9000))

        self.wss_process: Optional[Popen] = None

    def start(self, path: str, port: int = None):
        """
        Start the goclient WSS in a separate process
        :param path:
        :param port:
        :return started whether or not the process has been started successfully:
        """
        self.serverExePath = path
        port = port if port is not None else GoClient.port

        if not os.path.exists(self.serverExePath):
            raise Exception(f"Goclient path '{self.serverExePath}' not found")

        self.wss_process = Popen([self.serverExePath, str(port)], shell=True, stdout=PIPE, stderr=PIPE)
        stdout = str(self.wss_process.stdout.readline())
        print(stdout)   
        return stdout.startswith("b'Starting to listen")

    def stop(self):
        """
        Close the goclient WSS process
        :return:
        """
        if self.wss_process is not None:
            self.wss_process.terminate()

    async def connect(self, host: str = None, port: int = None):
        host = host if host is not None else self.host
        port = port if port is not None else GoClient.port
        self.conn = await websockets.connect(f"ws://{host}:{port}/client")

    async def _send(self, msg: str):
        await self.conn.send(msg)
        res = await self.conn.recv()
        return res

    async def send(self, request: WebSocketRequest):
        res = await self._send(request.to_json())
        resJson = json.loads(res)
        return WebSocketResponse(resJson["Id"], resJson["Response"], resJson["Error"])

    async def disconnect(self):
        await self.conn.close()
