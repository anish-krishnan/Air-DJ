####################################
# AIR-DJ!
# Made with <3 by Anish Krishnan 
#
# MOST RECENT EDIT: 4/21/2018
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

#Volume control
import osascript

#Photo Image Library
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


#initializes all attributes when program is first run
def init(data):
    
    #Splash/Instruction Screen Attributes
    data.logoImage = PhotoImage(file="img/logo.gif")
    data.splashImage = PhotoImage(file="img/djPersonCrop.gif")
    data.instructImage = PhotoImage(file="img/djLights.gif")
    data.mode = "SPLASH" #SPLASH or INSTRUCT or DJ
    data.splashBall = [data.width/2, data.height/2 + 50]
    data.sBallR = 10
    
    data.m = data.height/20
    data.dockHeight = data.height/3*2
    initVisual(data)
    
    #Song Attributes
    data.threadList = []
    data.musicList = getMusicList("music")
    data.curSong = (0, data.musicList[0])
    data.beatPlaying = False
    data.switchCounter = 0
    
    #Volume Attributes
    data.curVolume = 40
    data.dVol = 5
    data.maxVol = 80
    data.speedRamp = 1
    
    #color attributes
    data.circleColor = '#%02x%02x%02x' % (245, 82, 71)
    data.dark = '#%02x%02x%02x' % (54, 63, 112)#(50, 46, 77)
    data.light = '#%02x%02x%02x' % (116, 137, 242)#(172, 163, 230)
    
    #disk position attributes
    data.Lcircle = (data.width/4, (data.dockHeight)/2)
    data.Rcircle = (data.width/2, (data.dockHeight)/2 + data.m/2)
    data.rL = (data.dockHeight)/3
    data.rR = (data.dockHeight)/3
    data.angle = 0
    
    #Beat disks (x, y, rad, color, angle)
    data.bCol = '#%02x%02x%02x' % (116, 137, 242)
    data.bR = 30
    data.bA = 0
    data.beatDisks = {"UP": [data.width/2, data.m/2+data.m+data.bR, data.bR,
    data.bCol, data.bA], 
        "RIGHT": [data.width-data.bR-data.m, data.dockHeight/2, data.bR,
        data.bCol, data.bA],
        "DOWN": [data.width/2, data.dockHeight-data.bR-data.m/2, data.bR,
        data.bCol, data.bA],
        "LEFT": [data.bR+data.m, data.dockHeight/2, data.bR, data.bCol,
        data.bA]}
        
    #Line Attributes
    data.horizY = data.height/2
    data.vertX = data.width/2
    
    data.songSwitchBarX = data.width/2
    
    #sample listener and controller for Leap Motion
    data.listener = SampleListener()
    data.controller = Leap.Controller()
    data.controller.add_listener(data.listener)
    
    data.counter = 0

#initialize attributes for visualizer
def initVisual(data):
    data.circleList = [] #(cx, cy, color)
    data.numCircles = 50
    for i in range(data.numCircles):
        rad = random.randint(2, 8)
        x = random.randint(rad, data.width - rad)
        y = random.randint(data.m + rad, data.dockHeight - rad)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        dx, dy = random.randint(-5 ,5), random.randint(-5 ,5)
        if(dx == 0): dx = 1
        if(dy == 0): dy = 1
        data.circleList.append([x, y, '#%02x%02x%02x'%(r, g, b), dx, dy, rad])    

#Scales a value from an old range to a new range
def scaleValues(oldMin, oldMax, newMin, newMax, oldValue):
    oldRange = oldMax - oldMin  
    newRange = newMax - newMin
    #newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
    newValue = oldValue - oldMin
    newValue *= newRange
    newValue /= oldRange
    newValue += newMin
    return newValue

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

#Switchs song to seek tracks (Forwards/Backwards)
def switchSong(data, direction):
    if(direction == "NEXT"):
        num = data.curSong[0]
        if(num+1 < 4):
            data.curSong = [num+1, data.musicList[num+1]]
    elif(direction == "PREV"):
        num = data.curSong[0]
        if(num-1 >= 0):
            data.curSong = [num-1, data.musicList[num-1]]
    if(len(data.threadList)>0):
        data.threadList.pop(0)
    for key in stopSong:
        stopSong[key] = False
    stopSong[data.curSong[1]] = True
    data.threadList.append(threading.Thread(target=play, 
        args=("music/"+data.curSong[1], data,)))
    data.threadList[-1].start()

#Returns True if a song is currently playing
def songPlaying():
    for key in stopSong:
        if(stopSong[key]):
            return True
    return False
    
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
    if(event.keysym == "Up"):
        data.curVolume += data.dVol
    elif(event.keysym == "Down"):
        data.curVolume -= data.dVol
    elif(event.char == 'q'):
        exit()

#Called every timerDelay-interval
def timerFired(data):
    t1 = threading.Thread(target=timerHelper, args=(data,))
    t1.start()
    
    if(data.switchCounter > 0):
        data.switchCounter += 1
    if(data.switchCounter > 10):
        data.switchCounter = 0
    if(songPlaying()):
        data.angle -= 5
    if(data.beatPlaying):
        for key in data.beatDisks:
            if(data.beatDisks[key][3] == "green"):
                data.beatDisks[key][4] -= 10
    
def timerHelper(data):
    #data.speedRamp = max(1, data.curVolume/10)
    for i in range(data.numCircles):
        dX = data.circleList[i][3] * max(1, data.speedRamp)
        dY = data.circleList[i][4] * max(1, data.speedRamp)
        dX = dX
        dY = dY
        data.circleList[i][0] += dX
        data.circleList[i][1] += dY
        x, y = data.circleList[i][0], data.circleList[i][1]
        r = data.circleList[i][5]
        if(x-r<0 or x+r>data.width):
            data.circleList[i][0] -= dX
            data.circleList[i][3] = -dX
        if(y-r<data.m or y+r>data.dockHeight):
            data.circleList[i][1] -= dY
            data.circleList[i][4] = -dY

#If there are two hands, you can add beats with your left hand while
#controlling the volume with your right hand
def twoHandHelper(data, handData):
    left, right = handData[0], handData[1]
    data.horizY = scaleValues(120, -60, data.dockHeight-2*data.m, 3*data.m, left[2])
    data.vertX = scaleValues(-150, -45, 3*data.m, data.width-3*data.m, left[0])
    if(data.vertX < 0): data.vertX = 0
    if(data.vertX > data.width): data.vertX = data.width
    data.songSwitchBarX = scaleValues(55, 150, data.width/4, data.width*3/4, right[0])
    
    #Checks Gesture Recognition
    if(right[0] > 150 and data.switchCounter == 0):
        switchSong(data, "NEXT")
        data.switchCounter = 1
    if(right[0] < 55 and data.switchCounter == 0):
        switchSong(data, "PREV")
        data.switchCounter = 1
    if(not data.beatPlaying and left[2] < -60):
        data.beatDisks["UP"][3] = "green"
        data.beatPlaying = True
        data.threadList.append(threading.Thread(target=play, 
            args=("beats/BamBamBamWAV.wav", data, )))
        data.threadList[-1].start()
    elif(not data.beatPlaying and left[0] < -150):
        data.beatDisks["LEFT"][3] = "green"
        data.beatPlaying = True
        data.threadList.append(threading.Thread(target=play, 
            args=("beats/BasicCoreBeatWAV.wav", data, )))
        data.threadList[-1].start()
    if(not data.beatPlaying and left[2] > 120):
        data.beatDisks["DOWN"][3] = "green"
        data.beatPlaying = True
        data.threadList.append(threading.Thread(target=play, 
            args=("beats/DeepBeatMOD.wav", data, )))
        data.threadList[-1].start()
    if(not data.beatPlaying and left[0] > -45):
        data.beatDisks["RIGHT"][3] = "green"
        data.beatPlaying = True
        data.threadList.append(threading.Thread(target=play, 
            args=("beats/FreeBeat.wav", data, )))
        data.threadList[-1].start()
        
    data.rL, data.rR = right[1],right[1]
    if(data.rR > data.dockHeight/2 - data.m):
        data.rR, data.rL = data.dockHeight/2-data.m, data.dockHeight/2-data.m
        data.rL = data.dockHeight/2 - data.m 
    data.curVolume = int(min(data.maxVol, right[1]/4))

    
#If there is only one hand, you can switch between disk sides and control
#disks seperately
def oneHandHelper(data, handData):
    right = handData[0]
    if(data.mode != "DJ"):
        rX, rY = right[0], right[1]
        x = scaleValues(-100, 100, 0, data.width, rX)
        y = scaleValues(60, 320, data.height, 0, rY)
        data.splashBall = [x, y]
        
    data.rR = right[1]
    if(data.rR > data.dockHeight/2 - data.m):
        data.rR = data.dockHeight/2 - data.m
    data.curVolume = int(min(data.maxVol, right[1]/4))

#Uses data from Leap to accordinly change attributes
def LeapProcess(data):
    handData = runLeap(data)
    
    #There are two hands in the frame
    if(handData != None and len(handData) == 2):
        if(data.mode == "DJ"):
            twoHandHelper(data, handData)
     
    #There is one hand in the frame
    elif(handData != None and len(handData) == 1):
        oneHandHelper(data, handData)
    
#Redraws canvas
def redrawAll(canvas, data):
    #DJ screen
    if(data.mode == "DJ"):
        redrawAllDJ(canvas, data)
    #Splash Screen
    elif(data.mode == "SPLASH"):
        redrawSplash(canvas, data)
    #Instruction Screen
    elif(data.mode == "INSTRUCT"):
        redrawInstruct(canvas, data)
        

#Redraws the tkinter
def redrawAllDJ(canvas, data):
    # t1 = threading.Thread(target=drawVisual, args=(canvas, data, ))
    # t1.start()
    drawVisual(canvas, data)
    
    drawLines(canvas, data)
    
    data.counter += 1
    LeapProcess(data)
    
    #Sets volume to current volume
    if(data.counter % 6 == 0):
        osascript.osascript("set volume output volume " + str(data.curVolume))
    drawDisks(canvas, data)
    drawBeatDisks(canvas, data)
    canvas.create_text(data.width/2, data.dockHeight+10, text="Music",
        fill="white", anchor=N)
    drawDock(canvas, data)
    
    canvas.create_rectangle(0, data.dockHeight-0.5*data.m,
        data.width, data.dockHeight, width=0, fill="purple")
    canvas.create_rectangle(data.width/2, data.dockHeight-0.5*data.m, 
        data.songSwitchBarX, data.dockHeight, width=0, fill="blue")
    canvas.create_rectangle(data.width/4, data.dockHeight-0.5*data.m, 
        data.width/4 + 5, data.dockHeight, width=0, fill="green")
    canvas.create_rectangle(data.width*3/4, data.dockHeight-0.5*data.m, 
        data.width*3/4 + 5, data.dockHeight, width=0, fill="green")
        
#redraw the splash screen
def redrawSplash(canvas, data):
    canvas.create_image(0, 0, anchor = NW, image = data.splashImage)
    canvas.create_image(data.width/2, data.height*7/10, anchor = CENTER, 
        image = data.logoImage)
    data.logoImage
    LeapProcess(data)
    [x, y] = data.splashBall
    
    canvas.create_rectangle(0, 0, 290, 30, fill="black")
    canvas.create_text(10, 10, text="Move the cursor with your hand!", 
        font="Arial 20", anchor=NW, fill="white")
    canvas.create_rectangle(data.width-150, 0, data.width,150, fill="green",
        width=0)
    canvas.create_rectangle(data.width-150, 150, data.width,300, fill="purple",
        width=0)
    canvas.create_text(data.width-75, 75, text="START", 
        font="Arial 20 bold", anchor=CENTER)
    canvas.create_text(data.width-75, 225, text="INSTRUCTIONS", 
        font="Arial 20 bold", anchor=CENTER)
    
    canvas.create_oval(x-data.sBallR, y-data.sBallR, x+data.sBallR, 
        y+data.sBallR, fill="white", width=0)
    canvas.create_oval(x-data.sBallR/2, y-data.sBallR/2, x+data.sBallR/2, 
        y+data.sBallR/2, fill="blue", width=0)
        
    if(x > data.width-150):
        if(y < 150):
            data.mode = "DJ"
        elif(y > 150 and y < 300):
            data.mode = "INSTRUCT"

#redraws the instruction screen
def redrawInstruct(canvas, data):
    canvas.create_image(0, 0, anchor = NW, image = data.instructImage)
    
    LeapProcess(data)
    [x, y] = data.splashBall
    
    canvas.create_rectangle(0, 0, 150,150, fill="red",
        width=0)
    canvas.create_text(75, 75, text="BACK", 
        font="Arial 20 bold", anchor=CENTER, fill="white")
        
    canvas.create_text(data.width/2, 75, text="Instructions", 
        font="Arial 50 bold", anchor=CENTER, fill="white")
        
    canvas.create_text(data.width/2, 110, text="You're in control now", 
        font="Arial 20 bold", anchor=CENTER, fill="white")
        
    canvas.create_text(data.width/5, 200, text="1. Raising/Lowering your" + 
        " right hand\n will increase/decrease the volume.", 
        font="Arial 30 bold", anchor=W, fill="white")
    
    canvas.create_text(data.width/5, 300, text="2. Swiping your right hand"+ 
        " to the\n left/right lets you seek tracks.", 
        font="Arial 30 bold", anchor=W, fill="white")
    
    canvas.create_text(data.width/5, 430, text="3. Moving your left hand"+ 
        " in the X/Z\n plane allows you to add 4 \ndifferent types of"+
        " beats shown by\n the 4 smaller circles around the screen.", 
        font="Arial 28 bold", anchor=W, fill="white")
        
    canvas.create_text(data.width/2, 600, text="Have fun making your"+ 
        " next greatest hit!", 
        font="Arial 30 bold", anchor=CENTER, fill="white")
    
    canvas.create_oval(x-data.sBallR, y-data.sBallR, x+data.sBallR, 
        y+data.sBallR, fill="white", width=0)
    canvas.create_oval(x-data.sBallR/2, y-data.sBallR/2, x+data.sBallR/2, 
        y+data.sBallR/2, fill="blue", width=0)
    if(x < 150 and y < 150):
            data.mode = "SPLASH"
 
#Draws Background Visual
def drawVisual(canvas, data):
    for i in range(data.numCircles):
        cX, cY = data.circleList[i][0], data.circleList[i][1]
        color = data.circleList[i][2]
        factor = (float)(data.curVolume)/20
        if(factor <= 0): factor = 1
        r = factor*data.circleList[i][5]
        canvas.create_oval(cX-r, cY-r, cX+r, cY+r, fill=color, width=0) 

#Draws lines to show position of left hand
def drawLines(canvas, data):
    
    canvas.create_line(0, data.horizY, data.width, data.horizY)
    canvas.create_line(data.vertX, 0, data.vertX, data.height)

#Draws the disks
def drawDisks(canvas, data):
        
    canvas.create_oval(data.Rcircle[0]-data.rR, data.Rcircle[1]-data.rR,
        data.Rcircle[0]+data.rR, data.Rcircle[1]+data.rR, fill=data.circleColor,
        width = 0)
        
    canvas.create_arc(data.Rcircle[0]-data.rR, data.Rcircle[1]-data.rR,
        data.Rcircle[0]+data.rR, data.Rcircle[1]+data.rR,
        start=data.angle,extent=30, style=PIESLICE,fill="black", width=0)
    
    canvas.create_rectangle(0, 0, data.width, data.m, fill=data.dark)
    
    canvas.create_text(10, 10, text = "Volume: " + str(data.curVolume),
        fill="white", font = "Arial 10", anchor = NW)
    
    canvas.create_text(data.width/2, 10, text="Playing: " + getReadableFile(
        data.curSong[1]), fill="white", anchor=N)
        
    canvas.create_rectangle(0, data.dockHeight, data.width, data.height,
        fill=data.dark)

#Draws the 4 disk beats
def drawBeatDisks(canvas, data):
    for beat in data.beatDisks:
        beatDisk = data.beatDisks[beat]
        x, y, r, c = beatDisk[0], beatDisk[1], beatDisk[2], beatDisk[3]
        a = beatDisk[4]
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=c, width = 0)
        canvas.create_arc(x-r, y-r, x+r, y+r,
        start=a,extent=30, style=PIESLICE,fill="black", width=0)
  
#Draws the dock for choosing music
def drawDock(canvas, data):
    data.numSongs = data.width/(data.height-data.dockHeight)
    data.numSongs = 4
    for i in range(data.numSongs):
        bgColor = data.dark
        textColor = "white"
        if(data.musicList[i] == data.curSong[1]):
            bgColor = data.light
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
    if(file == "beats/BamBamBamWAV.wav" or file == "beats/BasicCoreBeatWAV.wav" 
        or file == "beats/DeepBeatMOD.wav" or file == "beats/FreeBeat.wav"):
        data1.beatPlaying = False
        for beat in data1.beatDisks:
            data1.beatDisks[beat][3] = '#%02x%02x%02x' % (116, 137, 242)
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


run(700, 700)
