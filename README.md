grequests-throttler
------
A simple (g)Requests.session wrapper for throttling, rate-limiting, and retry strategies. This library requires Gevent, as the name implies.

example
-------
```
from throttler import ThrottledSession, Strategy

with ThrottledSession(delay_per_request=1,
                      strategy=Strategy.Backoff(),
                      as session:
    for i in range(5):
        response = session.send('http://example.com/', timeout=5)
        if response:
            print response.text
```

Check example.py for a more thorough example.
