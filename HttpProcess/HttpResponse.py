__author__ = 'SPHCool'
from HttpPacket import HttpPacket

class HttpResponse(HttpPacket):
    def __init__(self, headers=None, body=''):
        super(HttpResponse, self).__init__(headers, body)
        HttpPacket.__init__(self, headers, body)
        # if headers.first_line != '':
        #     print headers.first_line
        # else:
        #     print 'first_line is None from HttpResponse'

    def response(self):
        return True

    def is_cacheable(self):
        status_code = int(self.get_header('Status-Code'))

        cache_directive = ''
        if self.has_header('Cache-Control'):
            cache_directive = self.get_header('Cache-Control')

        # proxy does not support Range and Content-Range
        # so that proxy does not cache response with 206 status code
        if status_code == 206:
            return False

        if status_code in (200, 203, 300, 301, 410):
            # proxy cannot cache response with 'private' directive
            if 'no-store' in cache_directive or 'private' in cache_directive:
                return False

            return True

        # status code except 200, 203, 300, 301, 410  MUST NOT be returned in a reply to a subsequent request
        # unless there are cache-control directives or another header(s) that explicitly allow it.
        can_cache_directive_list = ['max-age',
                                    's-maxage',
                                    'must-revalidate',
                                    'proxy-revalidate',
                                    'public']

        for directive in can_cache_directive_list:
            if directive in cache_directive:
                return True

        if self.has_header('Expires') or self.has_header('ETag') or self.has_header('Last-Modified'):
            return True

        return False
