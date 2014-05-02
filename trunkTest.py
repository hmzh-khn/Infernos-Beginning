# Dante's journey - Joseph Hungate + Hamzah Khan
# Contributions from Lukas Stracovsky
# Graphics library made by Andrew Merrill

from graphics3d import *

import math
from random import randint
import time

makeGraphicsWindow(1024, 768)


class Tree:

    def __init__(self, x, y, z, trunk, branches):
        self.trunk = trunk
        self.branches = branches
        self.x = x
        self.y = y
        self.z = z

    def draw(self):
        draw3D(self.trunk, self.x, self.y + self.trunk.height/2, self.z)
        draw3D(self.branches, self.x, self.y + self.trunk.height + self.branches.height/2, self.z, anglex = 180)
       

    







def startWorld(world):

    world.lionX = 0
    world.thetaLion = 0
    
    world.leopardX = 10
    world.sheWolfX = 20

    world.lion = Rect3D(5, 5, texture = "lion.jpg")

    world.leopard = Rect3D(5, 5, texture = "leopard.png")
    
    world.sheWolf = Rect3D(5, 5, texture = "sheWolf.psd")


    world.trunk = Cylinder3D(5, .75, slices = 6, wedges = 3, texture = "bark.jpg")#height, radius

    world.branches = Cone3D(4, 2.5, slices = 6, wedges = 3, texture = "branch.jpg", textureTiles = True)#height, radius

    setClipRange(1, 1000)

    world.trees = []


    #world.trees.append(Tree(0, 0, -20))

    

    for x in range(20):
        xFactor = randint(5, 10)
        world.trees.append(Tree(xFactor*x, 0, -20, world.trunk, world.branches))
        for z in range(20):
            world.trees.append(Tree(randint(5, 10)*x, 0, randint(5, 10)*z, world.trunk, world.branches))



def updateWorld(world):

    if isKeyPressed(pygame.K_UP):
            moveCameraForward(4)
    if isKeyPressed(pygame.K_a):
            strafeCameraLeft(4)
    if isKeyPressed(pygame.K_d):
            strafeCameraRight(4)
    if isKeyPressed(pygame.K_RIGHT):
        adjustCameraRotation(-3, 0, 0)
    if isKeyPressed(pygame.K_r):
            startWorld(world)
    if isKeyPressed(pygame.K_LEFT):
            adjustCameraRotation(3, 0, 0)
    if isKeyPressed(pygame.K_i):
            adjustCameraRotation(0, 3, 0)
    if isKeyPressed(pygame.K_k):
            adjustCameraRotation(0, -3, 0)
    if isKeyPressed(pygame.K_DOWN):
            moveCameraBackward(2)
    (cameraX, cameraY, cameraZ) = getCameraPosition()
    
    world.thetaLion = math.atan2(-1*(cameraX - world.lionX), -1*cameraZ)#math.atan2(-x, -z)
    world.thetaLeopard = math.atan2(-1*(cameraX - world.leopardX), -1*cameraZ)
    world.thetaSheWolf = math.atan2(-1*(cameraX - world.sheWolfX), -1*cameraZ)


    #print world.thetaLion


def drawWorld(world):

##    draw3D(world.trunk,0, 0, -20)
##
##    draw3D(world.branches, 0, 4, -20, anglex = 180)

    for tree in world.trees:
        tree.draw()

    draw3D(world.lion, world.lionX, 20, 0, angley = math.degrees(world.thetaLion), anglez = 0)
    draw3D(world.leopard, world.leopardX, 20, 0, angley = math.degrees(world.thetaLeopard), anglez = 0)
    draw3D(world.sheWolf, world.sheWolfX, 20, 0, angley = math.degrees(world.thetaSheWolf), anglez = 0)

runGraphics(startWorld, updateWorld, drawWorld)
