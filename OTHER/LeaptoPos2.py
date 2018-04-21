# events-example0.py
# Barebones timer, mouse, and keyboard events

from Tkinter import *

import random

####################################
# customize these functions
####################################

import sys, thread, time

sys.path.insert(0, "/Users/anishkrishnan/Downloads/LeapDeveloperKit_2.3.1+31549_mac/LeapSDK/lib/")

import Leap

from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class Hand(object):
    
    def init(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 
'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #       frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"
        
            # print "  %s, id %d, position: %s" % (
            #     handType, hand.id, hand.palm_position)

            

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
        # if not (frame.hands.is_empty and frame.gestures().is_empty):
        #     print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

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

def init(data):
    # load data.xyz as appropriate
    data.sqrR = data.width/20
    data.sqrCX = data.sqrR
    data.sqrCY = data.height - data.sqrR
    
    data.sdX = data.width/20
    
    data.bCX = data.width/2
    data.bCY = data.sqrR
    
    data.state = "active"
    data.score = 0

    # Create a sample listener and controller
    data.listener = SampleListener()
    data.controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    data.controller.add_listener(data.listener)




def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if(event.keysym == "Left"):
        data.sqrCX -= data.sdX
    elif(event.keysym == "Right"):
        data.sqrCX += data.sdX
    elif(event.char == "r"):
        data.state = "active"

def timerFired(data):
    data.bCY += data.sdX
    
    if(data.bCY + data.sqrR > data.height):
        data.bCY = data.sqrR
        data.bCX = random.randint(data.sqrR, data.width - data.sqrR)
        data.score += 1
        data.sdX += 0.5 #increases speed every rotation
        
    if(rectanglesOverlap(data.sqrCX-data.sqrR, data.sqrCY-data.sqrR, 
        data.sqrR*2, data.sqrR*2, data.bCX-data.sqrR, data.bCY-data.sqrR, 
        data.sqrR*2, data.sqrR*2)):
        data.score = 0
        data.state = "gameover"


def LeaptoCoord(data):
    
    handData = runLeap(data)
    
    if(handData != None and len(handData) == 2):
        #print("2HANDS")
        left = handData[0]
        #print(left)
        right = handData[1]
        diff = left[1] - right[1]
        #print(diff)
        
        data.sqrCX = (diff*data.width/400) + data.width/2
        
    if(data.sqrCX - data.sqrR < 0):
        data.sqrCX = data.sqrR 
    elif(data.sqrCX + data.sqrR > data.width):
        data.sqrCX = data.width - data.sqrR 

    
    


def redrawAll(canvas, data):
    # draw in canvas
    if(data.state == "gameover"):
        canvas.create_text(data.width/2, 25,
            text = "Game Over!", font = "Arial 26 bold")
        canvas.create_text(data.width/2, 50, 
            text = "press 'r' to restart",
            font = "Arial 10")
    else:
        canvas.create_text(data.width/2, 25,
            text = "Score: " + str(data.score), font = "Arial 26 bold")
            
        LeaptoCoord(data)
        
        canvas.create_rectangle(data.sqrCX - data.sqrR, data.sqrCY - data.sqrR,
            data.sqrCX + data.sqrR, data.sqrCY + data.sqrR, fill="red")
            
        canvas.create_oval(data.bCX - data.sqrR, data.bCY - data.sqrR,
            data.bCX + data.sqrR, data.bCY + data.sqrR, fill="blue")
        
        
def rectanglesOverlap(x1, y1, w1, h1, x2, y2, w2, h2):
    #case1
    if((x2 <= x1 + w1) and (y2 <= y1 + h1)):
        if((x2 >= x1) and (y2 >= y1)):
            return True
    #case2
    if((x2 + w2 <= x1 + w1) and (y2 <= y1 + h1)):
        if((x2 + w2 >= x1) and (y2 >= y1)):
            return True
    #case3
    if((x2 <= x1 + w1) and (y2 + h2 <= y1 + h1)):
        if((x2 >= x1) and (y2 + h2 >= y1)):
            return True
    #case4
    if((x2 + w2 <= x1 + w1) and (y2 + h2 <= y1 + h1)):
        if((x2 + w2 >= x1) and (y2 + h2 + h2 >= y1)):
            return True
    #case5: rect1 is inside rect2
    if((x2 <= x1) and (y2 <= y1)):
        if((x2 + w2 >= x1 + w1) and (y2 + h2 >= y1 + h1)):
            return True
    #case6: rect2 is inside rect1
    if((x1 <= x2) and (y1 <= y2)):
        if((x1 + w1 >= x2 + w2) and (y1 + h1 >= y2 + h2)):
            return True 
             
    #return False if all cases fail        
    return False

####################################
# use the run function as-is
####################################

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

run(400, 400)