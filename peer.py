# peer.py
"""
A P2P client
It provides the following functions:
- Register the content file to the index server (R)
- Contact the index server to search for a content file (D)
    - Contact the peer to download the file
    - Register the content file to the index server
- De-register a content file (T)
- List the local registered content files (L)
- List the on-line registered content files (O)
"""
import socket  # Import socket module
from collections import namedtuple
import select
import pickle
import os

s = socket.socket(socket.SOCK_DGRAM)  # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 60000  # Reserve a port for your service.

s.connect((host, port))
# client is connected to the server
# define the PDU
PDU = namedtuple('PDU', ['data_type', 'data'])
regFiles = []


# Functions
def select_name():  # function for registering a username
    return input('Please enter preferred username:')


def de_register(s, username, filename):  # function to de-register a file from the index server
    t_pdu = PDU('T', {'peer_name': username,
                      'file_name': filename})  # create T type PDU convert it to binary and send to index server
    b_t_pdu = pickle.dumps(t_pdu)
    s.send(b_t_pdu)
    b_conf_pdu = s.recv()  # Receive reply PDU and parse it
    reply_pdu = pickle.loads(b_conf_pdu)

    if reply_pdu.data_type == 'A':
        print('successfully removed from the list')
        regFiles.remove(filename)

    elif reply_pdu.data_type == 'E':
        print(conf_pdu.data)


def download_file(file_name, address, destination):
    ip = address[0]  # extract address and port_number
    port_number = address[1]
    ds = socket.socket()  # create socket for connection
    ds.connect((ip, port_number))
    # establish new TCP connection
    pdu = PDU('D', file_name)
    b_pdu = pickle.dumps(pdu)
    # create a 'D' type pdu asking for the file
    ds.send(b_pdu)
    # send pdu to peer address (destination)
    r_b_pdu = ds.recv()
    r_pdu = pickle.loads(r_b_pdu)
    data_type = r_pdu.data_type
    if data_type == 'E':
        print('File does not exist anymore')
    elif data_type == 'C':
        with open(destination + filename) as f:
            f.write(r_pdu.data)
    # receive the data
    # it should be 'C' type
    # write to the file


##################


# select username
username = select_name()

# create a server to listen to the file requests
'''
Here we config the server capability of the peers. As a server we need to specify ip address and ports. Since all the 
peers are inside the local network (IP=127.0.0.1), we need to use unique port numbers for each peers so they can
bind socket successfully. This can be done by generating random numbers and using try/except command to bind a socket.
Withing multiple attempt we can be sure that peer would eventually bind a socket with random port number. Here I do not
use this approach. Instead I asked the user to enter a port number manually. During the test, for each of the peers,
you will need to enter different port numbers for different peers. 
The '' for IP address means our server is listening to all IPs,
you can change it to socket.hostname instead like before.
'''
inputs = []
outputs = []
exp = []
ss = socket.socket()  # this is a TCP connection
serverPort = int(input('Please enter listening port number for the download server:'))
try:
    ss.bind(('', serverPort))
except Exception:
    pass
ss.listen(5)
inputs.append(ss)
exp.append(ss)

timeout = 1  # timeout for the select function, it's 1 second now, you can have fraction of a second using float
# number, example: timeout = 0.3
# service loop
while True:
    readable, writable, exceptional = select.select(inputs, outputs, exp)
    for sock in readable:  # check the incoming connection requests
        if sock is ss:
            fileReq_Socket, fileReq_addr = ss.accept()  # accept connection
            ss.recv()  # receive the request
            data = s.recv(100)
            new = pickle.loads(data)  # change it to namedtuple
            type = new.data_type  # extract data_type
            print(type)
            data = new.data  # extract data
            print(data)
            if type == 'D':  # check the file name (it should be 'D' type)
                c_pdu = PDU('C', {'msg': 'File does not exist'})  # creates E pdu
                b_c_pdu = pickle.dumps(e_pdu)  # turns pdu into bytes
                s.send(b_c_pdu)  # send the pdu
                break
            else: # if file doest not exist send 'E' pdu
                e_pdu = PDU('E', {'msg': 'File does not exist'})  # creates E pdu
                b_e_pdu = pickle.dumps(e_pdu)  # turns pdu into bytes
                s.send(b_e_pdu)  # send the pdu
                break

    command = str(input('Please choose from the list below:\n'
                        '[O] Get online list\n'
                        '[L] List local files\n'
                        '[R] Register a file\n'
                        '[T] De-register a file\n'
                        '[Q] Quit the program\n'))

    if command == 'O':  # List index data from server
        o_pdu = PDU('O', ['', ''])  # create O type PDU and send it to index server
        b_o_pdu = pickle.dumps(o_pdu)
        s.send(b_o_pdu)

        reply_pdu = s.recv()
        reply = pickle.loads(reply_pdu)
        print(*reply.data, sep='\n')

        file_name = input('Please type the desired filename')
        peer = input("Please input the peer's name")
        # Send S type PDU to establish peer to peer connection
        s_pdu = PDU(data_type='S', data={'peer_name': peer, 'file_name': file_name})
        b_s_pdu = pickle.dumps(s_pdu)
        s.send(b_s_pdu)

        reply_pdu = s.recv()  # Get reply PDU for connection and send data to download file function
        reply = pickle.loads(reply_pdu)
        address = reply.data.get('address')

        destination = './'
        download_file(file_name, address, destination)

    if command == 'L':  # lists local files
        # list local files
        print(os.listdir('.'))

    if command == 'R':  # Register new file to index server
        filename = input('Please input file name to be registered: ')
        # Create R type PDU to register to the index server and send it
        r_PDU = PDU(data_type='R',
                    data={'peer_name': username, 'file_name': filename, 'IPaddress': host, 'portnumber': serverPort})
        b_r_PDU = pickle.dumps(r_PDU)
        s.send(b_r_PDU)

        b_recv_PDU = s.recv()  # Receive response from index server and parse the PDU
        conf_pdu = pickle.loads(b_recv_PDU)

        if conf_pdu.data_type == 'A':  # Ack received  and successful registration
            print('successfully Added to the list')
            regFiles.append(filename)

        elif conf_pdu.data_type == 'E':
            while conf_pdu.data_type == 'E':  # a used may need to retry multiple times to register a username on
                # server!
                print(conf_pdu.data)
                # ask user to change username
                username = select_name()
                r_PDU = PDU(data_type='R',
                            data={'peer_name': username, 'file_name': filename, 'address': (host, serverPort)})
                b_r_PDU = pickle.dumps(r_PDU)
                ss.send(b_r_PDU)

            print('successfully Added to the list')
            regFiles.append(filename)
            # send 'R' pdu
            # receive response
            # extract data_type

        # get the file name
        # create 'R' pdu using username, filename, IPaddress and portnumber
        # send 'R' pdu
        # receive response pdu
        # if 'A', done
        # else if 'E',

    if command == 'T':  # De-register file from index server
        # get the file name from user
        de_register(username, input('Please enter file name to be de-registered: '))

    if command == 'Q':
        # for all the registered files:
        for fname in regFiles:
            de_register(s, username, fname)
        # quit the program
        s.close()
