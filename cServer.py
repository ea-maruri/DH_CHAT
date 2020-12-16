"""Script for representing a server for a chatting application.
    
    Uses Selectors for manage clients. Selectors is a module that allows a High-Level I/O multiplexing.
    events is a bitwise mask indicating which I/O events should be waited for on a given file object.
                Constant            Meaning
                EVENT_READ    -->   Available for read
                EVENT_WRITE   -->   Available for write"""


import socket
import selectors
import types
from cServer_Client import cServer_Client
from cServer_Room import cServer_Room
from sys import stderr
from datetime import datetime


class cServer:
    """Class for representing server-socket IPv4 (socket.AF_INET, socket.SOCK_STREAM)."""

    def __init__(self, host: str, port: int):
        """Initializes the tuple-socket 'ip:port', ensuring the input arguments be correct. 
        Creates the socket for server, a list to store users, a list to store rooms, 
        and a selector to manage users/clients."""

        # Trying to make a str the 'host' argument
        try:
            host = str(host)
        except ValueError as e:
            print("Error in __init__(host: str, port: int): Incorrect Type for 'host' argument.\n\t" + str(e), file=stderr)
            host = None  # To assign the IP later

        # An empty or invalid 'host' argument
        if host is None or host == "":
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host = s.getsockname()[0]  # IP for server
            print("Assigned IP, for hosting:", host)
            s.close()

        # Trying to make an int the 'port' argument
        try:
            port = int(port)
        except ValueError as e:
            print("Error in __init__(host: str, port: int): Incorrect Type for 'port' argument.\n\t" + str(e), file=stderr)
            port = None  # To assign the port later

        # An empty or invalid 'port' argument
        if port is None or port < 1024 or port > 65535:
            port = 9090
            print("Assigned PORT, for hosting:", port)

        # IP (as HOST) and PORT for server
        self.HOST = host
        self.PORT = port

        # Creating socket for server use
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.initialized = False

        # List of clients. Instances of cServer_Client(name: str, socket) class
        self.list_of_server_clients = list()
        self.number_of_clients = len(self.list_of_server_clients)  # Number of clients in server

        # List of rooms. Instances of cServer_Room(id: str, creator: str)
        self.rooms = list()

        # Selector for managing clients
        self.selector = selectors.DefaultSelector()

        # Requested IP
        self.requested_ip = ''


    def start_server(self):
        """Binding and listening for the socket server"""

        # May occur a problem with a given 'host' argument. Ex: "The requested address is invalid in this context"
        try:
            self.server_socket.bind((self.HOST, self.PORT))
        except OSError as error:
            print("Error (in start_server()) with given 'host' for server-socket: '" + self.HOST + "'\n\t" + str(error), file=stderr)
            return False
        
        self.server_socket.listen()
        self.server_socket.setblocking(False)
        self.initialized = True

        # server_socket registered in selector 'available to read' with no data associated
        self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)

        print("\nServer socket started in " + str(self.server_socket.getsockname()) + " at " + str(datetime.now()) + "\n")
        print("Listening...")

        return True


    def attend(self):
        """Indicates if 'accept' or 'service' a client"""
        while True:
            # Wait until some registered file objects become ready, or the timeout expires.
            # This returns a list of (key, events) tuples, one for each ready file object.
            events = self.selector.select(timeout=None)

            for key, mask in events:
                if key.data is None:  # I no exists in selector, accept it
                    self.accept_wrapper(key.fileobj)
                else:
                    self.service_connection(key, mask)  # Services to a client


    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('\tAccepted connection from', addr)
        
        conn.setblocking(False)

        # Creating a 'subclass' that provides attribute access to its namespace
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')

        # Possible events for client (Binary OR)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE  

        # conn registered in selector with 'available to read/write' events and data associated (addr, inb, outb)
        self.selector.register(conn, events, data=data)


    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data

        # If client available to read
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024).decode()  # Decoding Bytes Received from socket

            if recv_data:
                if recv_data[:3] != "QqQ":
                    header = recv_data[:5] # Header of receiving request (as String)
                    room_id = None

                    # WORKING WITH PRIMITIVES OR HEADERS to know what to do (requests from users/clients)
                    print("\nReceived:", header, "from client\n")

                    # Receives "SATARTUser_Name"
                    if header == "START":
                        # Adding the cServer_Client(name, socket) to the list
                        name = recv_data[5:]
                        self.list_of_server_clients.append(cServer_Client(name, sock))

                        self.broadcast(name + " has joined the chat!", self.list_of_server_clients)
                        data.outb += bytes("STARTWelcome, " + name + " " + str(data.addr[1]), encoding="utf-8")
                        recv_data = ""  # To not append more
                    
                    # A "clients in Server" request
                    elif header == "LIST1":
                        self.print_list_of_clients()
                        data.outb += bytes("LIST1" + self.get_clients_names_in_server(), encoding="utf-8")
                    
                    # A message received from main client GUI
                    elif header == "BROAD":
                        self.broadcast(recv_data[5:], self.list_of_server_clients)
                        recv_data = ""
                    
                    # "Create a Room" request
                    elif header == "PROOM":
                        # Create a room (cServer_Room(id, creator))
                        room_id = str(len(self.rooms) + 1).zfill(5)  # Used to return to user
                        room = cServer_Room(room_id, self.get_client_in_server(recv_data[5:]))
                        self.rooms.append(room)
                        print("Room created:", str(room))

                        recv_data += "," + room_id  # To return to client the created room ID

                    # "List clients in a room" request
                    elif header == "LROOM":
                        id = recv_data[5:]
                        self.print_list_of_clients_in_room(id)
                        data.outb += bytes("LROOM" + self.get_clients_in_room(id), encoding="utf-8")
                        recv_data = ""  # Clear recv_data because receive "LROOMid"

                    # "Add a user to a room" request
                    elif header == "ADUSR":
                        # Receive ADUSR,user,id
                        head, user_name, id_room = tuple(recv_data.split(","))
                        #data_rec = recv_data.split(",")
                        id_for_room = id_room
                                                
                        recv_data = ""
                        
                        for client in self.list_of_server_clients:
                            if client.get_name() == user_name:
                                print("Try to add to", client.get_name())
                                client.get_socket().send(bytes("ADDED," + str(id_for_room), encoding='utf8'))
                    
                    # "Send a group message" request
                    elif header == "LOCAL":
                        # Receive "LOCAL,id,self.name: msg
                        head, id_room, msg = tuple(recv_data.split(","))

                        for room in self.rooms:
                            if id_room == room.get_id():
                                clients_in_room = room.get_list_of_clients()  # List in room
                                self.broadcast(msg, clients_in_room)
                        
                        recv_data = ""

                    # "'Accept' of client to enter a private room"
                    elif header == "ADDME":
                        #Received ADDMME,id,self.name
                        received = recv_data.split(",")
                        for room in self.rooms:
                            if received[1] == room.get_id():
                                room.get_list_of_clients().append(cServer_Client(received[2], sock))

                    # Try to make a connection with DNS given a name
                    elif header == "TRYCO":
                        name = recv_data[5:]
                        HOST = "192.168.203.1"
                        PORT = 10001
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((HOST, PORT))
                            s.sendall(bytes('GIVIP' + name, encoding='utf-8'))
                            ip_data = s.recv(1024).decode()  # I receive: bytes("THEIP" + the_ip, encoding="utf-8")
                            print('THE DATA IS', ip_data)

                            if ip_data[:5] == "THEIP":
                                self.requested_ip = ip_data[5:]

                        recv_data = 'OBTAINED: ' + ip_data
                        print('Received', repr(ip_data))

                    elif header == "CONIP":
                        HOST = self.requested_ip.split(":")[0]
                        PORT = int(self.requested_ip.split(":")[1])
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((HOST, PORT))
                            s.sendall(bytes('START' + "NEW CONNECT", encoding='utf-8'))
                            received_data = s.recv(1024).decode()  # I receive: bytes("THEIP" + the_ip, encoding="utf-8")
                            print('THE DATA IS', received_data)


                    # Another "unsupported" Header
                    else:
                        print("'" + recv_data + "' is NOT a correct primitive")
                        data.outb += bytes("ERROR")
                        recv_data = ""

                    # To return to client
                    data.outb += bytes(recv_data, encoding="utf-8")

                # "Quit" request from client
                else:
                    print('\tClosing (by "QqQ") connection to', data.addr, '\n')
                    self.selector.unregister(sock)
                    self.remove_client(recv_data[3:])       
                    sock.close()

            else:
                print('\tClosing (by "unknown") connection to', data.addr, '\n')
                self.selector.unregister(sock)
                self.remove_client(recv_data[3:])              
                sock.close()

        # If client available to write
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('\tEchoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write

                data.outb = data.outb[sent:]
                data.outb = bytes("", encoding = 'utf8')


    def remove_client(self, name: str):
        """Remove a client from list_of_server_clients given a name"""
        print("Try to remove", name)
        for client in self.list_of_server_clients:
            if client.get_name() == name:
                print("Deleting to", name)
                del self.list_of_server_clients[self.list_of_server_clients.index(client)]


    def get_client_in_server(self, name:str):
        """Return a client in list_of_server_clients given a name"""
        print("Try to get", name)
        for client in self.list_of_server_clients:
            if client.get_name() == name:
                print("Returning to", name)
                return client

        return None


    def get_clients_in_room(self, id: str):
        """Returns a list of clients (separated by commas) in a given room, if exists"""
        print("ID recibido " + id)
        for room in self.rooms:
            if id == room.get_id():
                return str(room.get_list_of_names())
        
        return "NOT FOUND"


    def get_clients_names_in_server(self):
        """Returns the names of list_of_server_clients separated by commas"""
        list_of_clients_names_as_list = ""

        for client in self.list_of_server_clients:
            print(client.get_name())
            list_of_clients_names_as_list += client.get_name() + ","

        return str(list_of_clients_names_as_list[:-1])


    def print_list_of_clients(self):
        print("Listing clients:\n\t")
        print(self.get_clients_names_in_server())


    def print_list_of_clients_in_room(self, id: str):
        print("Listing clients in room:\n\t")
        print(self.get_clients_in_room(id))


    def broadcast(self, msg, list_of_clients):
        """For each client in (cServer_Client(name, socket)) in the list, send the message 'msg'"""
        for client in list_of_clients:
            client.get_socket().send(bytes(msg, encoding='utf8'))


    def __str__(self):
        if self.initialized:
            return "Server socket at (" + self.HOST + ":" + str(self.PORT) + ")"
        else:
            return "Server socket has not started yet."


if __name__ == "__main__":
    IP = socket.gethostname()   # "192.168.x.x"
    PORT = "9091"
    server = cServer(IP, PORT)  # Instance of cServer(host: str, port: int)

    # Initializes the server: bind and listen and returns True if all is OK
    if server.start_server():  
        server.attend()

    print("\nServer Finished!\n")
