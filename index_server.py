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

port = 6000                    # Reserve a port for your service.
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

    if data_type == 'R':# check data_type
        data = pdu.data_type #local variable for the data
        p_peer_name = data.get('peer name') #Local variable for peer name
        p_file_name = data.get('file_name') #local variable for file name
        p_peer_address = data.get('address') #local variable for address

        already_exists = False #setting a boolean variable to false
        for i in fList: #for loop
            if i.peer_name == p_peer_name and i.file_name == p_file_name: #if statment for searching for the same file
                e_pdu = PDU('E',{'msg':'File already exists'}) #creates an error pdu
                b_pdu = pickle.dumps(e_pdu) #converts pdu to binary
                conn.send(b_pdu) #send pdu
                already_exists = True #setting boolean to true
                break #break from the if statement
        if not already_exists: #boolean set to false
            fList.append(Files_List(p_peer_name,p_file_name,p_peer_address)) #adds the list to fList
            a_pdu = PDU('A', {'msg':'Successfully registered '}) #creates Acknowledgement pdu
            b_pdu = pickle.dumps(a_pdu) #converts PDU to binary
            conn.send(b_pdu) #sends PDU


    if data_type == 'T':
        data = pdu.data #local variable for the data
        p_peer_name = data.get('peer_name') #Local variable for peer name
        p_file_name = data.get('file_name') #local variable for file name
        p_peer_address = data.get('address') #local variable for address
        toBeRemoved = Files_List(p_peer_name, p_file_name, p_peer_address) #puts it into a list

        try:
            fList.remove(toBeRemoved) #removes the peer name,file name and peer address
            a_pdu = PDU('A',{'msg':'Successfully De-registered'}) #creates A pdu
            b_pdu = pickle.dumps(a_pdu) #turns the pdu into bytes
            conn.send(b_pdu) #send the bytes

        except:
            e_pdu = PDU('E',{'msg':'File already De-registered'}) #creates E pdu
            b_pdu=pickle.dumps(e_pdu) #turns pdu into bytes
            conn.send(b_pdu) #send the pdu
        '''
        exists = False
        for i in fList:
            if i.peer_name == p_peer_name and i.file_name == p_file_name:
                e_pdu = PDU('E',{'msg':'File already exists'})
                b_pdu = pickle.dumps(e_pdu)
                conn.send(b_pdu)
                already_exists = True
        '''
        '''
        if not already_exists:
            fList.append(Files_List(p_peer_name, p_file_name, p_peer_address))
            a_pdu = PDU('A', {'msg': 'Successfully registered '})
            b_pdu = pickle.dumps(a_pdu)
            conn.send(b_pdu)
        '''
    if data_type == 'S':
        data = pdu.data #local variable for the data
        p_peer_name = data.get('peer_name') #Local variable for peer name
        p_file_name = data.get('file_name') #local variable for file name

        for i in fList: #create for loop
            if i.peer_name == p_peer_address and i.file_name == p_file_name: #if statement looking for file
                target = i #variable for found content
                break

        pdu = PDU('s',i)#create PDU
        b_pdu = pickle.dumps(pdu) #converts PDU to binary
        conn.send(b_pdu) #sends PDU

    if data_type == '0':
        menu = [] #creates an array
        for i in fList:  #creating a for loop
            menu.append((i.peer_name,i.file_name)) #adds the peer name and file name to the list
        pdu = PDU('O',menu) #creates a pdu
        b_pdu = pickle.dumps(pdu) #convert to bytes
        conn.send(b_pdu) #sends ths pdu

    # else ....

    print('Done sending')
    conn.send(b'Thank you for connecting')
    conn.close() # close the connection
