import _portaudio
import wave
from array import array
from struct import pack

import pyaudio
import numpy as np

CHUNK = 1024
RATE = 44100

wf = wave.open("fadeawayWAV.wav", 'rb')

p=pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)
# for i in range(int(10*44100/1024)): #go for a few seconds
#     data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
#     peak=np.average(np.abs(data))*2
#     bars="#"*int(50*peak/2**16)
#     print("%04d %05d %s"%(i,peak,bars))
    
while len(data) > 0:
    peak=np.average(np.abs(data))*2
    bars="#"*int(50*peak/2**16)
    print("%04d %05d %s"%(i,peak,bars))
    stream.write(data)
    #print("Playing Music")
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()
p.terminate()