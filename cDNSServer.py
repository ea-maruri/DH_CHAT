"""Script for representing a server for a chatting application.
    
    Uses Selectors for manage clients. Selectors is a module that allows a High-Level I/O multiplexing.
    events is a bitwise mask indicating which I/O events should be waited for on a given file object.
                Constant            Meaning
                EVENT_READ    -->   Available for read
                EVENT_WRITE   -->   Available for write"""


import socket
import selectors
import types
import pandas as pd
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

        self.configDF = self.read_config()
        print('Config\n--------------\n', self.configDF)

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

        # Selector for managinf clients
        self.selector = selectors.DefaultSelector()

    def read_config(self):
        configDF = pd.read_csv('./config.csv')
        return configDF.set_index('Nombre').to_dict()['IP']

    def get_IP_given_a_name(self, name: str):
        try:
            return self.configDF[name]
        except Exception as e:
            return "NO ip " + str(e)

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
                    header = recv_data[:5]  # Header of receiving request (as String)

                    # WORKING WITH PRIMITIVES OR HEADERS to know what to do (requests from users/clients)
                    print("\nReceived:", header, "from client\n")

                    if header == "GIVIP":
                        name = recv_data[5:]
                        the_ip = self.get_IP_given_a_name(name)
                        if the_ip:
                            data.outb += bytes("THEIP" + the_ip, encoding="utf-8")
                        else:
                            data.outb += bytes("ERROR", encoding="utf-8")
                        recv_data = ""  # Clear recv_data because receive "GIVIP"

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
                data.outb = bytes("", encoding='utf8')


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
    PORT = 10001
    server = cServer(IP, PORT)  # Instance of cServer(host: str, port: int)

    # Initializes the server: bind and listen and returns True if all is OK
    if server.start_server():  
        server.attend()

    print("\nServer Finished!\n")
