__author__ = 'SPHCool'
from HttpPacket import HttpPacket
import re
import HttpDefine

class HttpRequest(HttpPacket):
    def __init__(self, headers=None, body=''):
        super(HttpRequest, self).__init__(headers, body)

        self.method = ''
        self.path = ''
        self.protocol = ''
        self.http_version = ''

        # if headers.get_first_line() != '':
        #     self.parse_request_line(headers.get_first_line())
        # else:
        #     print 'first_line is None from HttpRequest'
        if headers.first_line != '':
            self.parse_request_line(headers.first_line)
        # else:
        #     print 'first_line is None from HttpRequest'

    def get_protocol(self):
        return self.headers.get_header('Protocol')

    def parse_request_line(self, req_line):
        # print 'parse_request_line'
        # match = re.search(r'(\w+) (\w+)://([^/:]+):?([0-9]+)?/(\S*) (HTTP/[0-9.]+)', req_line)
        info_data = req_line.split(' ')
        method = info_data[0]
        req_uri = info_data[1]
        http_version = info_data[2].strip()

        # self.put('Method', method)
        # self.put('Http-Version', http_version)
        self.method = method
        self.http_version = http_version

        match = re.search(r'(\w+)://([^/:]+):?([0-9]+)?/(\S*)', req_uri)
        if not match:
            print 'not match'
            return

        # self.put('Protocol', match.group(1))
        self.protocol = match.group(1)
        port = match.group(3)
        if port is None:
            port = '80'
        # self.put('Port', port)
        if not self.has_header('Host'):
            self.put('Host', match.group(2) + ':' + port)

        path = match.group(4)
        if path is None:
            path = ''
        self.path = path

    def to_string(self):
        first_line = self.method + ' /' + self.path \
                + ' ' + self.http_version + HttpDefine.CRLF

        headers_str = first_line
        headers = self.headers.headers
        for header in headers:
            header_line = header + ': ' + headers[header] + HttpDefine.CRLF
            headers_str += header_line

        # print 'req to string'
        return headers_str + HttpDefine.CRLF + self.body

