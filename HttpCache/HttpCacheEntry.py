__author__ = 'PsCool'
import time
from HttpProcess import HttpResponse

class HttpCacheEntry(object):
    def __init__(self, host, path, local_path='', frequent=0, lock=None):
        self.host = host
        self.path = path
        self.local_path = local_path
        self.frequent = frequent
        self.lock = None
        self.size = 0

        self.receive_age = 0
        self.create_time = time.mktime(time.gmtime())

    def set_response(self, response):
        self.response = response

    def get_response(self):
        return self.response

    def is_stale(self):
        return False

