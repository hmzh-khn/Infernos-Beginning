from graphics3d import *

makeGraphicsWindow(800, 600)

def startWorld(world):
    world.earth = Sphere3D(3, 36, texture="img/earth.jpg")
    world.angle = 0.0
    world.cylinder = Cylinder3D(3,2, colors=["white","red"], wedges=100)

def updateWorld(world):
    world.angle += 0.5

def drawWorld(world):
    draw3D(world.cylinder, z=-15, anglex=world.angle) # x, y, z, rotation angles
    # draw3D(world.earth, 0, 0, -10, 0, world.angle, 0)




runGraphics(startWorld, updateWorld, drawWorld)


def draw_tree():
	print 'lol'
