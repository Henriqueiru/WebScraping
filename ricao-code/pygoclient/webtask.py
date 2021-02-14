import time
from abc import abstractmethod
from typing import Callable
import threading
from pygoclient.http import HttpResponse, Proxy
from pygoclient import ThreadManager, log_warning
from pygoclient.sockets import WebSocketResponse
from pygoclient.log import log_status

class WebTask:
    def __init__(self, var_global):
        """
        Base class for building sitescripts
        """
        self.thread_manager = ThreadManager.instance()
        self.task_processor = self.thread_manager.task_processor
        self.task_processor.set_unknown_response_handler(self.handle_unknown_responses)
        self._stop = False
        self.var_global = var_global
        # delays are in seconds
        self.retry_delay = 3
        self.monitor_delay = 3
        self.queue_delay = 10
    

    def start(self):
        """
        Start this task
        :return:
        """
        self._stop = False
        self.run()
        

    def stop(self):
        """
        Stop this task
        :return:
        """
        self._stop = True

    def wait_retry(self):
        time.sleep(self.retry_delay)

    def wait_monitor(self):
        time.sleep(self.monitor_delay)

    def wait_queue(self):
        time.sleep(self.queue_delay)

    @abstractmethod
    def run(self):
        """
        Entry point for running this task
        :return:
        """

    def handle_errors(self, err: str, response_callback : callable):
        """
        Called when a goclient returns a (fatal) error in a response

        By default stop() will be called and an unrecoverable error will be thrown!

        Override this method to customize its behaviour
        :param err:
        :return:
        """
        # self.stop()
        #raise Exception("Task failed with error: " + err)
        self.schedule_sleep_thread(response_callback)
        log_status('Example Error In Single Thread - Other Threads Should Continue Running But Are Being Blocked By This Sleep', 'FAILED', self.name, self.task_id)
        #thread = threading.Thread(target=self.schedule_sleep_thread,args=(response_callback, )) # create thread
        #thread.start()
        #self.var_global.tasks.append(thread)
        #self.var_global.add_threads_in_task(thread)

    def schedule_sleep_thread(self, method):
        time.sleep(1000)
        self.schedule(method)

    def handle_unknown_responses(self, response: WebSocketResponse):
        """
        Called when no response handler was registered for a scheduled task

        Normally this shouldn't happen, so by default a warning will be printed to console.

        Override this method to customize its behaviour
        :param response:
        :return:
        """
        log_status(f'Task Crashed Unknown Error', 'FAILED', self.name, self.task_id)
        # log_warning(f"No response handler registered for request with ID '{response.Id}'")
        # uncomment to dump response for debugging
        # log_warning(response.Response.body)

    def schedule(self, method: Callable):
        """
        Schedule a task to be processed by the task processor
        :param method:
        :return:
        """
        if not self._stop:
            request =  method()
            self.task_processor.add(request, method, self.handle_errors)