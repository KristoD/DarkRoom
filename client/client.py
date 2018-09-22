# DarkRoom - Anonymous, Encrypted, Multithreaded Python Chat Application

# Client side code

from cryptography.exceptions import InvalidKey
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import sys
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter import ttk

# Encryption functions

def get_key(password):
    try:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(password)
        return base64.urlsafe_b64encode(digest.finalize())
    except InvalidKey:
        print("Invalid password")
        sys.exit()
        return

def encrypt(password, token):
    try:
        f = Fernet(get_key(password))()
        return f.encrypt(bytes(token))
    except InvalidKey:
        print("Invalid password.")
        sys.exit()
        return

def decrypt(password, token):
    try:
        f = Fernet(get_key(password))
        return f.decrypt(bytes(token))
    except InvalidKey:
        print("Invalid password.")
        sys.exit()
        return

# Handles receiving of messages.

def receive():
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE)
            msg = decrypt(key, msg)
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

# Handles sending of messages.

def send(event=None):  # event is passed by binders.
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(encrypt(key, bytes(msg, 'utf-8')))
    if msg == "{quit}":
        client_socket.close()
        top.quit()

# This function is to be called when the window is closed.

def on_closing(event=None):
    my_msg.set("{quit}")
    send()

top = tkinter.Tk()
top.title("DarkRoom")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=25, width=75, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

# Client config

if(len(sys.argv) < 2):
    print("Usage: python3 client.py <server password>")
    sys.exit()

HOST = '127.0.0.1'
PORT = 33000
PASSWORD = sys.argv[1]
key = bytes(PASSWORD, 'utf-8')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop() # Starts GUI execution.