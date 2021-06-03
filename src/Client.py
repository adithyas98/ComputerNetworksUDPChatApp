#!/usr/bin/env python3

#Created by Adithya Shastry
#This file will hold all the code needed by the Client in for the UDP Chat
    # Application

from UDPSocket import UDPSocket
from threading import Thread as th
import sys
from datetime import datetime
import time
class Client:
    """
    This class will handle the opperations of the Client as described by the 
    assignment such as registering with a server, recieving a client table,
    and messaging clients.
    Methods:
        Constructor:
            Will create the udp client with which the client will communicate.
        clientTablePrint:
            This method will print the nicknames of current clients and their
            online status
        MainThread:
            This is the main loop for the Client
        ProcessMessage:
            This will process UDP messages
        ProcessInput:
            Processes User Input
    Attributes:
        upd: Will hold an instance of the UDPSocket class binded to a 
            certain port and IP
        Nick: Holds the Nickname of the Client
        threads: will hold all the threads
        clientTable: Will hold the client table (as sent from the Server) 
                    of updated client information.
        serverIP: Will hold the server's IP info
        serverPort: Will hold the server's Port info
    Format of Messages and Commands:
        Commands will take the following form in the 1st index of a packet:
            Command1:Command2
        
    """
    def __init__(self,Nick,IP,PORT,ServerPort,ServerIP='127.0.0.1'):
        self.threads = []
        self.Nick = Nick
        self.serverPort = ServerPort
        self.serverIP = ServerIP
        self.udp = UDPSocket(PORT,IP)
        self.clientTable = dict()
        #with this we actually want to register with the Server
        print("Initializing Connection with Server...")
        #we simply need to send our Nick name because Address info will be 
         # send automatically
        response = self.udp.secureSend([1,"reg:",Nick],ServerPort,ServerIP)
        if response != 200:
            #then we didnt connect to the server so we can just break here
            print("We didn't connect to the Server")
            return None
        print("We successfully connected to the Server!\n")
        print("Waiting for the updated table of Clients")
        #We need to wait to receive the client table
        while True:
            try:
                data,Address = self.udp.secureRecieve()
                if data != None:
                    break
            except TypeError:
                continue
        if data[2] == "ERROR":
            #Nickname is already taken
            print("Nickname is already taken. Please Try Again.")
            exit()
        self.clientTable = data[2] 
        print("Recieved the Table of other Clients!")
        print(self.clientTablePrint())
        self.MainLoop()
    def clientTablePrint(self):
        """
        This method will print all the clients' nicknames. This will return
        a string of all of the clients and their online status.
        """
        nicknames = self.clientTable.keys()
        #Now we can convert this into a string to be able to print it easier
        names = 'Clients:|Status:\n--------------\n'
        for nick in nicknames:
            online = self.clientTable[nick]['Online']
            if online:
                online = 'Online'
            else:
                online = 'Offline'
            names += '{} | {}\n'.format(nick,online)
        return names
    def MainLoop(self):
        """
        This will serve as the main loop that the Client will use to listen
        for user input
        """
        #we want to make a thread to listen for user input
        y=th(target=self.processInput,daemon=True)
        y.start()
        self.threads.append(y)
        while True:
            #We will use this as out main loop to listen for inputs
            try:
                data,address = self.udp.secureRecieve()
            except TypeError:
                continue
            if data != None:
                x=th(target=self.processMessage,args=(data,address),daemon=True)
                x.start()
                self.threads.append(x)
                data = None
                address = None
        return None
    def processMessage(self,data,address):
        """
        This method processes all incoming UDP packets
        """
        command = data[1].split(':')
        data = data[2]
        if command[0] == 'update':
            #This will update our table
            self.clientTable = data
        elif command[0] == 'MSG':
            #We just recieved a message
            #we just want to print the message
            if address[1] == self.serverPort:
                print(">>> You Have Messages")
            print('>>> {} {}'.format(datetime.now(),data))
        else:
            print('>>> Incorect Command. Please Try Again')
    def processInput(self):
        """
        This method will process any inputs that is recieved by the client, 
        from both the Server and other clients. It is split up this way to 
        make it easiet to handle multiple requests
        """
        while True:
            command = input(">>> ").split(' ') 
            print(command)
            if command[0] == 'send':
                #we want to send a message
                nick = command[1]
                data = " ".join(command[2:])#Combine the list into strings
                self.sendMessage(nick,data)
            elif command[0] == 'clients':
                #This will list the clients
                print(self.clientTablePrint())
            elif command[0] == 'dereg':
                #we want to deregister the user
                MSG = [1,'dereg:',self.Nick]
                self.udp.secureSend(MSG,self.serverPort,self.serverIP)
                data,_ = self.udp.secureRecieve()
                if data[2] == 'ACK':
                    print("You're Offline. Bye.")
                    sys.exit()
                else:
                    print("Server Connection Timed Out\n")
                    print("Exiting...")
                    sys.exit()#this will exit the whole program
            
    def sendMessage(self,nick,MSG):
        """
        This method will send a message to a client. It will try to send a 
        message directly to a client, if the client is currently offline or
        is unreachable the method will instead encode and send the message
        to the Server to store
        """
        if nick not in self.clientTable:
            #Then we want to say the client doesn't exist
            print(">>> No Record of that Client. Please try again!")
            return None
        #we can first get the IP and PORT of the client we want to contact
        IP = self.clientTable[nick]['IP']
        PORT = self.clientTable[nick]['PORT']
        #we can check if the client is online
        MSG = [1,'MSG:'+nick,self.Nick+": "+MSG]
        if not (self.clientTable[nick]['Online']):
            #since the client is not online we will need to send the server 
            #our message
            response = self.udp.secureSend(MSG,self.serverPort,self.serverIP)
            if response == 200:
                #The data was successfully stored
                print("Your Message was Successfully Saved in the Server!")
                return None
            else:
                #then there was an error connecting to the server
                print("There was an error sending the message to the Server")
        else:
            #We want to try and see if we can successfully send a message
            response = self.udp.secureSend(MSG,PORT,IP)
            if response == 200:
                #Everything checked out fine!
                return None
            else:
                #Client is offline so we need to send our message t the server
                response = self.udp.secureSend(MSG,self.serverPort,self.serverIP)
                if response == 200:
                    #We successfully sent the message to the Server
                    print("Client was offline. Sent the message to the Server")
                    data,_ =self.udp.secureRecieve()
                    if data[1] == 'ERROR':
                        print(data[2])
                    
        
            

if __name__ == '__main__':
    client = Client('Buddy','127.0.0.1',50020,50000)


