"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab N
- Names:
  - 
  - 

An HTTP client

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked, what you
   disliked, and any suggestions you have for improvement)





"""

# import the "socket" module -- not using "from socket import *" in order to selectively use items
# with "socket." prefix
import socket

# import the "regular expressions" module
import re


def main():
    """
    Tests the client on a variety of resources
    """

    # These resource request should result in "Content-Length" data transfer
    get_http_resource('http://www.httpvshttps.com/check.png', 'check.png')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://www.httpvshttps.com/',
                      'index.html')

    # HTTPS example. (Just for fun.)
    # get_http_resource('https://www.httpvshttps.com/', 'https_index.html')

    # If you find fun examples of chunked or Content-Length pages, please share them with us!


def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """

    # Parse the URL into its component parts using a regular expression.
    if url.startswith('https://'):
        use_https = True
        protocol = 'https'
        default_port = 443
    else:
        use_https = False
        protocol = 'http'
        default_port = 80
    url_match = re.search(protocol + '://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else default_port
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.
              format(host_name, host_port, host_resource))
        status_string = do_http_exchange(use_https, host_name.encode(), host_port,
                                         host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


def do_http_exchange(use_https, host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param use_https: True if HTTPS should be used. False if just HTTP should be used.
           You can ignore this argument unless you choose to implement the just-for-fun part of the
           lab.
    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to
           connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL
           after the domain name, including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """
    request_resource(host, port, resource)

    return 500  # Replace this "server error" with the actual status code


def request_resource(host, port, resource):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))
    address = b'GET ' + resource + b' HTTP/1.1\r\nHOST:' + host + b'\r\n\r\n'
    tcp_socket.send(address)
    b = True
    while (b):
        b = receive_resource(tcp_socket)
    tcp_socket.close()
    ##return response


def determine_chunked(data_socket, transfer_encoding_value, content_length):
    if transfer_encoding_value:
        read_chunked_body(data_socket)
        print('ISACHUNK')
    else:
        read_content_length(data_socket, content_length)
        print('NOTACHUNK')


def read_chunked_body(data_socket):
    calculate_length = b''
    x = 0
    while x < 100:
        x += 1
        calculate_length += next_byte(data_socket)
    """
    while not calculate_length.endswith(b'\r\n'):
        calculate_length += next_byte(data_socket)
    length = int(calculate_length.rstrip(b'\r\n'))
    if length != 0:
        read_chunk(data_socket, length)
        print('ischsunk')
        """
    print(calculate_length)


def read_chunk(data_socket, length):
    while length > 0:
        next_byte(data_socket)
        length -= 1
    print(next_byte(data_socket))
    pass


def read_content_length(data_socket, content_length):
    write_to_text_file(data_socket, "not_chunked", content_length)
    print('readsContentLenght')


def write_to_text_file(bytes_block, file_name, length):
    """
    - programed by Josiah Clausen
    - takes in a text block and the message number to write to a file and create one
    - the text block is converted to to bytes and writen to a byte file
    - a new text file is writen with increasing value such as 1.txt, 2.txt... and so on
    - if the server is restarted old files will be over written
    -:param String text_block: gets the text from the server in string form and writes it to a bytes file
    -:param int message_num: keeps track of the message being sent from 1, 2, 3..... etc is and int
    """
    out_file = open(file_name + ".txt", 'wb')
    out_file.write(bytes_block.recv(length))


def read_body(data_socket):
    pass


def read_line(data_socket):
    pass


def next_byte(data_socket):
    """
    Read the next byte from the socket data_socket.

    Read the next byte from the sender, received over the network.
    If the byte has not yet arrived, this method blocks (waits)
      until the byte arrives.
    If the sender is done sending and is waiting for your response, this method blocks indefinitely.

    :param data_socket: The socket to read from. The data_socket argument should be an open tcp
                        data connection (either a client socket or a server data socket), not a tcp
                        server's listening socket.
    :return: the next byte, as a bytes object with a single byte in it
    """
    return data_socket.recv(1)


def receive_resource(data_socket):
    b = read_status_line(data_socket)
    print(b)
    is_it_chunked, length = read_headers(data_socket)
    determine_chunked(data_socket, is_it_chunked, length)
    return False;


def read_status_line(data_socket):
    b = b''
    while not b.endswith(b'\r\n'):
        b += next_byte(data_socket)
    return b


def read_headers(data_socket):
    length = b''
    chunked = False
    no_more_headers = False
    while not no_more_headers:
        header_name = read_header_name(data_socket)
        if header_name == b'Transfer-Encoding:':
            chunked = read_header_value(data_socket)
            print(chunked)
        elif header_name == b'Content-Length':
            length = read_header_value(data_socket)
            print(length)
        elif header_name == b'\r\n':
            no_more_headers = False
        else:
            read_header_value(data_socket)
    return chunked, length


def read_header_name(data_socket):
    bytes = b''
    is_end = False
    while not bytes.endswith(b':') and not is_end:
        if bytes == b'\r\n':
            is_end = True
        else:
            bytes += next_byte(data_socket)

    print(bytes)

    return bytes, is_end


def check_header_importance(data_socket, header_name):
    if header_name == b'Transfer-Encoding:':
        return 0
    elif header_name == b'Content-Length:':
        return 1
    pass


def read_header_value(data_socket):
    byte = b''
    while not byte.endswith(b'\r\n'):
        byte += next_byte(data_socket)
    return byte


def no_more_headers():
    pass


# Define additional functions here as necessary
# Don't forget docstrings and :author: tags


main()
