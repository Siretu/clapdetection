#!/usr/bin/env python3

import lifx
import socket
import sys
from time import sleep

print("Initializing light")
light = lifx.get_lights()[0]
print(light.addr)
print(light.hue)
print(light.saturation)
print(light.brightness)
print(light.kelvin)
print(light.dim)
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
            light = lifx.get_lights()[0]
            print("%s,%s,%s,%s" % (light.hue, light.saturation, light.brightness, light.kelvin))
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break
            print("Got data: '%s'" % data)
            info = data.split(":")
            if data == "on":
                print("Turning on lights!")
                lifx.set_power(lifx.BCAST, True)
            elif data == "off":
                print("Turning off lights!")
                lifx.set_power(lifx.BCAST, False)
            elif info[0] == "hue":
                hue = int(info[1])
                print("Setting hue to %d" % hue)
                lifx.set_color(lifx.BCAST,hue,light.saturation,light.brightness,light.kelvin,1)
            elif info[0] == "saturation":
                saturation = int(info[1])
                print("Setting saturation to %d" % saturation)
                lifx.set_color(lifx.BCAST,light.hue,saturation,light.brightness,light.kelvin,1)
            elif info[0] == "brightness":
                brightness = int(info[1])
                print("Setting brightness to %d" % brightness)
                lifx.set_color(lifx.BCAST,light.hue,light.saturation,brightness,light.kelvin,1)
            elif info[0] == "kelvin":
                kelvin = int(info[1])
                print("Setting kelvin to %d" % kelvin)
                lifx.set_color(lifx.BCAST,light.hue,light.saturation,light.brightness,kelvin,1)
            elif data == "default":
                lifx.set_color(lifx.BCAST,55000,0,55000,3200,1)
        conn.close()
finally:
    sock.close()
