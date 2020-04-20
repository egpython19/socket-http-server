import socket
import sys
import traceback
import os
import mimetypes


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """ default response when server is able to meet client request """
    version = b'HTTP/1.1'
    code = b'200'
    code_description = b'OK'
    response_header = b" ".join((version, code, code_description))
    mime_content_type = b'Content-Type:' + mimetype
    line_separator = b'\r\n'
    blank_line = b''

    return line_separator.join([response_header,
                                mime_content_type,
                                blank_line,
                                body])


def response_method_not_allowed():
    """ response when the client sends a request other than GET """
    version = b'HTTP/1.1'
    code = b'405'
    code_description = b'Method Not Allowed'
    response_header = b" ".join((version, code, code_description))
    separator = b'\r\n'
    blank_line = b''
    notice = b'Error: ' + code + b' ' + code_description
    message = b'Only GET methods allowed on this server.'

    return separator.join([response_header + blank_line,
                           notice,
                           message])


def response_not_found():
    """ response when the requested page or resource is not found """
    version = b'HTTP/1.1'
    code = b'404'
    code_description = b'Not Found'
    response_header = b" ".join((version, code, code_description))
    separator = b'\r\n'
    blank_line = b''
    notice = b'Error: ' + code + b' ' + code_description
    message = b'Sorry. Could not find the page you wanted.'

    return separator.join([response_header + blank_line,
                           notice,
                           message])


def parse_request(request):
    """ parse method, path, version from client request, raise error if not GET """
    line_separator = "\r\n"
    argument_separator = " "
    method, path, version = \
        request.split(line_separator)[0].split(argument_separator)

    if method != "GET":
        raise NotImplementedError

    return path


def response_path(path):
    """
    If request is directory, return plain text mime type of file names at the / delimiter.
    If request is for a file resource, get the mime type and return the resource.
    """

    path = "webroot" + path

    is_directory = "." not in path
    
    if is_directory:
        try:
            separator = '\r\n'
            content = f'Directory of {path}:'

            for item in os.listdir(path):
                content += (separator+item)
            content = content.encode()
            mime_type = b"text/plain"
        except FileNotFoundError:
            raise NameError

    else:
        try:
            with open(path, 'rb') as f:
                content = f.read()
                mime_type = mimetypes.guess_type(path)[0]
                mime_type = mime_type.encode()
        except FileNotFoundError:
            raise NameError

    return content, mime_type


def server(log_buffer=sys.stderr):
    """ main http server function """
    address = 'localhost', 10000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen()

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                print('request received:\n{}\n\n'.format(request))

                try:
                    path = parse_request(request)
                    content, mimetype = response_path(path)
                    response = response_ok(body=content, mimetype=mimetype)
                except NotImplementedError:
                    response = response_method_not_allowed()
                except NameError:
                    response = response_not_found()

                conn.sendall(response)

            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


