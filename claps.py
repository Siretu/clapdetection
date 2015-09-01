#!/usr/bin/env python

from collections import deque
import pyaudio
import audioop
import socket

lamp_on = True

CHUNK = 1024
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 2 
RATE = 44100 #sample rate
THRESHOLD = 10**10
TICKS_BETWEEN_CLAPS = 15

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK) #buffer

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to local lifx server and get light power status

sock.connect(("localhost",5432))
print("Getting light status")
status = sock.recv(1024)
print("Got status: %s" % status)
lamp_on = (status == b"True")
print("Lamp on: %s" % str(lamp_on))


latest_chunks = deque() # Latest 20 chunks. 0's are below threshold, 1's are above threshold.

recent = 0
non_peaks = 0
avg = []
while 1:
    # Decrease recent, and reset non_peaks when it reaches 0
    if recent > 0:
        recent -= 1
        if not recent:
            non_peaks = 0

    # Read audio data from stream
    try:
        data = stream.read(CHUNK)
    except IOError:
        print("Data lost")
        continue

    
    max_level = audioop.max(data,4)
    if len(avg) < 30:
        avg.append(max_level)
    elif len(avg) == 30:
        THRESHOLD = sum(avg)/len(avg)*4
        print "Set threshold to: %d" % THRESHOLD
        avg.append(avg[0])

    if max_level > THRESHOLD:
        latest_chunks.append(1)
        print(str(max_level) + " ***************")
        
        # Got first clap
        if recent == 0 and sum(latest_chunks) == 1:
            recent = TICKS_BETWEEN_CLAPS
        # Got second clap
        elif non_peaks >= 4 and sum(latest_chunks) < 8:
            # Reset
            recent = 0
            non_peaks = 0
            print("DOUBLE-CLAP")
            if lamp_on:
                sock.send("off")
            else:
                sock.send("on")
            lamp_on = not lamp_on
    else:
        latest_chunks.append(0)
        if recent > 0:
            non_peaks += 1
        print(max_level)

    # Keep size of latest_chunks at 20
    if len(latest_chunks) > 20:
        latest_chunks.popleft()

stream.stop_stream()
stream.close()
p.terminate()
