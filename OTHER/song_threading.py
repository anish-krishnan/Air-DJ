import threading, random

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

def init(data):
    # load data.xyz as appropriate
    pass

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    pass

def timerFired(data):
    pass

def redrawAll(canvas, data):
    canvas.create_rectangle(0, 0, data.width, data.height, fill="blue")
        
            
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 50 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
    
########################
# Main Program
########################
    
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


def printStuff():
    i = 0
    while(True):
        print(i)
        i += 1

if __name__ == '__main__':
    sentence = "I am a handsome beast. Word."
    numThreads = 5
    threadList = []
    
    print("Starting..")



    t1 = threading.Thread(target=play, args=("fadeawayWAV.wav",))
    t1.start()
    
    # t2 = threading.Thread(target=play, args=("grenadeWAV.wav",))
    # t2.start()
    
    # t3 = threading.Thread(target=printStuff, args=())
    # t3.start()
    
    # t4 = threading.Thread(target=run, args=(400, 400,))
    # t4.start()
    
    run(400, 400)
    
    #threadList.append(t1)
    
    
    print("Thread Count: " + str(threading.activeCount()))
    print("Exiting..")
    
    
