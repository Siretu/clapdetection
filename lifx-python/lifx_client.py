import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost",5432))
status = sock.recv(1024)

while 1:
    sock.send(raw_input())
