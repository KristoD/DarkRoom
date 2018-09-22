# DarkRoom - Anonymous, Encrypted, Multithreaded Python Chat Application

# Server side code

import configparser
import sys
import signal
import os
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

os.system("clear")
print ("""
          ___  ________________    ____  _________________
         / _ \ ___    ____ __ _   / _\ )__  ___  __    __ 
        / _/ // _ \  / __// / /  / _  / _ \/ _ \/  \  /  \ 
       /___ / \__/_\/_/  /_/\_\ /_/ \_\___/\___/_/\_\/_/\_\ \n
       server v 1.0 | Kristo

""")

# Server config

clients = {}
addresses = {}

config = configparser.RawConfigParser()
config.read(r'darkroom.conf')

HOST = config.get('config', 'HOST')
PORT = int(config.get('config', 'PORT'))
BUFFER_SIZE = 1024
ADDRESS = (HOST, PORT)

server = socket(AF_INET, SOCK_STREAM)
server.bind(ADDRESS)

# Accepting connections

def accept_incoming_connections():
    # Sets up handling for incoming clients
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Welcome to DarkRoom. Enter your alias.", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

# Handles new client

def handle_client(client): # Takes client socket as argument
    # Handles a single client connection
    name = client.recv(BUFFER_SIZE).decode("utf8")
    welcome = 'You have entered the DarkRoom. If you want to quit, type {quit} to exit.'
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the DarkRoom."
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    while True:
        msg = client.recv(BUFFER_SIZE)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the DarkRoom." % name, "utf8"))
            break

# Broadcasts message to all users

def broadcast(msg, prefix=""): # prefix is for name identification
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)

# Start server and listen for incoming connections

if __name__ == "__main__":
    server.listen(30)
    print("Server listening on port " + str(PORT) + "....")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start() # Starts the infinite loop.
    ACCEPT_THREAD.join()
    server.close()
