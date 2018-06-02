import grequests, gevent
import gevent.time as time
from gevent.pool import Pool
from gevent.queue import Queue
from requests import exceptions


class Strategy(object):
    class Strict(object):
        def retry(self, try_count, exception):
            if isinstance(exception, exceptions.Timeout) or\
               isinstance(exception, exceptions.HTTPError):
                if try_count < 3:
                    return 2
                else:
                    return -1
            return -1
    
    class Backoff(object):
        def retry(self, try_count, exception):
            if isinstance(exception, exceptions.Timeout) or\
               isinstance(exception, exceptions.HTTPError):
                # 0.5, 1, 2, 4, 8, 16, 32, 60, 60, 60, -1
                if try_count < 11:
                    return min(2**(try_count-2), 60)
                return -1
            else:
                if try_count == 1:
                    return 10
                return -1

class ThrottledSession(grequests.Session):
    """This class wraps Requests.session for rate-limiting, throttling, 
        and pooling. Built with Gevent and simplicity in mind.
        
    :kwarg int max_pool_size: The size to limit the gevent.Pool to.None 
                              for unlimited.
    :kwarg int delay_per_request: How long to pause in seconds between 
                                  each request. Pool size of 1 will block
                                  until the following request is finished.
    :kwarg tuple requests_over_time: 
    """

    def __init__(self, *args, **kwargs):
        self._pool = Pool(kwargs.pop('max_pool_size', None))
        self._delay = self._get_delay(kwargs.pop('delay_per_request',None),
                                      kwargs.pop('requests_over_time',None),
        )
        self._retries = kwargs.pop('retries', 0)
        self._strategy = kwargs.pop('strategy', Strategy.Strict())
        self._checkpoint = 0
        self._enqueued_request = Queue()
        self._close = False
        self._loop = gevent.spawn(self.run)
        super(ThrottledSession, self).__init__(*args, **kwargs)
    
    def _get_delay(self, delay, requests_over_time):
        if delay is None:
            if requests_over_time is None:
                return 0
            n_reqs, time_for_reqs = requests_over_time
            if n_reqs < 0 or time_for_reqs < 0:
                delay = 0
            delay = float(time_for_reqs) / n_reqs
        if delay < 0:
            delay = 0
        return delay

    def _wait(self, delay):
        if delay > 0:
            time.sleep(delay)

    def _send(self, *args, **kwargs):
        try_count = kwargs.pop('try_count')
        try_count += 1
        try:
            return super(ThrottledSession, self).send(*args, **kwargs)
        except Exception, e:
            delay = self._strategy.retry(try_count, e)
            if delay > 0:
                return self.send(try_count=try_count, delay=delay, *args, **kwargs) 
            return None

    def send(self, *args, **kwargs):
        try_count = kwargs.pop('try_count', -1)
        delay = kwargs.pop('delay', self._delay)
        request = self._pool.greenlet_class(self._send, try_count=try_count, *args, **kwargs)
        self._enqueued_request.put((request, delay))
        return request.get()
    
    def run(self):
        while not self._close:
            self._pool.wait_available()
            request, delay = self._enqueued_request.get()
            self._wait(delay)
            self._pool.start(request)
            
    def shutdown(self):
        self._close = True
        self._loop.kill()
        
    def __del__(self):
        self.shutdown()
