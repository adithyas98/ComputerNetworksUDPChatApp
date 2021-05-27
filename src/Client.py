#!/usr/bin/env python3

#Created by Adithya Shastry
#This file will hold all the code needed by the Client in for the UDP Chat
    # Application

from UDPSocket import UDPSocket

if __name__ == '__main__':
    client = UDPSocket(PORT=51000)
    client.connectTo(PORT=50000)


