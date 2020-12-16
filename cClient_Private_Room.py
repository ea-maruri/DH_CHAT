import socket
from threading import Thread
import tkinter as tk
from tkinter import ttk

class cClient_Private_Room:
    def __init__(self, server_ip, server_port, id_room, client_name):
        self.name = client_name
        self.id = id_room

        #MUST BE ANOTHER SOCKET
        self.connected = False
        self.the_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.the_socket.connect((server_ip, int(server_port)))
        self.the_socket.send(bytes("ADDME," + self.id + "," + self.name, encoding="utf-8"))
        receive = self.the_socket.recv(1024)
        print("I have created Private and receive:", receive)
        self.connected = True

        # FOR GUI
        self.top = tk.Tk()
        self.top.geometry("490x600")
        self.top.title("My private room " + id_room)
        self.top.resizable(False, False)
        self.top.protocol("WM_DELETE_WINDOW", self.gui_on_closing)

        #Text Area
        self.scrollbar = tk.Scrollbar(self.top)  # To navigate through past messages.
        self.msg_list = tk.Listbox(self.top, height=15, width=70, yscrollcommand=self.scrollbar.set)
        self.msg_list.grid(row=0, column=0, columnspan=4, padx=(10, 10), pady=(10,10))
        #self.msg_list["state"] = tk.DISABLED
            
        #Message
        tk.Label(self.top, text="Message: ").grid(row=1, column=0, padx=(5,5))  # Label
        #self.my_group_msg = tk.StringVar()
        #self.my_group_msg.set("Message to group here!")
        self.message_entry = tk.Entry(self.top, width=48)  # Entry
        self.message_entry.grid(row=1, column=1, padx=(10, 10), pady=(10,10), columnspan=2)
        self.message_entry.insert(0, "Group Mesage Here!")
        
        self.btn_send_message = tk.Button(self.top, text="Send", command=self.send_group_message) # Send Button
        self.btn_send_message.grid(row=1, column=3)
        

        # Separator
        self.message_separator = ttk.Separator(self.top).grid(row=2, column=0, columnspan=4, sticky="ew", padx=(5,5))

        #Listing and private room
        self.btn_list_clients = tk.Button(self.top, text="List", command=self.ask_for_clients_list)
        self.btn_list_clients.grid(row=3, column=0, padx=(5,5))  # Disconnect Button
        self.combo_box_clients = ttk.Combobox(self.top, width=30)
        self.combo_box_clients.grid(row=3, column=1, columnspan=2)  # Combobox
        self.btn_private_room = tk.Button(self.top, text="Add", command=self.add_user)
        self.btn_private_room.grid(row=3, column=3, padx=(5,5), pady=(5,5))

        # Separator
        self.text_separator = ttk.Separator(self.top).grid(row=4, column=0, columnspan=4, sticky="ew", padx=(5,5))

        #Text Area for users in room
        tk.Label(self.top, text="Users in Room:").grid(row=5, column=0, padx=(5,5))  # Label
        self.scrollbar2 = tk.Scrollbar(self.top)  # To navigate through past messages.
        self.group_text = tk.Listbox(self.top, height=10, width=70, yscrollcommand=self.scrollbar2.set)
        self.group_text.grid(row=6, column=0, columnspan=4, padx=(10, 10), pady=(10,10))

        #Go out button
        # Separator
        self.message_separator = ttk.Separator(self.top).grid(row=7, column=0, columnspan=4, sticky="ew", padx=(5,5))
        self.btn_go_out = tk.Button(self.top, text="Go Out", command=self.disconnect_private)
        self.btn_go_out.grid(row=8, columnspan=4, padx=(5,5), pady=(5,5))

        self.start_receiving_thread()
        self.start_clients_in_room_thread()


    def ask_for_clients_in_room(self):
        self.the_socket.send(bytes("LROOM" + self.id, "utf8"))


    def asking_for_clients_in_room(self):
        import time
        while True:
            if self.connected:
                self.ask_for_clients_in_room()
                time.sleep(10)  # Sleeps 10 seconds
                self.group_text.delete(0, "end")


    def start_clients_in_room_thread(self):
        asking_thread = Thread(target=self.asking_for_clients_in_room)  # For asking list
        asking_thread.start()
        

    def startGUI(self):
        self.top.mainloop() # Starts GUI execution.


    def send_group_message(self):
        msg = self.message_entry.get().strip()
        print("Room send", msg)
        if msg == "QqQ":
            #self.disconnect_to_host()
            # GO OUT FROM THE CHAT ROOM
            self.top.quit() 
            return

        msg = "LOCAL," + self.id + "," + self.name + ": " + msg
        print("Local send:", msg)
        self.the_socket.send(bytes(msg, encoding="utf-8"))  
        self.message_entry.delete(0, 'end')


    def ask_for_clients_list(self):
        self.the_socket.send(bytes("LIST1", "utf8"))


    def add_user(self):
        msg = "ADUSR," + self.combo_box_clients.get() + "," + self.id
        self.the_socket.send(bytes(msg, "utf8"))


    def gui_on_closing(self, event=None):
        """This function is to be called when the window is closed.""" 
        try:
            if self.connected:
                self.message_entry.delete(0, 'end')
                self.message_entry.insert(0, "QqQ")
                self.send_group_message()
        except OSError as e:
            print("Error on closing:", str(e))
        finally:
            self.top.quit()       


    def disconnect_private(self):
        self.the_socket.send(bytes("QqQ", "utf8"))
        self.the_socket.close()
        self.connected = False


    def start_receiving_thread(self):
        receive_thread = Thread(target=self.receive)
        receive_thread.start()


    def receive(self):
        while True:
            try:
                received_message = self.the_socket.recv(1024).decode("utf8")
                if received_message:
                    print("I receive this in private room:", received_message)
                    
                    header = received_message[:5]
                    if header == "LIST1":
                        print("I recieve the List")
                        received_message = received_message.replace("LIST1", "")
                        #received_message = received_message.replace("b", "")
                       
                        self.combobox_list = received_message.split(",")
                                       
                        self.combo_box_clients.grid_forget()
                        self.combo_box_clients = ttk.Combobox(self.top, width=30, values=self.combobox_list)
                        self.combo_box_clients.grid(row=3, column=1, columnspan=2)
                    
                    elif header == "LROOM":
                        print("I recieve the List")
                        received_message = received_message.replace("LROOM", "")
                        received_message = received_message.split(",")

                        for name in received_message:
                            self.group_text.insert(tk.END, name)

                    elif header == "ADUSR":
                        self.group_text.delete(0, "end")

                        received_message = received_message.replace("ADUSR", "")
                        received_message = received_message.split(",")

                        for name in received_message:
                            self.group_text.insert(tk.END, name)

                    else:
                        self.msg_list.insert(tk.END, received_message)
    
            except OSError as e:  # Possibly client has left the chat.
                print("Error receiving data from server:", str(e))
                break


if __name__ == "__main__":
    private_room_gui = cClient_Private_Room("192.168.0.100", 9090, "MY-ID", "NAME")
    private_room_gui.startGUI()
