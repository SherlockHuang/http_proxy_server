__author__ = 'SPHCool'
from HttpPacket import HttpPacket
import HttpDefine
import time

class HttpResponse(HttpPacket):
    def __init__(self, headers=None, body=''):
        super(HttpResponse, self).__init__(headers, body)

        self.http_version = ''
        self.status_code = ''
        self.reason_phrase = ''

        if headers.first_line != '':
            self.parse_status_line(headers.first_line)
        else:
            print 'first_line is None from HttpResponse'

    def parse_status_line(self, status_line):
        info_data = status_line.split(' ')
        self.http_version = info_data[0].strip()
        self.status_code = info_data[1].strip()
        self.reason_phrase = ' '.join(info_data[2:]).strip()

    def is_cacheable(self):
        status_code = int(self.status_code)
        cache_directive = ''
        if self.has_header('Cache-Control'):
            cache_directive = self.get_header('Cache-Control')

        # proxy cannot cache response with 'private' or 'no-store' directive
        if 'no-store' in cache_directive or 'private' in cache_directive:
            return False

        # status code 200, 203, 300, 301, 410  SHOULD be returned in a reply to a subsequent request
        if status_code in (200, 203, 300, 301, 410):
            return True

        # status code except 200, 203, 300, 301, 410  MUST NOT be returned in a reply to a subsequent request
        # unless there are cache-control directives or another header(s) that explicitly allow it.
        if self.has_header('Expires') or self.has_header('ETag') or self.has_header('Last-Modified'):
            return True

        can_cache_directive_list = ['max-age',
                                    's-maxage',
                                    'must-revalidate',
                                    'proxy-revalidate',
                                    'public']
        for directive in can_cache_directive_list:
            if directive in cache_directive:
                return True
        return False

    def calculate_age(self):
        pass

    def to_string(self):
        return self.get_header_string() + HttpDefine.CRLF + self.body

    def get_header_string(self):
        first_line = self.http_version + ' ' + self.status_code \
            + ' ' + self.reason_phrase + HttpDefine.CRLF

        headers_str = first_line
        headers = self.headers.headers
        for header in headers:
            header_line = header + ': ' + headers[header] + HttpDefine.CRLF
            headers_str += header_line

        return headers_str

    # def set_response_time(self, response_time):
    #     self.response_time = response_time
