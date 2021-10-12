"""
- CS2911 - 051
- Fall 2021
- Lab 05
- Names:
  - Josiah Clausen
  - Elisha Hamp

An HTTP client

Introduction:
    This lab is designed to familiarize students with reading http packets and writing a tcp client. It does so by
requiring the students to code a client to make a tcp request to a tcp server. The students then must write code
to understand the values returned from the given http website. This includes reading a regular and chunked response,
along with reading header names and storing important values.


Summary:
    This lab challenged our understanding of how http headers are formatted and function. Getting the program to read
the file by individual bytes was easy enough and fun to accomplish, however working with the bytes and finding
ways to use them properly to get the desired output was difficult. There are no changes we would suggest.


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
    status_code = int(request_resource(host, port, resource, file_name))
    return status_code  # Replace this "server error" with the actual status code


def request_resource(host, port, resource, file_name):
    """
    :author Both
    Makes a client that sends a request to the server and then catches the response.
    :param host: website given to us by instructor
    :param port: connection port given by instructor
    :param resource: everything after domain name
    :param file_name: name of the file that will be created
    :return: status code received from website
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((host, port))
    address = b'GET ' + resource + b' HTTP/1.1\r\nHOST:' + host + b'\r\n\r\n'
    tcp_socket.send(address)
    status_code = receive_resource(tcp_socket, file_name)
    tcp_socket.close()
    return status_code


def determine_chunked(data_socket, transfer_encoding_value, content_length, file_name):
    """
    -author Josiah Clausen
    :param data_socket: this is the data socket from the website and is used to get bytes from it
    :param transfer_encoding_value: boolean for weather the information is chunked or not
    :param content_length: the content length just encase the information is not chunked
    :param file_name: name of the file with the extension
    :return:
    """
    if transfer_encoding_value:
        read_chunked_body(data_socket, file_name)
    else:
        read_content_length(data_socket, content_length, file_name)


def read_chunked_body(data_socket, file_name):
    """
    -author: Josiah Clausen
    -this method is used to read all the chunks in from the website it saves them to a byte object to be save and pushed
    -to a write file.
    :param data_socket: this is the data socket from the website and is used to get bytes from it
    :param file_name: name of the file with the extension
    :return:
    """
    whole_chunk = b''
    end_chunks = False
    while not end_chunks:
        calculated_length = get_chunk_length(data_socket)
        if calculated_length == b'':
            end_chunks = True
        else:
            whole_chunk += read_chunk(data_socket, calculated_length)
    write_to_text_file(whole_chunk, file_name)


def get_chunk_length(data_socket):
    """
    :author: Josiah Clausen
    :helper method designed to get the length of each chunk from the bytes
    read with the data socket.
    :param data_socket: received from website, used to read bytes
    :return: returns the length of the next chunk
    """
    calculated_length = b''
    while not calculated_length.endswith(b'\r\n'):
        calculated_length += next_byte(data_socket)
    calculated_length = calculated_length.replace(b'\r\n', b'')
    return calculated_length


def read_chunk(data_socket, length):
    """
    -author: Josiah Clausen
    :param data_socket: this is the data socket from the website and is used to get bytes from it
    :param length: is the length of the chunk that is being read
    :return: returns a byte object with all the bytes from that chunk
    """
    length_of_chunk = int(length, 16)
    chunk_information = b''
    while length_of_chunk > 0:
        chunk_information += next_byte(data_socket)
        length_of_chunk -= 1
    return chunk_information


def read_content_length(data_socket, content_length, file_name):
    """
    -author: Josiah Clausen
    :param data_socket: this is the data socket from the website and is used to get bytes from it
    :param content_length: the length of the whole HTTP get request
    :param file_name: name of the file with the extension
    :return:
    """
    body = read_body(data_socket, content_length)
    write_to_text_file(body, file_name)


def write_to_text_file(bytes_block, file_name):
    """
    - author: Josiah Clausen
    - takes in a text block and the message number to write to a file and create one
    - the text block is converted to to bytes and writen to a byte file
    - a new text file is writen with increasing value such as 1.txt, 2.txt... and so on
    - if the server is restarted old files will be over written
    -:param String text_block: gets the text from the server in string form and writes it to a bytes file
    -:param int message_num: keeps track of the message being sent from 1, 2, 3..... etc is and int
    """
    out_file = open(file_name, 'wb')
    out_file.write(bytes_block)


def read_body(data_socket, total_length):
    """
    :author: Josiah Clausen
    Reads the body of the website.
    :param data_socket: this is the data socket from the website and is used to get bytes from it
    :param total_length: used to get the total length of the body so it can be retrieved
    :return: a bytes object
    """
    length = int(total_length)
    body = b''
    while length > 0:
        length -= 1
        body += next_byte(data_socket)
    return body


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


def receive_resource(data_socket, file_name):
    """
    :author: Elisha Hamp
    Reads the status line and headers before reading the body.
    :param data_socket: socket from website where response is being received
    :param file_name: name of the file to be output
    :return: returns the status code
    """
    status_code = read_status_line(data_socket)
    is_it_chunked, length = read_headers(data_socket)
    determine_chunked(data_socket, is_it_chunked, length, file_name)
    return status_code


def read_status_line(data_socket):
    """
    :author: Elisha Hamp
    Reads through the end of the status line,
    splits it by spaces, and stores the status code.
    :param data_socket: socket from website where response is being received
    :return: the status code
    """
    b = b''
    while not b.endswith(b'\r\n'):
        b += next_byte(data_socket)
    b = b.split(b' ', -1)
    return b[1]


def read_headers(data_socket):
    """
    :author: Elisha Hamp
    Uses a while loop to read through every header in the response until it reaches
    a double carriage return, line feed.
    :param data_socket: socket from website where response is being received
    :return:
    """
    length = b''
    chunked = False
    no_more_headers = False
    while not no_more_headers:
        header_name = read_header_name(data_socket)
        chunked, length, no_more_headers = check_header_importance(header_name, data_socket,
                                                                   length, chunked, no_more_headers)
    return chunked, length


def check_header_importance(header_name, data_socket, length, chunked, no_more_headers):
    """
    :author: Elisha Hamp
    Checks to see if the head being read holds any values important to our lab.
    :param header_name: name of the header being checked
    :param data_socket: socket from website where response is being received
    :param length: The length of the body, if received
    :param chunked: boolean which is made true if the transfer encoding is chunked
    :param no_more_headers: false boolean that will be used to terminate the loop
    in read headers
    :return:
    chunked: True if transfer encoding is chunked
    length: Length of the body of the response
    no_more_headers: True if the header name is CRLF
    """
    if header_name == b'Transfer-Encoding:':
        chunked = read_header_encoding(data_socket)
    elif header_name == b'Content-Length:':
        length = read_header_value(data_socket)
    elif header_name == b'\r\n':
        no_more_headers = True
    else:
        read_header_value(data_socket)
    return chunked, length, no_more_headers


def read_header_name(data_socket):
    """
    :author: Elisha Hamp
    Uses a while loop to receive the header name in full as a byte literal.
    :param data_socket: socket from website where response is being received
    :return: header name as a byte literal
    """
    header_bytes = b''
    while not header_bytes.endswith(b':') and not header_bytes == b'\r\n':
        header_bytes += next_byte(data_socket)
    return header_bytes


def read_header_value(data_socket):
    """
    Uses a while loop to read the bytes between the end of a header's name
    and the end of the header value.
    :author: Elisha Hamp
    :param data_socket: socket from website where response is being received
    :return: header value as a byte literal
    """
    value_bytes = b''
    while not value_bytes.endswith(b'\r\n'):
        value_bytes += next_byte(data_socket)
    value_bytes = value_bytes.replace(b'\r\n', b'')
    return value_bytes


def read_header_encoding(data_socket):
    """
    Determines whether the encoding of the body is chunked
    :author: Elisha Hamp
    :param data_socket: socket from website where response is being received
    :return: True if the encoding is chunked
    """
    encoding_bytes = b''
    is_chunked = False
    while not encoding_bytes.endswith(b'\r\n'):
        encoding_bytes += next_byte(data_socket)
    encoding_bytes = encoding_bytes.replace(b'\r\n', b'')
    if encoding_bytes == b' chunked':
        is_chunked = True
    return is_chunked


# Define additional functions here as necessary
# Don't forget docstrings and :author: tags


main()
