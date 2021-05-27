#!/usr/bin/env python3

#Created by Adithya shastry
#This File will house of the methods to allow the clients and Servers to 
    # Communicate with one another through Sockets

#Import Required Modules
import socket

class UDPSocket:
    """
    This Class will obfuscate the Socket communications from the Server and
    Client Classes since the same code will mostly be used by both Classes

    Methods:
        Constructor:
            Takes the Host IP and the PORT number and binds a socket to listen
            on that PORT

    Attributes:
        HOST: Holds the Host IP
        PORT: Holds the Port Number the Socket will send/recieve from
        socket: Will facilitate the communication
    """
    def __init__(self,PORT,HOST='127.0.0.1'):
        #Here we will specify the HOST IP and PORT
        self.HOST = HOST
        self.PORT = PORT
        #Create a UDP Socket
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #We will bind to the Port since both the Client and the Server need
        # be able to recieve messages. We wouldn't need to if the the Client or
        # Server only sent messages
        self.socket.bind((self.HOST,self.PORT)) 

    def connectTo(self,PORT,IP='127.0.0.1'):
        """
        This method will initialize a connection to the Specified HOST
        Parameters: 
            IP: The IP info of the Destination Host
            PORT: Destination Port number
        """
        while True:
            Input = input('Type Something: ')
            self.socket.sendto(str.encode(Input),(IP,PORT))
            #recieve a message from the server
            reply,senderAddress = self.socket.recvfrom(1024)
            print("Server Says: {}".format(reply.decode('utf-8')))
    def acceptConnections(self):
        """
        This method will listen for connection requests and approve them
        """ 
        while True:
            data,senderAddress = self.socket.recvfrom(1024)
            print("Recived Data from: {}".format(senderAddress))
            data = data.decode('utf-8')
            print("Client Says: {}".format(data))
            if not data:
                #we want to just exit the loop
                break
            self.socket.sendto(str.encode(data), senderAddress)

