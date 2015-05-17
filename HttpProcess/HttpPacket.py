__author__ = 'SPHCool'
from HttpHeaders import CRLF


class HttpPacket(object):
    def __init__(self, headers=None, body=''):
        self.headers = headers
        self.body = body

    def has_header(self, header_name):
        return self.headers.has_header(header_name)

    def get_header(self, header_name):
        return self.headers.get_header(header_name)

    def is_empty(self):
        if self.headers.is_empty() and self.body is '':
            return True

    def to_string(self):
        return self.headers.to_string() + CRLF + self.body