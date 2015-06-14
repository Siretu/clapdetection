#!/usr/bin/env python3

import lifx
import socket
import sys
from time import sleep

print("Initializing light")
light = lifx.get_lights()[0]
print("Light done")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
print("Socket created")

try:
    sock.bind(("localhost",5432))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg))
    sys.exit()

print("Socket bind complete")

sock.listen(1)
print("Socket now listening")
try:
    while 1:
        conn, addr = sock.accept()
        print("Connected to client")
        conn.send(bytes(str(light.power),"UTF-8"))

        while 1:
            data = conn.recv(1024)
            if not data:
                break
            print("Got data: %s" % data)
            if data == b"on":
                print("Turning on lights!")
                lifx.set_power(lifx.BCAST, True)
            elif data == b"off":
                print("Turning off lights!")
                lifx.set_power(lifx.BCAST, False)
            
        conn.close()
finally:
    sock.close()
