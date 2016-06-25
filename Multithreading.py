#-*-coding:utf-8-*- 
import threading
import time
   
class WorkerTask(object):
    """A task to be performed by the ThreadPool."""
    
    def __init__(self, function, args=()):
        self.function = function
        self.args = args       
   
    def __call__(self):  
        self.function(*self.args)
        #  爬虫状态
        self.status = self.function(*self.args).status        
 
class WorkerThread(threading.Thread):
    """A thread managed by a thread pool."""
    
    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.setDaemon(True)  # 设置为守护线程       
        self.pool = pool
        self.timeout = pool.timeout  # 超时设置
        self.busy = False
        self._started = False
        self._event = None
        
    def work(self):
        if self._started is True:
            if self._event is not None and not self._event.isSet():
                self._event.set()  # 将标识设为True
        else:
            self._started = True
            self.start()

    def run(self):
        " 重写父类run方法 "
        begintime = time.time()
        while True:
            self.busy = True
            while len(self.pool._tasks) > 0:
                try:
                    task = self.pool._tasks.pop()  #从列表移除并返回最后一个对象
                    task()
                    # 任务列表大小是否超标
                    if len(self.pool._tasks)>1000000:
                        self.pool.overburden = True
                        
                    # 将未完成的请求插入到任务列表
                    if task.status is False:
                        #self.pool._tasks.append(task)
                        self.pool._tasks.insert(0,task)                        
                        #raw_input("\nPress <Enter> To continue!")
                        
                    # 超时退出
                    if time.time()-begintime > self.timeout:
                        print u'\n 超时!'
                        break
                    
                except IndexError:
                    # Just in case another thread grabbed the task 1st.
                    pass
            # Sleep until needed again
            self.busy = False
            print '\n succeed !'
            if self._event is None:
                self._event = threading.Event()  
            else:
                self._event.clear()  # 将标识设为False
            self._event.wait()  # 堵塞线程，直到Event对象内部标识位被设为True或超时

class ThreadPool(object):
    """Executes queued tasks in the background."""  

    def __init__(self, max_pool_size=10,timeout =150):
        " max_pool_size=10,timeout =150 "
        self.max_pool_size = max_pool_size
        self.timeout = timeout
        self._threads = []  
        self._tasks = []  # 任务列表
        self.overburden = False
        
    def _addTask(self, task):
        self._tasks.append(task)
        
        worker_thread = None
        for thread in self._threads:
            if thread.busy is False:
                worker_thread = thread
                break
            
        if worker_thread is None and len(self._threads) <= self.max_pool_size:
            worker_thread = WorkerThread(self)
            self._threads.append(worker_thread)
            
        if worker_thread is not None:
            worker_thread.work()

    def addTask(self, function, args=()):
        "function, args=()"
        self._addTask(WorkerTask(function, args))

class GlobalThreadPool(object):  
    """ThreadPool Singleton class."""  

    _instance = None  

    def __init__(self):
        """Create singleton instance """
        if GlobalThreadPool._instance is None:
            # Create and remember instance
            GlobalThreadPool._instance = ThreadPool()  

    def __getattr__(self, attr):  
        """ Delegate get access to implementation """  
        return getattr(self._instance, attr)  

    def __setattr__(self, attr, val):  
        """ Delegate set access to implementation """  
        return setattr(self._instance, attr, val)
