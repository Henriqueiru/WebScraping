import queue
# import asyncio
import threading
from pygoclient import ThreadManager, RequestQueue, GoClient
import time
import sites.example.example as example

# loop = asyncio.get_event_loop()


class Mock():
    tasks = []
    global_var_threads = 0
    global_lock = threading.Lock() # global

    def change_var_in_threads(self, data):  
        
        global global_var_threads 
        with self.global_lock:
            self.global_var_threads = data + self.global_var_threads

    def add_threads_in_task(self, thread):  
        
        global global_var_threads 
        with self.global_lock:
            self.tasks.append(thread) 

def execute_task(i, var_global):   # this is a example of use
    global global_var_threads
    task = example.Example(var_global, i) #This is what needs to run in async
    task.start()

def main():
    goclient = GoClient()

    if not goclient.start(r'C:\Users\User\Downloads\server.exe'): #Websocket server
        raise Exception("Failed to start goclient WSS!")

    ThreadManager(RequestQueue(max_tasks_per_worker=2), queue.Queue())
    
    var_global = Mock()

    for i in range(0,1000):
        thread = threading.Thread(target=execute_task,args=(i, var_global)) # create thread
        thread.start() # start thread
       # var_global.tasks.append(thread)
        var_global.add_threads_in_task(thread)

    for x in var_global.tasks: # wait all thread finish to continue
        x.join()
main()

