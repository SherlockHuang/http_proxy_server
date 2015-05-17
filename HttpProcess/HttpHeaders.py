__author__ = 'SPHCool'
import cStringIO
import re


CRLF = '\r\n'


def is_request(first_line):
    if first_line.startswith('HTTP'):
        return False
    else:
        return True


class HttpHeaders(object):
    REQUEST = 0
    RESPONSE = 1

    def __init__(self, headers=''):
        self.headers = {}

        if headers == '':
            return

        f_headers = cStringIO.StringIO(headers)
        first_line = f_headers.readline()

        # request or response
        if is_request(first_line):
            self.parse_request_line(first_line)
            self.type = HttpHeaders.REQUEST
        else:
            self.parse_status_line(first_line)
            self.type = HttpHeaders.RESPONSE

        for line in f_headers:
            pair = line.split(':')

            # header field name
            k = pair[0].strip()

            # header field value
            if len(pair) == 2:
                v = pair[1].strip()
            elif len(pair) > 2:
                v = ':'.join(pair[1:]).strip()

            self.headers[k] = v

    def parse_request_line(self, req_line):
        # match = re.search(r'(\w+) (\w+)://([^/:]+):?([0-9]+)?/(\S*) (HTTP/[0-9.]+)', req_line)
        info_data = req_line.split(' ')
        method = info_data[0]
        req_uri = info_data[1]
        http_version = info_data[2].strip()

        self.put('Method', method)
        self.put('Http-Version', http_version)

        match = re.search(r'(\w+)://([^/:]+):?([0-9]+)?/(\S*)', req_uri)
        if not match:
            print 'not match'
            return

        self.put('Protocol', match.group(1))

        port = match.group(3)
        if port is None:
            port = '80'
        self.put('Port', port)
        self.put('Host', match.group(2) + ':' + port)

        path = match.group(4)
        if path is None:
            path = ''
        self.put('Path', path)

    def parse_status_line(self, status_line):
        info_data = status_line.split(' ')
        http_version = info_data[0]
        status_code = info_data[1]
        reason_phrase = ' '.join(info_data[2:]).strip()

        self.put('Http-Version', http_version)
        self.put('Status-Code', status_code)
        self.put('Reason-Phrase', reason_phrase)

    def put(self, k, v):
        if v is not None:
            self.headers[k] = v
            return True
        else:
            return False

    def get_content_length(self):
        if 'Content-Length' in self.headers:
            return int(self.headers['Content-Length'])
        else:
            return 0

    def is_empty(self):
        return len(self.headers) == 0

    def to_string(self):
        first_line = ''
        if self.type is HttpHeaders.REQUEST:
            first_line = self.headers['Method'] + ' /' + self.headers['Path'] \
                + ' ' + self.headers['Http-Version'] + CRLF
        else:
            first_line = self.headers['Http-Version'] + ' ' + self.headers['Status-Code'] \
                + ' ' + self.headers['Reason-Phrase'] + CRLF

        headers_str = first_line
        for header in self.headers:
            header_line = header + ': ' + self.headers[header] + CRLF
            headers_str += header_line

        return headers_str

    def has_header(self, header_name):
        return header_name in self.headers

    def get_header(self, header_name):
        return self.headers[header_name]