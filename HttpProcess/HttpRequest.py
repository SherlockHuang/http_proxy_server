__author__ = 'SPHCool'
from HttpPacket import HttpPacket


class HttpRequest(HttpPacket):
    def __init__(self, headers=None, body=''):
        super(HttpRequest, self).__init__(headers, body)

    def get_protocol(self):
        return self.headers.get_header('Protocol')
