#!/usr/bin/env python3

#Created by Adithya Shastry
#This file will hold all the code needed by the Client in for the UDP Chat
    # Application

from UDPSocket import UDPSocket

if __name__ == '__main__':
    client = UDPSocket(PORT=51000)
    MSG = [1,1,[4,5,6]]
    print(client.secureSend(MSG,PORT=50000))


