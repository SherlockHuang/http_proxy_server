__author__ = 'SPHCool'
import re
import thread
import time
import socket
import sys,os
from HttpProcess import HttpDefine
from HttpProcess import HttpPacketUtil
from HttpCache.HttpCache import HttpCache
from HttpCache.HttpCacheEntry import HttpCacheEntry
from HttpCache import HttpCacheComm


def req_proc_func(client_sock, cache):
    try:
        client_req_file = client_sock.makefile()
        client_req = HttpPacketUtil.construct_packet(HttpDefine.REQUEST, client_req_file)

        if client_req.is_empty():
            client_sock.close()
            return

        # if client_req.headers.first_line == '':
        #     print 'client_req first_line is None' + '\r\n' + client_req.to_string()
        # else:
        #     print 'client_req first_line: ' + client_req.headers.first_line

        # if client_req.get_header('Protocol').lower() != 'http':
        #     print '[ERROR]: client request protocol is not http'
        #     client_sock.close()
        #     return
        if client_req.protocol.lower() != 'http':
            print '[ERROR]: client request protocol is not http'
            client_sock.close()
            return

        full_host = client_req.get_header('Host').split(':')
        origin_hostname = full_host[0]
        if len(full_host) == 2:
            origin_port = full_host[1]
        else:
            origin_port = '80'

        origin_ip = socket.gethostbyname(origin_hostname)

        origin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        origin_sock.connect((origin_ip, int(origin_port)))
        origin_sock.send(client_req.to_string())
        # print 'client_req\r\n' + client_req.to_string()

        origin_resp_file = origin_sock.makefile()
        origin_resp = HttpPacketUtil.construct_packet(HttpDefine.RESPONSE, origin_resp_file, HttpPacketUtil.CONTENT_BUFFER)


        client_sock.send(origin_resp.to_string())
        if origin_resp.has_header('Transfer-Encoding')  \
                and origin_resp.get_header('Transfer-Encoding') == 'chunked':
            while True:
                chunk_header = origin_resp_file.readline()
                client_sock.send(chunk_header)

                chunk_header_data = chunk_header.split(';')
                chunk_size = int(chunk_header_data[0].strip(), 16)

                if chunk_size == 0:
                    while True:
                        chunk_data = origin_resp_file.readline()
                        client_sock.send(chunk_data)
                        if chunk_data == HttpDefine.CRLF:
                            break
                    break
                else:
                    chunk_data = origin_resp_file.read(chunk_size + 2)
                    client_sock.send(chunk_data)
        else:
            origin_resp_content = ''
            content_length = origin_resp.get_content_length()
            while content_length >= 1024:
                origin_resp_buffer = origin_resp_file.read(1024)
                origin_resp_content += origin_resp_buffer
                client_sock.send(origin_resp_buffer)
                content_length -= 1024

            origin_resp_buffer = origin_resp_file.read(content_length)
            origin_resp_content += origin_resp_buffer
            client_sock.send(origin_resp_buffer)
            origin_resp.body = origin_resp_content
        # if origin_resp.headers.first_line == '':
        #     print 'origin_resp first_line is None' + '\r\n' + origin_resp.to_string()
        # else:
        #     print 'origin_resp first_line: ' + origin_resp.headers.first_line
        # print client_req.headers.to_string(), origin_resp.headers.to_string()
        if origin_resp.is_cacheable():
            # print time.mktime(time.gmtime())
            host = client_req.get_header('Host')
            path = client_req.path
            cache_entry = HttpCacheEntry(host, path)
            cache.add_entry(cache_entry)
            file_path = HttpCacheComm.ROOT_PATH + os.sep + host + os.sep + HttpPacketUtil.random_str()\
                        + str(cache_entry.create_time)
            cache_entry.local_path = file_path
            HttpPacketUtil.save_packet(origin_resp, file_path)
            # print origin_resp.host,origin_resp.path
            print origin_resp.get_header_string()

        origin_resp_file.close()
        origin_sock.close()
        client_sock.close()
    except socket.timeout:
        print '[WARNING]: timeout'
    except socket.gaierror:
        print '[ERROR]: socket.gaierror: Errno -5 No address associated with hostname'
        print '[ERROR]: req_hostname = ' + client_req.get_header('Host')
    except socket.error:
        # just ignore the broken pipe error
        broken_pipe_no = 32
        if socket.errno != broken_pipe_no:
            raise


def get_host_ip(site, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((site, port))
    host_ip = sock.getsockname()[0]
    sock.close()

    return host_ip


def wait_socket_func(server_sock, cache):
    while True:
        req_sock, address = server_sock.accept()
        thread.start_new(req_proc_func, (req_sock,cache,))


def main_func(host_ip, port, conn_num, cache):
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((host_ip, port))
        print 'bind successfully', host_ip, port
        server_sock.listen(conn_num)

        thread.start_new(wait_socket_func, (server_sock,cache,))
        while True:
            in_str = raw_input()
            if in_str == 'quit':
                server_sock.close()
                break
            elif in_str == 'show_cache':
                for k1 in cache.cache_dir:
                    for k2 in cache.cache_dir[k1]:
                        print k1,k2
    except KeyboardInterrupt:
        server_sock.close()


if __name__ == '__main__':
    test_site = 'www.baidu.com'
    test_port = 80
    host_port = 8080
    conn_num = 5

    host_ip = get_host_ip(test_site, test_port)

    path = sys.path[0]
    print path
    HttpCacheComm.ROOT_PATH = path + os.sep + 'cache'
    print HttpCacheComm.ROOT_PATH
    cache = HttpCache()

    main_func(host_ip, host_port, conn_num, cache)

