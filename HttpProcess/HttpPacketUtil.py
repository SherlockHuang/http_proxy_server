__author__ = 'SPHCool'
import HttpDefine
from HttpHeaders import HttpHeaders
from HttpRequest import HttpRequest
from HttpResponse import HttpResponse

CONTENT_BUFFER = 0


def construct_packet(packet_type, packet_file, op=None):
    packet_headers_str = ''
    for line in packet_file:
        if line == HttpDefine.CRLF:
            break
        packet_headers_str += line
    print packet_headers_str
    packet_headers = HttpHeaders(packet_headers_str)

    packet_content = ''
    if op is None or CONTENT_BUFFER != op:
        packet_content = packet_file.read(packet_headers.get_content_length())

    packet = None
    if packet_type == HttpDefine.REQUEST:
        packet = HttpRequest(packet_headers, packet_content)
    elif packet_type == HttpDefine.RESPONSE:
        packet = HttpResponse(packet_headers, packet_content)
    else:
        print 'Incorrect Type'

    return packet


def save_packet(packet, file_path):
    f = open(file_path)
    f.write(packet.to_string())
    f.flush()
    f.close()


