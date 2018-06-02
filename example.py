from requests import Request
from throttler import ThrottledSession, Strategy

class HttpClient(object):

    def __init__(self, proxy=None, timeout=30, retries=0, headers={}):
        self.session = ThrottledSession(delay_per_request=1,
                                        retries=retries,
                                        strategy=Strategy.Backoff())
        self.headers = headers
        self.timeout = timeout

        if proxy is not None:
            self.session.proxies.update({
                            'http': 'http://%s'% proxy,
                            'https': 'http://%s'% proxy
                        })

    def get(self, url, **kwargs):
        return self.send(url, 
                         method='GET', **kwargs
        )

    def post(self, url, **kwargs):
        return self.send(url, 
                         method='POST', **kwargs
        )

    def send(self, url, method='GET', **kwargs):
        timeout = kwargs.get('timeout', self.timeout)
        prepped = Request(method,
                          url,
                          params=kwargs.get('params',None),
                          data=kwargs.get('fields',None),
                          files=kwargs.get('files',None),
                          headers=kwargs.get('headers',self.headers)
        ).prepare()

        try:
            response = self.session.send(
                           prepped,
                           timeout=timeout
            )
        except Exception, e:
            raise e
        else:
            if response:
                return response
