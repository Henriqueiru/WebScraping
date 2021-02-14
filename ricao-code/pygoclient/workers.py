import asyncio
import queue

from pygoclient import WebSocketRequest, GoClient
from threading import Thread

from pygoclient.log import log_info, log_error
from datetime import datetime


class RequestWorker(Thread):
    def __init__(self, name: str, input_queue: queue.Queue, output_queue: queue.Queue):
        super().__init__(daemon=True)
        self.idle = False
        self.idle_time = None
        self.name = name
        self.client = GoClient()
        self.input_queue = input_queue
        self.output_queue = output_queue
        # create new event loop for this thread
        # so that we can use it to create a new goclient conn for this worker
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def _print_error(self, exception: Exception):
        log_error(f"Error: " + str(exception), self.name)

    async def _init(self):
        await self.client.connect()

    def init(self):
        """
        Initialize this worker

        This will establish a new (as in 'fresh') connection to goclient!
        :return:
        """
        self.loop.run_until_complete(self._init())

    def _check_for_idle(self):
        self.idle = self.input_queue.qsize() == 0
        # store idle time when idle
        if self.idle and self.idle_time is None:
            self.idle_time = datetime.now()
        # reset idle time when not idle (anymore)
        elif not self.idle and self.idle_time is not None:
            self.idle_time = None

    async def _run(self):
        while True:
            self._check_for_idle()

            # pop http request from input queue
            log_info("Waiting for request", self.name)
            request = self.input_queue.get()

            # send request
            res = await self.send(request)

            # put response in output queue
            self.output_queue.put(res)

            # notify done
            self.input_queue.task_done()

    def run(self):
        self.loop.run_until_complete(self._run())
        # self.loop.run_forever()
        self.loop.close()

    async def _destroy(self):
        await self.client.disconnect()
        self.loop.stop()
        self.loop.close()

    def destroy(self):
        log_info("Destroying self", self.name)
        self.loop.create_task(self._destroy())

    async def send(self, request: WebSocketRequest):
        res = await self.client.send(request)
        return res
