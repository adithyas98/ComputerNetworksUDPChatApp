#!/usr/bin/env python3

#Created By Adithya Shastry
#This file holds all the code that will be used by the Server in the UDP
# Chat application
from UDPSocket import UDPSocket
import time
from threading import Thread as th

class Server:
    """
    This class will handle the opperations that the Server needs to do as 
    described in the assignment paper such as maintain a table of all 
    registered clients, send an updated table when a client registers and 
    de registers, and hold messages sent by clients to other clients who are
    currently offline.

    Methods:
        Constructor:
            Will create an instance of the Server with the specified Port
        registerUser:
            This will register a user and append their nickname and 
            information to the clientTable dictionary
        updateAllClients:
            This must happen after a user(clients) has been registered. 
            Will send an updated table to all users on the service
    Attributes:
        udp: Will hold the udp socket that can be used to send and recieve
            data.
        threads = will hold all the threads
        messages = This will hold all stored messages
        clientTable: This will hold the IP addresses and Port numbers of
                    clients that are connected. The Client Table will hold 
                    the nick names of the clients in a nested dictionary of 
                    the following form
                        {
                        Nick:{
                           IP: IP of the Client
                           PORT: Port of the Client
                           Online: True/False value depicting their current
                                   status online
                            }
                        }
                            

    """
    def __init__(self,PORT):
        self.udp = UDPSocket(PORT)#We create an instance of the UDPsocket
        self.clientTable = dict()#A dictionary that will hold the Client Info
        #we want to call the Main thread now
        self.threads = []#will hold all threads
        self.messages = dict()
        print("Server all set up! Waiting for Connections")
        self.MainThread()
    def MainThread(self):
        """
        This method will serve as the main loop that the server will follow.
        When the server needs to accomplish some task, it will create a new 
        thread that will complete that task, so that the server can continue 
        to listen for incoming connection requests

        """
        while True:
            try:
                data,address = self.udp.secureRecieve()
            except:
                continue
            if data != None:
                #We want to create a thread and send it to Process Message
                x=th(target=self.processMessage,args=(data,address),daemon=True)
                x.start()
                self.threads.append(x)
                data = None
                address = None
    def processMessage(self,data,address):
        """
        This method will process any inputs that is receieved in the Main
        Thread function. I decided to make a separate function to ensure
        that I can multithread everything and keep the main loop going
        """
        command = data[1].split(':')
        data = data[2]
        if command[0] == 'reg':
            #now we can register the user and update all other users
            self.registerUser(data,address[0],address[1])
        elif command[0] == 'dereg':
            self.deRegister(data)
            #We want to de register the person
        elif command[0] == 'send':
            pass
            #In this case we want to store the message that the client is 
              #sending and send it later
        else:
            print("Incorrect Command")
            return None

    def storeMessage(self,nick,MSG,address):
        """
        This method will first try to contact the client and if that fails
        will store the message and relay it to the client when they reregister
        Parameters:
            nick: the nickname of the client being contacted
            MSG: the Message to relay to the client
            address: the address of the client making the request
        """
        #first we will get all the clients details
        IP = self.clientTable[nick]['IP']
        PORT = self.clientTable[nick]['PORT']
        online = self.clientTable[nick]['Online']
        #first we will check to see if the client is online in our records
        if online:
            #If they are online, we want to try to send the message to them
            response = self.udp.secureSend(MSG,PORT,IP)
            if response == 200:
                #Then the client was online!
                #we want to notify the client
                Error = [1,"ERROR",'The client is online!']
                self.udp.secureSend(Error,PORT,IP)
                return None
            else:
                #We want to update the Status of the Client
                self.clientTable[nick]['Online'] = False
                #The message was not send correctly, so we want to store it
                if nick in self.clientTable.keys():
                    #if there is a key then we wna to append a message
                    self.messages[nick].append(MSG)
                else:
                    #if a key doesn't already exist we want to make on
                    self.messages[nick] = [MSG]
                return None
        else:
            #If the client is not online we, want to store the message
            #The message was not send correctly, so we want to store it
            if nick in self.clientTable.keys():
                #if there is a key then we wna to append a message
                self.messages[nick].append(MSG)
            else:
                #if a key doesn't already exist we want to make on
                self.messages[nick] = [MSG]
            return None
    def sendStored(self,nick):
        """
        This method will send registered users offline messages
        """
        #we want to iterate over the list of messages stored
        for message in self.message[nick]:
            MSG = [1,"MSG:",message]
            #figure out the IP and Port of the client
            IP = self.clientTable[nick]['IP']
            PORT = self.clientTable[nick]['PORT']
            #now we can send the message
            self.udp.secureSend(MSG,IP,PORT)
        #After this we can return
        return None

    def registerUser(self,Nick,IP,PORT):
        """
        This method is used to register a user by adding them to the 
        table along with their IP,PORT, and Online Status

        Parameters:
            Nick: The Nickname of the client connecting to the Server
            IP: The IP of the Client
            PORT: The Port of the Client
        """
        #we first want to check if the nickname already exists
        if Nick in self.clientTable.keys():
            if not self.clientTable[Nick]['Online']:
                #this means the client is logging back in
                #if this is the case we want to just update the online status
                self.clientTable[Nick]['Online']=True
                #Now we want to send the updated table to the Client
                self.updateAllClients()
                #TODO: Create a method to send all Stored Chats
                return None
            #If the nickname already exists, we dont want to allow it
            print("The Nickname already exist, please exit the program")
            #We want to send this to the client
            MSG = [1,1,"ERROR"]
            self.udp.secureSend(MSG,PORT,IP)
            return None
        #First we will make an empty dictionary to hold the New Client's Data
        client = dict()
        client['IP'] = IP
        client['PORT'] = PORT
        client['Online'] = True
        #Now we need to add the data to the full Client Table
        self.clientTable[Nick] = client
        print("Debug:{}".format(self.clientTable))
        print("Registered {} at {}:{}".format(Nick,IP,PORT))
        #Now that we have updated the table, we can tell all existing clients
        self.updateAllClients()
        return None
    def updateAllClients(self):
        """
        This method will update all clients in the clientTable dictionary. The
        secureSend method of the UDPSocket class will be utilized to send the 
        dictionary file. 
        """
        #We will create a base message as described in the secureSend method
        #A packer is of the form
        #[Current Seq,Total Packets,Message]
        MSG = [1,'update:',self.clientTable]
        for client,clientData in self.clientTable.items():
            #Now we can send the packet with the secure send method
            PORT = clientData['PORT']
            IP = clientData['IP']
            if clientData['Online'] == True:
                #we only want to send the updated table to the clients online
                response = self.udp.secureSend(MSG,PORT,IP)
                
                
        #we updated all the clients so we can print it to the console
        print("Updated All Clients")
        return None
    def deRegister(self,nick):
        """
        This method will deregister a client, setting its online status in the
        table to Offline

        """
        self.clientTable[nick]['Online'] = False
        #then we need to send the Client an ACK
        PORT = self.clientTable[nick]['PORT']
        IP = self.clientTable[nick]['IP']
        self.udp.secureSend([1,1,'ACK'],PORT,IP)
        #now we need to update all the clients
        self.updateAllClients()
        
        


            


if __name__ == '__main__':
    server = Server(50000)

