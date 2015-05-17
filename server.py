__author__ = 'SPHCool'
import thread
import socket
from HttpProcess.HttpHeaders import HttpHeaders, CRLF
from HttpProcess.HttpRequest import HttpRequest
from HttpProcess.HttpResponse import HttpResponse


def req_proc_func(client_sock, ):
    try:
        client_req_file = client_sock.makefile()

        client_req_headers_str = ''
        for line in client_req_file:
            if line == CRLF:
                break
            client_req_headers_str += line

        client_req_headers = HttpHeaders(client_req_headers_str)

        client_req_content = client_req_file.read(client_req_headers.get_content_length())
        client_req = HttpRequest(client_req_headers, client_req_content)

        if client_req.is_empty():
            client_sock.close()
            return

        if client_req.get_header('Protocol').lower() != 'http':
            print '[ERROR]: client request protocol is not http'
            client_sock.close()
            return

        full_host = client_req.get_header('Host').split(':')
        origin_hostname = full_host[0]
        if len(full_host) == 2:
            origin_port = full_host[1]
        else:
            origin_port = '80'

        # origin_ip = socket.gethostbyname(client_req.get_header('Host'))
        # origin_port = client_req.get_header('Port')
        origin_ip = socket.gethostbyname(origin_hostname)

        origin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        origin_sock.connect((origin_ip, int(origin_port)))
        origin_sock.send(client_req.to_string())

        origin_resp_file = origin_sock.makefile()
        origin_resp_data = ''
        for line in origin_resp_file:
            if line == CRLF:
                break
            origin_resp_data += line

        origin_resp_header = HttpHeaders(origin_resp_data)

        client_sock.send(origin_resp_header.to_string() + CRLF)
        if origin_resp_header.has_header('Transfer-Encoding')  \
                and origin_resp_header.get_header('Transfer-Encoding') == 'chunked':
            while True:
                chunked_header = origin_resp_file.readline()
                chunked_length = int(chunked_header.strip(), 16)
                chunked_data = origin_resp_file.read(chunked_length + 2)

                client_sock.send(chunked_header + chunked_data)
                if chunked_length == 0:
                    break
        else:
            origin_resp_content = ''
            content_length = origin_resp_header.get_content_length()
            while content_length >= 1024:
                origin_resp_buffer = origin_resp_file.read(1024)
                origin_resp_content += origin_resp_buffer
                client_sock.send(origin_resp_buffer)
                content_length -= 1024

            origin_resp_buffer = origin_resp_file.read(content_length)
            origin_resp_content += origin_resp_buffer
            client_sock.send(origin_resp_buffer)
            origin_resp = HttpResponse(origin_resp_header, origin_resp_content)
            print client_req_headers.to_string(), origin_resp.headers.to_string()

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


def wait_socket_func(server_sock):
    while True:
        req_sock, address = server_sock.accept()
        thread.start_new(req_proc_func, (req_sock,))


def main_func(host_ip, port, conn_num):
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((host_ip, port))
        print 'bind successfully', host_ip, port
        server_sock.listen(conn_num)

        thread.start_new(wait_socket_func, (server_sock,))
        while True:
            in_str = raw_input()
            if in_str == 'quit':
                server_sock.close()
                break
    except KeyboardInterrupt:
        server_sock.close()


if __name__ == '__main__':
    test_site = 'www.baidu.com'
    test_port = 80
    host_port = 8080
    conn_num = 5

    host_ip = get_host_ip(test_site, test_port)
    main_func(host_ip, host_port, conn_num)

