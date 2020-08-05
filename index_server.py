# index_server.py
'''
Index Server 
Message types:
R - used for registration
A - used by the server to acknowledge the success
Q - used by chat users for de-registration
D - download content between peers (not used here)
C - Content (not used here)
S - Search content
E - Error messages from the Server
'''

import socket                   # Import socket module
from collections import namedtuple
import pickle

port = 60000                    # Reserve a port for your service.
s = socket.socket(socket.SOCK_DGRAM)             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.
# server is up and listening
print('Server listening....')

PDU = namedtuple('PDU', ['data_type', 'data'])
Files_List = namedtuple('Files_List', ['peer_name', 'file_name', 'address'])
fList = [] # list of files, containing Files_List namedtuples


while True:
    conn, addr = s.accept()     # Establish connection with client.
    print(addr)
    # receiving the binary_pdu = conn.recv(100)
    # convert pdu from binary to pdu object using pickle
    binary_pdu = conn.recv(100)
    pdu = pickle.loads(binary_pdu)
    data_type = pdu.data_type # extract the type from pdu, type = pdu.data_type
    # check data_type

    if data_type == 'R':
        data = pdu.data_type
        p_peer_name = data.get('peer name')
        p_file_name = data.get('file_name')
        p_peer_address = data.get('address')

        already_exists = False
        for i in fList:
            if i.peer_name == p_peer_name and i.file_name == p_file_name:
                e_pdu = PDU('E',{'msg':'File already exists'})
                b_pdu = pickle.dumps(e_pdu)
                conn.send(b_pdu)
                already_exists = True
                break
        if not already_exists:
            fList.append(Files_List(p_peer_name,p_file_name,p_peer_address))
            a_pdu = PDU('A', {'msg':'Successfully registered '})
            b_pdu = pickle.dumps(a_pdu)
            conn.send(b_pdu)


    if data_type == 'T':
        data = pdu.data
        p_peer_name = data.get('peer_name')
        p_file_name = data.get('file_name')
        p_peer_address = data.get('address')
        toBeRemoved = Files_List(p_peer_name, p_file_name, p_peer_address)

        try:
            fList.remove(toBeRemoved)
            a_pdu = PDU('A',{'msg':'Successfully registered'})
            b_pdu = pickle.dumps(a_pdu)
            conn.send(b_pdu)
        '''
        exists = False
        for i in fList:
            if i.peer_name == p_peer_name and i.file_name == p_file_name:
                e_pdu = PDU('E',{'msg':'File already exists'})
                b_pdu = pickle.dumps(e_pdu)
                conn.send(b_pdu)
                already_exists = True
        '''
        except:
            e_pdu = PDU('E',{'msg':'File already exists'})
            b_pdu=pickle.dumps(e_pdu)
            conn.send(b_pdu)
        '''
        if not already_exists:
            fList.append(Files_List(p_peer_name, p_file_name, p_peer_address))
            a_pdu = PDU('A', {'msg': 'Successfully registered '})
            b_pdu = pickle.dumps(a_pdu)
            conn.send(b_pdu)
        '''
    if data_type == 'S':
        data = pdu.data
        p_peer_name = data.get('peer_name')
        p_file_name = data.get('file_name')

        for i in fList:
            if i.peer_name == p_peer_address and i.file_name == p_file_name
                target = i
                break

        pdu = PDU('s',i)
        b_pdu = pickle.dumps(pdu)
        conn.send(b_pdu)

    if data_type == '0':
        menu = []
        for i in fList:
            menu.append((i.peer_name,i.file_name))
        pdu = PDU('O',menu)
        b_pdu = pickle.dumps(pdu)
        conn.send(b_pdu)

    # else ....

    print('Done sending')
    conn.send(b'Thank you for connecting')
    conn.close() # close the connection
