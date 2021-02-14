from abc import abstractmethod, ABC
from threading import Thread
import queue

from pygoclient import WebSocketRequest
from pygoclient.log import log_info
from pygoclient.workers import RequestWorker
from datetime import datetime


class WorkerQueue(Thread, ABC):
    def __init__(self, max_tasks_per_worker, max_workers, max_worker_idle_time, max_queue_size):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.max_tasks_per_worker = max_tasks_per_worker
        self.max_workers = max_workers
        self.max_worker_idle_time = max_worker_idle_time  # in seconds
        self.workers: list[RequestWorker] = []

    def put(self, request: WebSocketRequest):
        """
        Add an item to queue
        :param request:
        :return:
        """
        self.queue.put(request)

    @abstractmethod
    def run(self):
        pass


class RequestQueue(WorkerQueue):
    def __init__(self, response_queue: queue.Queue = None, max_tasks_per_worker=30, max_workers=30,
                 max_worker_idle_time=480, max_queue_size=0):
        super().__init__(max_tasks_per_worker, max_workers, max_worker_idle_time, max_queue_size)
        self.response_queue = response_queue

    def set_response_queue(self, request_queue: queue.Queue):
        self.response_queue = request_queue

    def add_worker(self):
        """
       Add a worker to this queue

       When started, a worker will process requests that come into the queue
       :return:
       """
        name = f"worker-{str(len(self.workers) + 1)}"
        log_info("Adding worker " + name, "requests queue")
        worker = RequestWorker(name, self.queue, self.response_queue)
        worker.init()
        worker.start()
        self.workers.append(worker)
        log_info("Started worker " + name, "requests queue")

    def try_kill_idle_workers(self, count: int):
        if count == 0:
            return

        for worker in self.workers:
            if worker.idle and int((datetime.now() - worker.idle_time).total_seconds()) > self.max_worker_idle_time:
                worker.destroy()
                self.workers.remove(worker)
                count -= 1

    def run(self):
        """
        Run the request worker layer
        :return:
        """
        while True:
            workers_min = int(self.queue.qsize() / self.max_tasks_per_worker)
            workers_count = len(self.workers)

            # add another worker to the pool when a certain limit is reached
            # when max is set to 0, just use one worker for everything in total
            if self.max_tasks_per_worker == 0:
                if len(self.workers) == 0:
                    self.add_worker()
            elif workers_min >= workers_count and (self.max_workers == 0 or workers_count < self.max_workers):
                self.add_worker()
            # start killing workers if there are more than necessary
            # but make sure at least one worker remains
            # so that we don't loose to much time reconnecting to goclient for every new task session
            elif workers_min < workers_count and workers_count > 1:
                self.try_kill_idle_workers(workers_count - workers_min)
