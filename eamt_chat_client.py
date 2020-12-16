from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tk
from tkinter import ttk
import eamt_client_class as cl


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE).decode("utf8")
            msg_list.insert(tk.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "disconnect":
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("disconnect")
    send()


def connect_to_host():
    """Make the connection with a host given in entries"""
    HOST = host_entry.get()
    PORT = port_entry.get()
    NAME = name_entry.get()

    host_entry.delete(0, 'end')
    port_entry.delete(0, 'end')
    name_entry.delete(0, 'end')

    if not PORT:
        PORT = 10023
    else:
        PORT = int(PORT)
    if not HOST:
        HOST = "10.0.0.19"

    client_socket.connect((HOST, PORT))
    #client_socket.send(bytes(NAME + ", (" + HOST + ":" + str(PORT) + ")", "utf8"))
    receive_thread = Thread(target=receive)
    receive_thread.start()

    connect_button["state"] = tk.DISABLED
    host_entry["state"] = tk.DISABLED
    port_entry["state"] = tk.DISABLED
    name_entry["state"] = tk.DISABLED

    send_button["state"] = tk.NORMAL
    entry_field["state"] = tk.NORMAL
    disconnect_button["state"] = tk.NORMAL
    list_clients_button["state"] = tk.NORMAL

    #client = cl.cClient(name=NAME, address=(HOST, PORT))
    client_socket.send(bytes(NAME, "utf8"))
    #print("I am", str(client))


def disconnect_to_host():
    msg = "disconnect"
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "disconnect":
        client_socket.close()
        top.quit()

def get_clients_list():
    msg = "list"
    client_socket.send(bytes(msg, "utf8"))

def private_connection():
    msg = "connect"
    client_socket.send(bytes(msg, "utf8"))

def end_private_connection():
    msg = "disconnect_private"
    client_socket.send(bytes(msg, "utf8"))

top = tk.Tk()
top.title("Chatter")

messages_frame = tk.Frame(top)
my_msg = tk.StringVar()  # For the messages to be sent.
my_msg.set("Your messages here.")
scrollbar = tk.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tk.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tk.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tk.Button(top, text="Send", command=send)
send_button.pack()

send_button["state"] = tk.DISABLED
entry_field["state"] = tk.DISABLED


## Frame for stablish connection
host_frame = tk.Frame(top)
host_frame.pack(side=tk.BOTTOM)
port_frame = tk.Frame(host_frame)
port_frame.pack(side=tk.BOTTOM)
name_frame = tk.Frame(port_frame)
name_frame.pack(side=tk.BOTTOM)
button_frame = tk.Frame(name_frame)
button_frame.pack(side=tk.BOTTOM)
combo_box_frame = tk.Frame(button_frame)
combo_box_frame.pack(side=tk.BOTTOM)

# Host
host_label = tk.Label(host_frame, text="Host: ")
host_label.pack(side=tk.LEFT)
host_entry = tk.Entry(host_frame)
host_entry.pack(side=tk.RIGHT)

# Port
port_label = tk.Label(port_frame, text="Port: ")
port_label.pack(side=tk.LEFT)
port_entry = tk.Entry(port_frame)
port_entry.pack(side=tk.RIGHT)

# Name
name_label = tk.Label(name_frame, text="Name: ")
name_label.pack(side=tk.LEFT)
name_entry = tk.Entry(name_frame)
name_entry.pack(side=tk.RIGHT)

# Buttons
connect_button = tk.Button(button_frame, text="Connect", command=connect_to_host)
connect_button.pack(side=tk.LEFT)
disconnect_button = tk.Button(button_frame, text="Disconnect", command=disconnect_to_host)
disconnect_button.pack(side=tk.LEFT)
list_clients_button = tk.Button(button_frame, text="List Clients", command=get_clients_list)
list_clients_button.pack(side=tk.BOTTOM)
private_connection_button = tk.Button(button_frame, text="Private Connection", command=private_connection)
private_connection_button.pack(side=tk.BOTTOM)
end_private_connection_button = tk.Button(button_frame, text="End Private Connection", command=end_private_connection)
end_private_connection_button.pack(side=tk.BOTTOM)
#disconnect_button["state"] = tk.DISABLED

# Combobox
connected_clients_list = ["client1", 'client2']
combo_box_clients = ttk.Combobox(combo_box_frame, values=connected_clients_list)
combo_box_clients.pack(side=tk.LEFT)


top.protocol("WM_DELETE_WINDOW", on_closing)

#----sockets part----
BUFFER_SIZE = 1024
client_socket = socket(AF_INET, SOCK_STREAM)

tk.mainloop()  # Starts GUI execution.
