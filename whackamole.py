#! /usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL
import sys
import getopt
import array
import random
from math import *


objectXform = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
]

#The global viewing angle 
theta = [0.0,0.0,0.0]
thetaIncr = 5.0

#A global for the amount of time a mole is up
moleTime = 3000

#a global for the current score
score = 0

#a little class for each of the moles
class Mole:
    moleNumber = 99#bogus data...
    moleStatus = 'MOLE_DOWN' 
    #The constructor
    def __init__(self,id):
        self.moleNumber = id

    def drawMole(self,mode):
        glPushMatrix()
        glRotatef(90,1.0,0.0,0.0)

        if(mode == GL_SELECT):
            glLoadName(self.moleNumber)
        if(self.moleStatus == 'MOLE_DOWN'):
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 0.3, 0.0, 1.0])
        else:
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glutSolidCylinder(.3,1.0,20,20)

        glPopMatrix()

    def showMole(self):
        global moleTime
        self.moleStatus = 'MOLE_UP'
        glutTimerFunc(moleTime,self.moleDown,0)
        display()

    def moleDown(self,step):
        self.moleStatus = 'MOLE_DOWN'
        display()


#The global list of moles
moles = []

def main():
    global moleTime
    global moles
    for i in range(0,9):
        moles.append(Mole(i))

    argc = len(sys.argv)
    glutInit(argc,sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(700, 700)
    glutInitWindowPosition(100, 100)
    glutCreateWindow("Whack-A-Mole!")
    glEnable(GL_DEPTH_TEST)

    #This function is what acctually draws stuff... It's called
    #every time the window is redrawn
    glutDisplayFunc(display)
    glutReshapeFunc(reshapeCallback)
    glutMouseFunc(mouseCallback)
    glutKeyboardFunc(keyCallback)
    glutTimerFunc(moleTime/2,randomMole,1)
    glutMainLoop()

def randomMole(step):
    global moles
    moles[random.randint(0,8)].showMole()
    glutTimerFunc(moleTime/2,randomMole,1)
    display()


def display():
    #This code runs wheever the window is redrawn
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    setUpView()
    setUpLight()
    setUpModelTransform()

    glPushMatrix()
    glMultMatrixf(objectXform)
    drawObjs(GL_RENDER)
    glPopMatrix()
    glutSwapBuffers()


def drawObjs(mode):
    drawBoard(mode)
    drawMoles(mode)
    return

def drawBoard(mode):
    if(mode == GL_SELECT):
        glLoadName(999)

    glPushMatrix()
    glScalef(5.0,1.0,5.0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.2, 0.2, 1.0])
    glutSolidCube(1.0)

    glPopMatrix()
    return

def drawMoles(mode):
    global moles
    glPushMatrix()
    glTranslatef(-2.0,1.0,-2.0)
    for j in range(0,3):
        glPushMatrix()
        for i in range (0,3):
            moles[3*j+i].drawMole(mode)
            glTranslatef(2.0,0,0)
        glPopMatrix()
        glTranslatef(0.0,0,2.0)
    glPopMatrix()


def proscessHits(buffer):
    global moles
    global score
    if(len(buffer)>0):
        minimum,maximum,firstName = buffer[0]
        for hit_record in buffer:
            min_depth, max_depth, names = hit_record
            
            if(min_depth <= minimum):
                closest = names
        if(closest[0] < 9):
            if(moles[closest[0]].moleStatus == 'MOLE_UP'):
                score = score+1
                moles[closest[0]].moleDown(0)


def setUpView():
   #this code initializes the viewing transform
   glLoadIdentity()
   #moves viewer along coordinate axes
   gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
   #move the view back some relative to viewer[] position
   glTranslatef(0.0,0.0, 0.0);
   # rotates view
   glRotatef(0, 1.0, 0.0, 0.0);
   glRotatef(0, 0.0, 1.0, 0.0);
   glRotatef(0, 0.0, 0.0, 1.0);
   return

def setUpModelTransform():
    #Rotates models
    glRotatef(theta[0],1.0,0.0,0.0)
    glRotatef(theta[1],0.0,1.0,0.0)
    glRotatef(theta[2],0.0,0.0,1.0)

def setUpLight():
    #set up the light sources for the scene
    # a directional light source from directly behind
    lightDir = [0.0, 0.0, 5.0, 0.0];
    diffuseComp = [1.0, 1.0, 1.0, 1.0];

    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);

    glLightfv(GL_LIGHT0, GL_POSITION, lightDir);
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseComp);
    return;


##########################
#Begin Callback Functions#
##########################
def mouseCallback(button, state, x, y): 
    #If the user clicks the left button
    if((button==GLUT_LEFT_BUTTON) and (state == GLUT_DOWN)):
        SIZE = 20 #The size of the selection buffer
        viewport = glGetIntegerv(GL_VIEWPORT)

        glSelectBuffer(SIZE)
        glRenderMode(GL_SELECT)

        glPushName(0)
        glPushMatrix()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #This is the only transform difference in the hierarchy
        gluPickMatrix(x, viewport[3] - y, 5.0, 5.0, viewport)
        w = viewport[2]
        h = viewport[3]
        setUpProjection(w,h)

        #The rest is the same as display(), except
        # the mode flag is GL_SELECT
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        setUpView()
        setUpModelTransform()

        glMultMatrixf(objectXform)
        drawObjs(GL_SELECT)
        glPopMatrix()

        glFlush()

        hits = glRenderMode(GL_RENDER)
        proscessHits(hits)

        #This should re-render everything again for display
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        setUpProjection(w,h)

    display()

def keyCallback(key,x,y):
    global theta
    global thetaIncr
    global moleTime
   
    if(key == 'w'):
        theta[0] = normalizeAngle(theta[0]+thetaIncr)
    elif(key == 's'):
        theta[0] = normalizeAngle(theta[0]-thetaIncr)
    elif(key == 'a'):
        theta[1] = normalizeAngle(theta[1]+thetaIncr)
    elif(key == 'd'):
        theta[1] = normalizeAngle(theta[1]-thetaIncr)

    if((key == '+') or (key == '=')):
        moleTime += 10
    elif((key == '-') or (key == '_')):
        moleTime -= 10


    display()
        

def normalizeAngle(degrees):
    if(degrees > 360):
        degrees -= 360.0
    return degrees


def reshapeCallback(w,h):
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    setUpProjection(w, h);
    
def setUpProjection(w,h):
    #This code initalizes the projection transform
    glViewport(9,9,w,h)

    if (w < h):
        glFrustum(-2.0, 2.0, -2.0*(h/w), 2.0*(h/w), 2.0, 200.0)
    else:
        glFrustum(-2.0, 2.0, -2.0*(w/h), 2.0*(w/h), 2.0, 200.0)

    glMatrixMode(GL_MODELVIEW)

if __name__ == "__main__":
     main()
