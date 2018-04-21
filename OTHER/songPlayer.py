from Tkinter import *

#pyAudio
import _portaudio
import pyaudio
import wave
from array import array
from struct import pack

#pydub
import pydub
from pydub.playback import play
from pydub import AudioSegment



    

# def playSong(data):
#     print("starting...")
#     play(data.song)
#     print("song over!")
    
def play(file):
    CHUNK = 1024

    wf = wave.open(file, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while len(data) > 0:
        stream.write(data)
        #print("Playing Music")
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()
    

play("fadeawayWAV.wav")

