__author__ = 'SPHCool'
import HttpDefine
from HttpHeaders import HttpHeaders
from HttpRequest import HttpRequest
from HttpResponse import HttpResponse
import time
import os
import random

CONTENT_BUFFER = 0
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
PATH = '/'

def construct_packet(packet_type, packet_file, op=None):
    packet_headers_str = ''
    for line in packet_file:
        if line == HttpDefine.CRLF:
            break
        packet_headers_str += line
    # print packet_headers_str
    packet_headers = HttpHeaders(packet_headers_str)

    packet_content = ''
    if op is None or CONTENT_BUFFER != op:
        packet_content = packet_file.read(packet_headers.get_content_length())

    packet = None
    if packet_type == HttpDefine.REQUEST:
        # if packet_headers.first_line != '':
        #     print 'first_line is not None :' + packet_headers.first_line
        # else:
        #     print 'first_line is None from con req -- ' + packet_headers_str
        packet = HttpRequest(packet_headers, packet_content)
    elif packet_type == HttpDefine.RESPONSE:
        packet = HttpResponse(packet_headers, packet_content)
        # print packet_headers_str
        # if packet_headers.first_line != '':
        #     print packet_headers.first_line
        # else:
        #     print 'first_line is None from con resp'
    else:
        print 'Incorrect Type'

    return packet

def int_time(time_str):
    t = time.strptime(time_str, TIME_FORMAT)
    return time.mktime(t)

def str_time(time_int):
    return time.strftime(TIME_FORMAT, time_int)

def save_packet(packet, file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    f = open(file_path, 'w')
    f.write(packet.to_string())
    f.flush()
    f.close()

def random_str():
    return ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g',
                                'f','e','d','c','b','a'],5))


