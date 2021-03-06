####################################
# AIR-DJ!
# Made with <3 by Anish Krishnan 
#
# Andrew ID: agkrishn
#
# MOST RECENT EDIT: 11/29/2017
####################################
from Tkinter import *

import random

#threading
import threading, os

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

#Volume control
import osascript

from PIL import Image, ImageTk

####################################
# LEAP MOTION CODE
####################################
import sys, thread, time

sys.path.insert(0, 
"/Users/anishkrishnan/Downloads/LeapDeveloperKit_2.3.1+31549_mac/LeapSDK/lib/")

import Leap

from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

#Leap Motion Starter Framework by Leap
#The following code was modified by me but originally coded and provided by 
#Leap

#The hand class containing x,y,z coordinates of a hand
class Hand(object):
    
    def init(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

#Listener for the Leap Motion
class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 
'STATE_END']

    #Called when initialized
    def on_init(self, controller):
        print "Initialized"

    #Called when Leap Motion is connected to the computer
    def on_connect(self, controller):
        print "Connected"

    #Called when Leap Motion disconnects from the computer
    def on_disconnect(self, controller):
        print "Disconnected"

    #Called when program is finished and Leap Motion stops tracking data
    def on_exit(self, controller):
        print "Exited"

    #Called on each frame (120 fps)
    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"
            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

#Method that I made that returns the x,y,z coordinates of each hand in a tuple
def runLeap(data):
    frame = data.controller.frame()
    if(len(frame.hands) == 0):
        return None
    elif(len(frame.hands) == 1):
        hand = frame.hands.rightmost
        position = hand.palm_position
        
        return [position]
    elif(len(frame.hands) == 2):
        hand1 = frame.hands.leftmost
        hand2 = frame.hands.rightmost
        position1 = hand1.palm_position
        position2 = hand2.palm_position
        
        return [position1, position2]



####################################
# customize these functions
####################################

#Global variable to keep track of which songs are playing
stopSong = dict()

#Gets all music from the 'music' folder adds it to a list and the stopSong dict
def getMusicList(path):
    musicList = os.listdir(path)
    for i in musicList:
        stopSong[i] = False
    return musicList[1:]

#Converts file names to readable names (ex. Fade_AwayWAV.wav --> Fade Away)
def getReadableFile(fileName):
    wavPos = fileName.find("WAV")
    fileName = fileName[:wavPos]
    name = ""
    for i in range(len(fileName)):
        if(fileName[i] == "_"):
            name = name + " "
        else:
            name = name + fileName[i]
    return name

def songPlaying():
    for key in stopSong:
        if(stopSong[key]):
            return True
    return False


def initVisual(data):
    data.image = PhotoImage(file="dj.gif")
    data.image = data.image.zoom(1, 1)
    
    data.circleList = [] #(cx, cy, color)
    data.numCircles = 50
    for i in range(data.numCircles):
        rad = random.randint(5, 15)
        x = random.randint(rad, data.width - rad)
        y = random.randint(rad, data.height - rad)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        dx, dy = random.randint(-10 ,10), random.randint(-10 ,10)
        if(dx == 0): dx = 1
        if(dy == 0): dy = 1
        data.circleList.append([x, y, '#%02x%02x%02x' % (r, g, b), dx, dy, rad])

#initializes all attributes when program is first run
def init(data):
    
    initVisual(data)
    
    #Song Attributes
    data.threadList = []
    data.musicList = getMusicList("music")
    data.curSong = (0, data.musicList[0])
    data.song = AudioSegment.from_wav("fadeawayWAV.wav")
    data.beatPlaying = False
    print(stopSong)
    
    #Volume Attributes
    data.curVolume = 40
    data.dVol = 5
    data.maxVol = 50
    
    #color attributes
    data.bgColor = "blue"
    data.circleColor = "red"
    
    #Misc. Attributes
    data.side = "RIGHT"
    data.dockHeight = data.height/3*2
    
    #disk position attributes
    data.Lcircle = (data.width/4, (data.dockHeight)/2)
    data.Rcircle = (data.width/4*3, (data.dockHeight)/2)
    data.rL = (data.dockHeight)/3
    data.rR = (data.dockHeight)/3
    data.m = data.height/20
    data.angle = 0
    
    #sample listener and controller for Leap Motion
    data.listener = SampleListener()
    data.controller = Leap.Controller()
    data.controller.add_listener(data.listener)
    
    data.counter = 0

#Called when the mouse is clicked
def mousePressed(event, data):
    if(event.y < data.dockHeight or event.y > data.height):
        return
    box = event.x/(data.width/data.numSongs)
    data.curSong = (box, data.musicList[box])
    if(len(data.threadList)>0):
        data.threadList.pop(0)
    for key in stopSong:
        stopSong[key] = False
    stopSong[data.curSong[1]] = True
    #new song played using a new thread so that animation can occur at the 
    #same time
    data.threadList.append(threading.Thread(target=play, 
        args=("music/"+data.curSong[1], data,)))
    data.threadList[-1].start()

#Called when a key is pressed
def keyPressed(event, data):
    if(event.keysym == "Left"):
        data.side = "LEFT"
    elif(event.keysym == "Right"):
        data.side = "RIGHT"
        
    elif(event.keysym == "Up"):
        data.curVolume += data.dVol
    elif(event.keysym == "Down"):
        data.curVolume -= data.dVol

#Called every timerDelay-interval
def timerFired(data):
    t1 = threading.Thread(target=timerHelper, args=(data,))
    t1.start()
    
    if(songPlaying()):
        data.angle -= 5
    
def timerHelper(data):
    for i in range(data.numCircles):
        dX, dY = data.circleList[i][3], data.circleList[i][4]
        data.circleList[i][0] += dX
        data.circleList[i][1] += dY
        x, y = data.circleList[i][0], data.circleList[i][1]
        r = data.circleList[i][5]
        if(x-r<0 or x+r>data.width):
            data.circleList[i][0] -= dX
            data.circleList[i][3] = -dX
        if(y-r<0 or y+r>data.height):
            data.circleList[i][1] -= dY
            data.circleList[i][4] = -dY

#If there are two hands, you can add beats with your left hand while
#controlling the volume with your right hand
def twoHandHelper(data, handData):
    left, right = handData[0], handData[1]
    if(not data.beatPlaying and left[2] < -60):
        data.beatPlaying = True
        data.threadList.append(threading.Thread(target=play, 
            args=("BamBamBamWAV.wav", data, )))
        data.threadList[-1].start()
    data.rL, data.rR = right[1],right[1]
    if(data.rR > data.dockHeight/2 - data.m):
        data.rR, data.rL = data.dockHeight/2-data.m, data.dockHeight/2-data.m
        data.rL = data.dockHeight/2 - data.m 
    data.curVolume = int(min(data.maxVol, right[1]/4))
    data.side = "BOTH"
    
#If there is only one hand, you can switch between disk sides and control
#disks seperately
def oneHandHelper(data, handData):
    right = handData[0]
    if(right[0] < 0):
        data.side = "LEFT"
        data.rL = right[1]
        if(data.rL > data.dockHeight/2 - data.m):
            data.rL = data.dockHeight/2 - data.m
    else:
        data.side = "RIGHT"
        data.rR = right[1]
        if(data.rR > data.dockHeight/2 - data.m):
            data.rR = data.dockHeight/2 - data.m
    data.curVolume = int(min(data.maxVol, right[1]/4))

#Uses data from Leap to accordinly change attributes
def LeapProcess(data):
    handData = runLeap(data)
    
    #There are two hands in the frame
    if(handData != None and len(handData) == 2):
        twoHandHelper(data, handData)
     
    #There is one hand in the frame
    elif(handData != None and len(handData) == 1):
        oneHandHelper(data, handData)
    
        
#Redraws the tkinter
def redrawAll(canvas, data):
    # t1 = threading.Thread(target=drawVisual, args=(canvas, data, ))
    # t1.start()
    drawVisual(canvas, data)
    
    data.counter += 1
    LeapProcess(data)
    
    #Sets volume to current volume
    if(data.counter % 6 == 0):
        osascript.osascript("set volume output volume " + str(data.curVolume))
    #Sets which side the hand is on
    if(data.side == "RIGHT"):
        canvas.create_rectangle(data.width/2, 0, data.width, data.height,
            fill=data.bgColor)
    elif(data.side == "LEFT"):
        canvas.create_rectangle(0, 0, data.width/2, data.height,
            fill=data.bgColor)
    elif(data.side == "BOTH"):
        canvas.create_rectangle(0, 0, data.width, data.height,
            fill=data.bgColor)
        canvas.create_line(data.width/2, 0, data.width/2, data.height,
            fill="black")
    drawDisks(canvas, data)
    canvas.create_text(data.width/2, data.dockHeight+10, text="Music",
        fill="white", anchor=N)
    drawDock(canvas, data)
    
    #canvas.create_image(400, 300, anchor = CENTER, image = data.image)
 
#Draws Background Visual
def drawVisual(canvas, data):
    for i in range(data.numCircles):
        cX, cY = data.circleList[i][0], data.circleList[i][1]
        color = data.circleList[i][2]
        r = data.circleList[i][5]
        canvas.create_oval(cX-r, cY-r, cX+r, cY+r, fill=color, width=0) 

#Draws the disks
def drawDisks(canvas, data):
    canvas.create_oval(data.Lcircle[0]-data.rL, data.Lcircle[1]-data.rL,
        data.Lcircle[0]+data.rL, data.Lcircle[1]+data.rL, fill=data.circleColor,
        width = 0)
    
    canvas.create_arc(data.Lcircle[0]-data.rL, data.Lcircle[1]-data.rL,
        data.Lcircle[0]+data.rL, data.Lcircle[1]+data.rL,
        start=data.angle,extent=30, style=PIESLICE,fill="black", width=0)
        
    canvas.create_oval(data.Rcircle[0]-data.rR, data.Rcircle[1]-data.rR,
        data.Rcircle[0]+data.rR, data.Rcircle[1]+data.rR, fill=data.circleColor,
        width = 0)
        
    canvas.create_arc(data.Rcircle[0]-data.rR, data.Rcircle[1]-data.rR,
        data.Rcircle[0]+data.rR, data.Rcircle[1]+data.rR,
        start=data.angle,extent=30, style=PIESLICE,fill="black", width=0)
    
    canvas.create_rectangle(0, 0, data.width, data.m, fill="black")
    
    canvas.create_text(10, 10, text = "Volume: " + str(data.curVolume),
        fill="white", font = "Arial 10", anchor = NW)
    
    canvas.create_text(data.width/2, 10, text="Playing: " + getReadableFile(
        data.curSong[1]), fill="white", anchor=N)
        
    canvas.create_rectangle(0, data.dockHeight, data.width, data.height,
        fill="black")
  
#Draws the dock for choosing music
def drawDock(canvas, data):
    data.numSongs = data.width/(data.height-data.dockHeight)
    for i in range(data.numSongs):
        bgColor = "black"
        textColor = "white"
        if(data.musicList[i] == data.curSong[1]):
            bgColor = "white"
            textColor = "black"
        coord = [i*data.width/data.numSongs, data.dockHeight+data.m,
            (i+1)*data.width/data.numSongs, data.height]
        canvas.create_rectangle(coord[0], coord[1], coord[2], coord[3],
            fill=bgColor, outline = "white", width = 2)
        songName = getReadableFile(data.musicList[i])
        canvas.create_text((coord[2]+coord[0])/2, (coord[3]+coord[1])/2,
            text=songName, fill=textColor, anchor=CENTER, font="Arial 30")

#Uses PyAudio to play a song (PyAudio Starter code modified from 112 TA's)
def play(file, data1):
    file1 = file
    if(file.find("music/") != -1):
        file1 = file[6:]
    CHUNK = 1024
    wf = wave.open(file, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        if(file1 in stopSong and stopSong[file1] == False):
            break
        stream.write(data)
        data = wf.readframes(CHUNK)
    if(file == "BamBamBamWAV.wav" or file == "BasicCoreBeatWAV.wav"):
        data1.beatPlaying = False
    stream.stop_stream(), stream.close(), p.terminate()
    

####################################
# use the run function as-is
####################################

#Run function from animation core framework
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
    data.timerDelay = 1 # milliseconds
    # create the root and the canvas
    root = Tk()
    init(data)
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

run(800, 600)
