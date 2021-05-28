#!/usr/bin/env python3

#Created By Adithya Shastry
#This file holds all the code that will be used by the Server in the UDP
# Chat application
from UDPSocket import UDPSocket
import time
if __name__ == '__main__':
    server = UDPSocket(PORT=50000)
    data = server.secureRecieve()
    print(data)

