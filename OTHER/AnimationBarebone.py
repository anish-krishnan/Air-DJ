# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *

import math, random

####################################
# customize these functions
####################################



def init(data):
    # load data.xyz as appropriate
    
    data.image = PhotoImage(file="c6.gif")
    
    data.image = data.image.zoom(4, 3)

    
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

    

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def timerFired(data):
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

def redrawAll(canvas, data):
    # draw in canvas
    

    
    for i in range(data.numCircles):
        cX, cY = data.circleList[i][0], data.circleList[i][1]
        color = data.circleList[i][2]
        r = data.circleList[i][5]
        canvas.create_oval(cX-r, cY-r, cX+r, cY+r, fill=color, width=0)
        #canvas.create_text(cX, cY, text=str(i))
    
    canvas.create_image(50, 50, anchor = NW, image = data.image)
    
    # mycolor = '#%02x%02x%02x' % (64, 204, 208)
    

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
    data.timerDelay = 5 # milliseconds
    
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