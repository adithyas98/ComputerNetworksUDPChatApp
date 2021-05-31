#!/usr/bin/env python3

#Created by Adithya shastry
#This File will house of the methods to allow the clients and Servers to 
    # Communicate with one another through Sockets

#Import Required Modules
import socket
import pickle #This will allow us to Serialize data 
from hashlib import md5 as md5
import time
class UDPSocket:
    """
    This Class will abstract the Socket communications from the Server and
    Client Classes since the same code will mostly be used by both Classes

    Methods:
        Constructor:
            Takes the Host IP and the PORT number and binds a socket to listen
            on that PORT
        send:
            Sends Python objects to desired IP and Port using Pickle
        secureSend:
            Sends data using a simple Stop and Wait Protocol
        Receive:
            Waits for and receives a message,decodes it, and returns it
        secureRecieve:
            Recieves data using a simple Stop and Wait protocol and works in
            conjunction with the secureSend method

    Attributes:
        HOST: Holds the Host IP
        PORT: Holds the Port Number the Socket will send/receive from
        socket: Will facilitate the communication
    """
    def __init__(self,PORT,HOST='127.0.0.1'):
        #Here we will specify the HOST IP and PORT
        self.HOST = HOST
        self.PORT = PORT
        #Create a UDP Socket
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #We will set a time out for the socket
        self.socket.settimeout(0.5)
        
        #We will bind to the Port since both the Client and the Server need
        # be able to receive messages. We wouldn't need to if the Client or
        # Server only sent messages
        self.socket.bind((self.HOST,self.PORT)) 
    def secureSend(self,MSG,PORT,IP='127.0.0.1'):
        """
        This method will securely send data using the simple Stop and Wait
        Algorithm and a Checksum to ensure the Integrity of the MSG

        Parameters:
            MSG: Is a list of length 3 with the following data in the
                Respective Index
                    Oth - Sequence Number of the Current Packet
                    1st - The Command
                    2nd - Message/Data to send

        What will be sent:
            A checksum will be sent prior to sending the message
            A serialized list with the following information in its indices
                Oth - Sequence Number of the Current Packet
                1st - The Command
                2nd - Message/Data to send
                3rd - Checksum Hash
        Output:
            200 - if the Message was sent successfully
            100 - if the Message was not sent Successfully
        """
        #We need to first pickle the message
        Data = pickle.dumps(MSG[2])
        #Calculate the Hash
        checksum = md5(Data).hexdigest()
        MSG.append(checksum)
        self.send(MSG,PORT,IP)
        #We now need to start a timeout counter
        for i in range(5):
            try:
                ACK,_ = self.recieve()
                if ACK == 'ACK':
                    #Everything went well so we want to return 200
                    return 200
            except socket.timeout as e:
                print("Timed Out, will try again...")
                self.send(MSG,PORT,IP)
        #We tried multiple times and it failed
        print("Message was not Sent Successfully")
        return 100

    def secureRecieve(self):
        """
        This method is meant to recieve data from a host securely in
        accordance with the secureSend() method. If the data is recieved
        correctly, the method will send an ACK back. If the data is not 
        recieved correctly, the method will simply disregard the message

        Output:
            100 -  if the data as not recieved correctly
            The data -  if the data was recieved correctly
        """
        #We want to continuously check for packets until we recieve one
        while True:
            try:
                #recieve the Data
                rdata,Address = self.recieve()
                if rdata != None:
                    break
            except socket.timeout as e:
                continue

        #Now we can check the checksum
        dataToCheck = pickle.dumps(rdata[2])
        checksum = md5(dataToCheck).hexdigest()
        if len(rdata) == 4:
            if checksum == rdata[3]:
                #Everything checks out!
                #we need to send an ACK
                #The Address Tuple is of the form (IP,PORT)
                self.send('ACK',Address[1],Address[0])
                #now we can return the Message to be processed
                return rdata[0:-1],Address

    def send(self,MSG,PORT,IP='127.0.0.1'):
        """
        This method will send a pickled object to the destination Port and IP
        Parameters: 
            IP: The IP info of the Destination Host
            PORT: Destination Port number
        """
        MSG = pickle.dumps(MSG)
        self.socket.sendto(MSG,(IP,PORT))
            
    def recieve(self):
        """
        This method will receive pickled objects
        """ 
        data,senderAddress = self.socket.recvfrom(20 * 1024)
        print("Received Data from: {}".format(senderAddress))
        data = pickle.loads(data)
        return data,senderAddress
