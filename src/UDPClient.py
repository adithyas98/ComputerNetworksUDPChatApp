#!/usr/bin/env python3
#Created By Adithya Shasty

#This will be the main program that will run both the Server and the Client
# Based on the inputs given when running the script

#import stuff
import sys #this will handle the command line Arguements
from Server import Server
from Client import Client
"""
The Arguements will be taken in the following form:

    Server:
        -s <Port>
    Client:
        -c <nick-name> <server-IP> <server-Port> <client-Port>
"""
def Main(arguments):
    """
    This method will use the system arguments in order to run the correct 
    script and and input the input parameters to the program
    """
    if arguments[0] == '-s':
        #then we want to call the server
        if len(arguments) > 2:
            #we have too many arguments
            print("Too many Arguments!")
        elif len(arguments) < 2:
            #Too few arguments
            print("Not enough Arguments")
        else:
            print("Starting the Server")
            server = Server(int(arguments[1]))
    elif arguments[0] == '-c':
        #We want to start the Client Server
        if len(arguments) < 5:
            #we have too few arguments
            print("Not Enough Arguments!")
        elif len(arguments) > 5:
            #too many arguments
            print("Too many Arguments")
        else:
            #We can start the client
            nick = arguments[1]
            serverIP = arguments[2]
            serverPort = int(arguments[3])
            clientPort = int(arguments[4])
            client = Client(nick,'127.0.0.1',clientPort,serverPort,serverIP)
    else:
        print("Wrong arguments")
    return None













if __name__ == '__main__':
    #we want to run the function above
    Main(sys.argv[1:])



