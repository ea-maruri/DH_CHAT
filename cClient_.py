"""Script for representing a client for a chatting application.

Has his own GUI"""

import socket
import tkinter as tk
from tkinter import ttk
from threading import Thread
from cClient_Private_Room import cClient_Private_Room
import sys


class cClient:

    def __init__(self, server_ip=1, server_port=1, name=""):
        ##########################################################################
        ##########################################################################
        # FOR CLIENT
        #Check ip
        if server_ip is None or server_ip == "" or not server_ip:
            print("Error: there is no server_ip")
            return
        self.server_ip = server_ip

        #Check Port
        if server_port is None or not server_port:
            print("Error: there is no server_port")
            return
        self.server_port = server_port

        #Check Name
        if not name or name == "" or name is None:
            name = "Client_Name_"
        
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.connect(("8.8.8.8", 80))  # Connec to Google DNS
        self.client_ip = test_socket.getsockname()[0]  # client IP
        self.client_port = test_socket.getsockname()[1]  # client PORT
        test_socket.close()
        self.name = name + "_" + self.client_ip

        #Socket for client
        self.client_socket = None
        self.connected = False
        self.assigned_port = 0

        #List for Combobox
        self.list_for_combobox = list()
        self.client = None  # For a cClient instance

        #Rooms
        self.num_of_rooms = 0

        #Threads
        #self.asking_thread = Thread(target=self.ask_for_list_thread)  # For asking list
        #self.receive_thread = Thread(target=self.receive)  # For receiving messages

        ##########################################################################
        ##########################################################################
        # FOR GUI
        self.top = tk.Tk()
        self.top.geometry("490x600")
        self.top.title("AR-Chatter")
        self.top.resizable(False, False)
        self.top.protocol("WM_DELETE_WINDOW", self.gui_on_closing)

        #Text Area
        self.scrollbar = tk.Scrollbar(self.top)  # To navigate through past messages.
        self.msg_list = tk.Listbox(self.top, height=15, width=72, yscrollcommand=self.scrollbar.set)
        self.msg_list.grid(row=0, column=0, columnspan=4, padx=(10, 10), pady=(10,10))
        #self.msg_list["state"] = tk.DISABLED
        
        #Message
        tk.Label(self.top, text="Message: ").grid(row=1, column=0, padx=(5,5))  # Label
        self.my_msg = tk.StringVar()
        self.my_msg.set("Your messages here.")
        self.message_entry = tk.Entry(self.top, width=48, textvariable=self.my_msg)  # Entry
        self.message_entry.grid(row=1, column=1, padx=(10, 10), pady=(10,10), columnspan=2)
        self.message_entry["state"] = tk.DISABLED
        self.btn_send_message = tk.Button(self.top, text="Send", command=self.send_message) # Send Button
        self.btn_send_message.grid(row=1, column=3)
        self.btn_send_message["state"] = tk.DISABLED

        # Try to connect
        tk.Label(self.top, text="Try to Connect: ").grid(row=2, column=0, padx=(5, 5))  # Label
        self.name_to_connect = tk.StringVar()
        self.name_to_connect.set("A name here")
        self.name_to_connect_entry = tk.Entry(self.top, width=48, textvariable=self.name_to_connect)  # Entry
        self.name_to_connect_entry.grid(row=2, column=1, padx=(10, 10), pady=(10, 10), columnspan=2)
        self.name_to_connect_entry["state"] = tk.DISABLED
        self.btn_name_to_connect = tk.Button(self.top, text="Try", command=self.try_connection)  # Send Button
        self.btn_name_to_connect.grid(row=2, column=3)
        self.btn_name_to_connect["state"] = tk.DISABLED

        # Separator
        self.message_separator = ttk.Separator(self.top).grid(row=3, column=0, columnspan=4, sticky="ew", padx=(5,5))

        #Connect
        tk.Label(self.top, text="Host: ").grid(row=4, column=0, padx=(5,5))
        tk.Label(self.top, text="Port: ").grid(row=5, column=0, padx=(5,5))
        tk.Label(self.top, text="Name: ").grid(row=6, column=0, padx=(5,5))
        
        self.host_entry = tk.Entry(self.top)
        self.port_entry = tk.Entry(self.top)
        self.name_entry = tk.Entry(self.top)
       
        self.host_entry.grid(row=4, column=1, padx=(10, 10), pady=(5,5))
        self.port_entry.grid(row=5, column=1, padx=(10, 10), pady=(5,5))
        self.name_entry.grid(row=6, column=1, padx=(10, 10), pady=(5,5))

        self.btn_connect = tk.Button(self.top, text="Connect", command=self.connect_to_host)
        self.btn_connect.grid(row=6, column=2)
        self.btn_disconnect = tk.Button(self.top, text="Disconnect", command=self.disconnect_to_host)
        self.btn_disconnect.grid(row=6, column=3, pady=(5,5))  # Disconnect Button
        self.btn_disconnect["state"] = tk.DISABLED

        # Separator
        self.connection_separator = ttk.Separator(self.top).grid(row=7, column=0, columnspan=4, sticky="ew", padx=(5,5))
        
        #Listing and private room
        self.btn_list_clients = tk.Button(self.top, text="List", command=self.ask_for_clients_list)
        self.btn_list_clients.grid(row=8, column=0, padx=(5,5))  # Disconnect Button
        self.combo_box_clients = ttk.Combobox(self.top, width=30)
        self.combo_box_clients.grid(row=8, column=1, columnspan=2)  # Combobox
        self.btn_private_room = tk.Button(self.top, text="Create Private Room", command=self.private_connection)
        self.btn_private_room.grid(row=8, column=3, padx=(5,5), pady=(5,5))

        self.btn_list_clients["state"] = tk.DISABLED
        self.combo_box_clients["state"] = tk.DISABLED
        self.btn_private_room["state"] = tk.DISABLED
        # Separator
        self.listing_separator = ttk.Separator(self.top).grid(row=9, column=0, columnspan=4, sticky="ew", padx=(5,5))

        #Buttons
        self.btn_make_room = tk.Button(self.top, text="Room")
        self.btn_talk_with = tk.Button(self.top, text="Talk with...")

        self.btn_connect_to_ip = tk.Button(self.top, text="Connect to registered IP", command=self.try_connection)  # Send Button
        self.btn_connect_to_ip.grid(row=10, column=0)
        self.btn_connect_to_ip["state"] = tk.DISABLED

        self.top.mainloop() # Starts GUI execution.

        #Receiving thread
        self.receive_thread = None


    ## CLIENT METHODS
    def connect_to_host(self):
        """Make the connection with a host given in tuple (server_ip:server_port)"""

        print("I am ", self.name, "in", self.client_ip, ":", self.client_port)

        HOST = self.host_entry.get().strip()
        PORT = self.port_entry.get().strip()
        NAME = self.name_entry.get().strip()

        self.host_entry.delete(0, 'end')
        self.port_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')

        if HOST is None or PORT is None or NAME is None or HOST == "" or PORT == "" or NAME == "":
            print("Error: An empty entry")
            return

        self.server_ip = HOST
        self.server_port = int(PORT)
        self.name = NAME + "_" + self.client_ip
        print("Try to connect to", self.server_ip, ":", self.server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        
        self.client_socket.send(bytes("START" + self.name, encoding="utf-8"))
        
        self.connected = True
        print("Connected!\n")
    
        #Threads
        self.start_receiving_thread()
        self.start_ask_for_list_thread()

        #Activate Messagging and Desactivating Connecting
        self.msg_list["state"] = tk.NORMAL
        self.message_entry["state"] = tk.NORMAL
        self.name_to_connect_entry["state"] = tk.NORMAL
        self.btn_send_message["state"] = tk.NORMAL
        self.btn_name_to_connect["state"] = tk.NORMAL
        self.btn_disconnect["state"] = tk.NORMAL
        self.btn_list_clients["state"] = tk.NORMAL
        self.combo_box_clients["state"] = tk.NORMAL
        self.btn_private_room["state"] = tk.NORMAL
        self.host_entry["state"] = tk.DISABLED
        self.port_entry["state"] = tk.DISABLED
        self.name_entry["state"] = tk.DISABLED
        self.btn_connect["state"] = tk.DISABLED
        self.btn_connect_to_ip["state"] = tk.DISABLED


    def start_receiving_thread(self):
        receive_thread = Thread(target=self.receive)
        receive_thread.start()


    def start_ask_for_list_thread(self):
        asking_thread = Thread(target=self.ask_for_list_thread)  # For asking list
        asking_thread.start()


    def disconnect_to_host(self):
        self.client_socket.send(bytes("QqQ" + self.name, "utf8"))
        self.client_socket.close()
        self.connected = False
        #self.top.quit()

        self.msg_list.delete(0, tk.END)
        
        #Activate Messagging and Desactivating Connecting
        self.msg_list["state"] = tk.DISABLED
        self.message_entry["state"] = tk.DISABLED
        self.name_to_connect_entry["state"] = tk.DISABLED
        self.btn_send_message["state"] = tk.DISABLED
        self.btn_name_to_connect["state"] = tk.DISABLED
        self.btn_disconnect["state"] = tk.DISABLED
        self.btn_list_clients["state"] = tk.DISABLED
        self.combo_box_clients["state"] = tk.DISABLED
        self.btn_private_room["state"] = tk.DISABLED
        self.host_entry["state"] = tk.NORMAL
        self.port_entry["state"] = tk.NORMAL
        self.name_entry["state"] = tk.NORMAL
        self.btn_connect["state"] = tk.NORMAL
        self.btn_connect_to_ip["state"] = tk.NORMAL

        self.top.title("AR-Chatter")
        
    
    def ask_for_list_thread(self):
        import time
        while True:
            if self.connected:
                time.sleep(10) # Sleeps 10 seconds
                self.ask_for_clients_list()
            #else:
             #   print("No more listing")
               # break  # No more connected (RuntimeError: threads can only be started once)

       
    def receive(self):
        while True:
            if self.connected:
                try:
                    received_message = self.client_socket.recv(1024).decode("utf8")

                    if received_message:
                        print("I receive this:", received_message)
                        
                        header = received_message[:5]
                        if header == "START":
                            received_message = received_message.split(" ")
                            # Receive: Welcome, Name Port

                            self.top.title("AR-Chatter: " + received_message[1])
                            
                            self.msg_list.insert(tk.END, received_message[0].replace("START", "") + " " + received_message[1] + "!")
                            self.msg_list.insert(tk.END, " ")

                            self.assigned_port = received_message[2]
                            print("Assigned port:", self.assigned_port, "\n")
        
                        elif header == "LIST1":
                            print("\tI recieve the List\n")
                            received_message = received_message.replace("LIST1", "")
 
                            self.combobox_list = received_message.split(",")

                            self.combo_box_clients.grid_forget()
                            self.combo_box_clients.grid_forget()
                            self.combo_box_clients = ttk.Combobox(self.top, width=30, values=self.combobox_list)
                            self.combo_box_clients.grid(row=7, column=1, columnspan=2)

                        elif header == "PROOM":
                            room_id = received_message.split(",")[1]
                            private_room_thread = Thread(target=self.create_private_room_gui, args=(room_id,))
                            private_room_thread.start()
                        
                        elif header == "ADDED":
                            room_id = received_message.split(",")[1]
                            private_room_thread = Thread(target=self.create_private_room_gui, args=(room_id,))
                            private_room_thread.start()

                        elif header == "ERROR":
                            print("Error in Server")

                        else:
                            self.msg_list.insert(tk.END, received_message)
        
                except OSError as e:  # Possibly client has left the chat.
                    print("Error receiving data from server:", str(e))
                    break

            #else:
            #    print("No more receive!!!")
                #break 


    def connect_to_ip(self):
        self.client_socket.send(bytes("CONIP", encoding='utf-8'))



    def try_connection(self):
        name = self.name_to_connect.get().strip()

        self.client_socket.send(bytes("TRYCO" + name, encoding="utf-8"))
        self.name_to_connect.set("")


    def send_message(self):
        msg = self.my_msg.get().strip()

        if msg == "QqQ":
            self.disconnect_to_host()
            return
       
        self.client_socket.send(bytes("BROAD" + self.name + ": " + msg, encoding="utf-8"))  
        self.my_msg.set("") 


    def ask_for_clients_list(self):
        self.client_socket.send(bytes("LIST1", "utf8"))


    def private_connection(self):
        # msg = "connect " + self.combo_box_clients.get()
        msg = "PROOM" + self.name
        self.client_socket.send(bytes(msg, "utf8"))


    def end_private_connection(self):
        msg = "disconnect_private"
        self.client_socket.send(bytes(msg, "utf8"))
        

    def create_private_room_gui(self, room_id:str):
        private_room = cClient_Private_Room(self.server_ip, self.server_port, room_id, self.name)
        private_room.startGUI()


    def __str__(self):
        if self.connected:
            return "Client socket in " + self.client_ip + ". Connected to (" + self.server_ip + ":" + self.server_port + ")"
        else:
            return "Client socket in " + self.client_ip + ". Not connected."


    # GUI METHODS
    def gui_on_closing(self, event=None):
        """This function is to be called when the window is closed."""
        try:
            if self.connected:
                self.my_msg.set("QqQ")
                self.send_message()
        except OSError as e:
            print("Error on closing:", str(e))
        finally:
            self.top.quit()
            sys.exit()
            
        

if __name__ == "__main__":
    my_client = cClient("0", 9090, " ")  # Arguments are not necessary

    print("Client Finished")