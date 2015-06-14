from collections import deque
import pyaudio
import audioop
import socket
import subprocess

lamp_on = True

CHUNK = 1024
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 2 
RATE = 44100 #sample rate

p = pyaudio.PyAudio()

stream = p.open(#input_device_index=2,
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK) #buffer

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("localhost",5432))
print "Getting light status"
status = sock.recv(1024)
print "Got status: %s" % status
lamp_on = (status == b"True")
print "Lamp on: %s" % str(lamp_on)

print("* recording")
print(p.get_device_info_by_index(0)['defaultSampleRate'])

peaks = deque()

recent = 0
threshold = 0
while 1:
    if recent > 0:
        recent -= 1
        if not recent:
            threshold = 0
    try:
        data = stream.read(CHUNK)
    except IOError:
        print("Data lost")
        continue
    avg = audioop.max(data,4)
    if avg > 100000000:
        peaks.append(1)
        print(str(avg) + " ***************")
        if recent == 0 and sum(peaks) == 1:
            recent = 15
        else:
            if threshold >= 4 and sum(peaks) < 5:
                recent = 0
                threshold = 0
                print("DOUBLE-CLAP")
                if lamp_on:
                    sock.send("off")
                    #subprocess.Popen("python3 /home/pi/work/lifx-python/lights_off.py", shell=True)
                else:
                    sock.send("on")
                    #subprocess.Popen("python3 /home/pi/work/lifx-python/lights_on.py", shell=True)
                lamp_on = not lamp_on
    else:
        peaks.append(0)
        if recent > 0:
            threshold += 1
        print(avg)
    if len(peaks) > 20:
        peaks.popleft()

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()
