# import Leap, sys, helper
# from lukas_graphics3d import *


from graphics3d import *

makeGraphicsWindow(800, 600)

def startWorld(world):
    world.earth = Sphere3D(3, 36, texture="earth.jpg")
    world.angle = 0.0

def updateWorld(world):
    world.angle += 0.5

def drawWorld(world):
    draw3D(world.earth, 0, 0, -10, 0, world.angle, 0)

runGraphics(startWorld, updateWorld, drawWorld)

# #########################################################
# #####################  Visualizer  ######################
# #########################################################

# # run once, intializes it
# def init(world):


# # updates all world necessary to visualizer
# def updateData(world):


# # draws the worldrmation
# # reads world changed in prior function
# def draw(world):
# 	# redraw the keyboard


# #########################################################
# #####################   Listener   ######################
# #########################################################

# class Listener(Leap.Listener):
# 	# when is this called?
# 	def on_init(self, controller):
# 		print "Init LeapMotion program"

# 	# when LeapMotion connects to program
# 	def on_connect(self, controller):
# 		print "Connected!"

# 	# on disconnect
# 	def on_disconnect(self, controller):
# 		print "Disconnected!"

# 	# on LeapMotion exit
# 	def on_exit(self, controller):
# 		print "Exited!"

# 	# each frame
# 	def on_frame(self, controller):
# 		# returns most recent frame
# 		frame = controller.frame()

# 		# animation loop information
# 		getWorld().frame = frame


# #runs everything
# def main():
# 	#create listener and controller
# 	listener = Listener();
# 	controller = Leap.Controller();

# 	#add listener to this LeapMotion device
# 	controller.add_listener(listener)	

# 	# make graphics world
# 	(width, height) = getScreenSize()
# 	makeGraphicsWindow(width, height, True)

# 	# start graphics loop
# 	runGraphics(initKeyboardVisualizer, updateKeyboardVisualizer, drawKeyboardVisualizer)

# 	# Remove the sample listener when done
# 	controller.remove_listener(listener)

# #initial call
# main()
