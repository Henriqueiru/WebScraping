import queue
from typing import Optional

from pygoclient import RequestQueue
from pygoclient.log import log_info
from pygoclient.tasks import TaskProcessor


class ThreadManager:
    __instance = None

    def __init__(self, request_queue: RequestQueue, response_queue: queue.Queue()):
        """
        Singleton class that stores all (background) thread objects for easy access
        :param request_queue:
        :param response_queue:
        """
        self.__instance: Optional[ThreadManager] = None

        if ThreadManager.__instance is not None:
            raise Exception("ThreadManager is a singleton and thus can't be instantiated like a regular object. Use the 'instance()' method instead!")
        else:
            log_info("Creating threads", "thread manager")

            self.response_queue = response_queue
            self.request_queue = request_queue
            if self.request_queue.response_queue is None:
                self.request_queue.set_response_queue(self.response_queue)
            self.task_processor = TaskProcessor(self.request_queue, self.response_queue)

            self.request_queue.start()
            self.task_processor.start()

            # store in singleton
            ThreadManager.__instance = self

    @staticmethod
    def instance(request_queue=None, response_queue=None):
        if ThreadManager.__instance is None:
            ThreadManager(request_queue, response_queue)

        # for some reason can't type the method directly, so we do this as a work-around instead then...
        instance: ThreadManager = ThreadManager.__instance

        return instance
