"""
track.transport
~~~~~~~~~~~~~~~

:copyright: (c) 2013 Simon Zimmermann.
:copyright: (c) 2010-2012 by the Sentry Team.
"""
from __future__ import absolute_import

import atexit
import logging
import os
import requests
import threading
import time

from .compat import Queue

DEFAULT_TIMEOUT = 10

logger = logging.getLogger('track.errors')

class AsyncWorker(object):
    _terminator = object()

    def __init__(self, shutdown_timeout=DEFAULT_TIMEOUT):
        self._queue = Queue(-1)
        self._lock = threading.Lock()
        self._thread = None
        self.options = {
            'shutdown_timeout': shutdown_timeout,
        }
        self.start()

    def main_thread_terminated(self):
        size = self._queue.qsize()
        if size:
            timeout = self.options['shutdown_timeout']
            print("Sentry is attempting to send %s pending error messages" % size)
            print("Waiting up to %s seconds" % timeout)
            if os.name == 'nt':
                print("Press Ctrl-Break to quit")
            else:
                print("Press Ctrl-C to quit")
            self.stop(timeout=timeout)

    def start(self):
        """
        Starts the task thread.
        """
        self._lock.acquire()
        try:
            if not self._thread:
                self._thread = threading.Thread(target=self._target)
                self._thread.setDaemon(True)
                self._thread.start()
        finally:
            self._lock.release()
            atexit.register(self.main_thread_terminated)

    def stop(self, timeout=None):
        """
        Stops the task thread. Synchronous!
        """
        self._lock.acquire()
        try:
            if self._thread:
                self._queue.put_nowait(self._terminator)
                self._thread.join(timeout=timeout)
                self._thread = None
        finally:
            self._lock.release()

    def queue(self, callback, *args, **kwargs):
        self._queue.put_nowait((callback, args, kwargs))

    def _target(self):
        while 1:
            record = self._queue.get()
            if record is self._terminator:
                break
            callback, args, kwargs = record
            try:
                callback(*args, **kwargs)
            except Exception:
                logger.error('Failed processing job', exc_info=True)

            time.sleep(0)

class HTTPTransport(object):
    async = False

    def __init__(self, timeout=None):
        self.timeout = timeout or 1.0

    def send(self, url, data, headers):
        res = requests.post(url, data=data, headers=headers, timeout=self.timeout)
        res.raise_for_status()

class ThreadedHTTPTransport(HTTPTransport):
    async = True

    def get_worker(self):
        if not hasattr(self, '_worker'):
            self._worker = AsyncWorker()
        return self._worker

    def send_sync(self, url, data, headers, success_cb=None, failure_cb=None):
        try:
            super(ThreadedHTTPTransport, self).send(url, data, headers)
        except Exception as e:
            if failure_cb:
                failure_cb(e)
        else:
            if success_cb:
                success_cb()

    def async_send(self, url, data, headers, success_cb=None, failure_cb=None):
        self.get_worker().queue(self.send_sync, url, data, headers,
            success_cb=success_cb, failure_cb=failure_cb)
