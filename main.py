from graphics3d import *
from helpers import *

from tree import *
import random
import math

makeGraphicsWindow(800, 600)

# constants
PEAK_HEIGHT = 6
HEIGHT_DROP = 0.5
MOUNTAIN_LAYERS = 10
SCALE = 5
HALF_DIMENSION = SCALE*DIMENSION

currentLayer = MOUNTAIN_LAYERS # for developer use

def startWorld(world):
	setCameraPosition(20,15,0)
	setCameraRotation(180,0,0)

	world.lionX = 20
	world.leopardX = 15
	world.sheWolfX = 10

	world.lionZ = 45
	world.leopardZ = 45
	world.sheWolfZ = 45

	world.drawVirgil = False
	world.virgilX = 0
	world.virgilY = 0
	world.virgilZ = 0

	world.thetaLion = 0
	world.thetaLeopard = 0
	world.thetaSheWolf = 0
	world.thetaVirgil = 0

	world.lion = Rect3D(2, 2, texture = "img/lion.jpg")
	world.leopard = Rect3D(2, 2, texture = "img/leopard.png")
	world.sheWolf = Rect3D(2, 2, texture = "img/sheWolf.psd")
	world.virgil = Rect3D(2, 2, texture = "img/virgil.psd")

	world.trees = []
	world.trunk = Cylinder3D(5, .75, slices = 6, wedges = 3, texture = "img/bark.jpg")#height, radius
	world.branches = Cone3D(4, 2.5, slices = 6, wedges = 3, texture = "img/branch.jpg", textureTiles = True)#height, radius

	# setClipRange(1, 1000)

	# gate
	world.gate_pole_1 = Cylinder3D(5,0.5,texture="img/stone.jpg")
	world.gate_pole_2 = Cylinder3D(5,0.5,texture="img/stone.jpg")
	world.gate_top = Box3D(5, texture="img/stone.jpg")
	world.gate_board = Box3D(3, texture="img/sign.jpg")

	# 2D array of 0's
	world.height_map = initialHeights 
	# return 2d array of heights on terrain
	world.height_map = initStructures(world, initialHeights)			

	world.terrain = Terrain3D(world.height_map, texture="img/ground texture night.png", textureRepeat=10)

# generate heights 2d array
def initStructures(world, heights):
	gridLen = gridWidth = len( heights )

	for listNum in range( gridLen ):

		for index in range( gridWidth ):

			currentPos = (listNum,index)

			# trees
			isTreeArea = isBoundedBy( currentPos,(0,0),(18,32) ) or isBoundedBy( currentPos,(25,0),(32,32) ) or isBoundedBy( currentPos, (32,58),(64,64) ) or isBoundedBy( currentPos,(58,32),(64,64) )
			isTreeArea = isTreeArea or isBoundedBy( currentPos, (18,0), (25,5)) or isBoundedBy(currentPos, (32,32), (53,53))

			if isTreeArea and random.uniform(0,1) <= 0.33:
				world.trees.append( Tree(listNum, heights[listNum][index], index, world.trunk, world.branches) )

			# mountain
			elif( isBoundedBy( currentPos,(15,52),(15,52) ) ):
				level_height = PEAK_HEIGHT
				heights[listNum][index] = level_height
				heights = create_mountain_ring(world, heights, (listNum,index), level_height - HEIGHT_DROP, MOUNTAIN_LAYERS)

			elif( isBoundedBy( currentPos,(41,5),(65,40) ) ):
				heights[listNum][index] = 0

			elif( isBoundedBy( currentPos,(50,50),(54,50) ) ):
				pass

	return heights

# creates ring of the mountain
def create_mountain_ring(world, heights, center_point, level_height, layer_number):
	global currentLayer
	if currentLayer > layer_number:
		currentLayer = layer_number

	level_height = level_height - HEIGHT_DROP

	if layer_number >= 0:
		for coords in getSurroundingPositions(world, center_point):
			(x,y) = coords

			if heights[x][y] < level_height:
				# set new level_height
				heights[x][y] = level_height

				heights = create_mountain_ring(world, heights, coords, level_height, layer_number-1)

	return heights

# creates ring of valley - combine with mountaint code
def create_valley_ring(world, heights, center_point, level_height, layer_number):
	global currentLayer
	if currentLayer > layer_number:
		currentLayer = layer_number

	level_height = level_height + HEIGHT_DROP

	if layer_number >= 0:
		for coords in getSurroundingPositions(world, center_point):
			(x,y) = coords

			if heights[x][y] > level_height:
				# set new level_height
				heights[x][y] = level_height

				heights = create_valley_ring(world, heights, coords, level_height, layer_number-1)

	return heights

# returns list of coordinates
def getSurroundingPositions(world, pos):
	height_map = world.height_map
	(x,y) = pos

	surrounding_positions = []
	surrounding_coords = [
		(x-1,y-1),
		(x-1,y),
		(x-1,y+1),
		(x,y-1),
		(x,y+1),
		(x+1,y-1),
		(x+1,y),
		(x+1,y+1)
	]

	# append position to list if the height exists
	for coord in surrounding_coords:
		(x1,y1) = coord

		if 0 <= x1 < len(world.height_map[0]) and 0 <= y1 < len(world.height_map):
			if height_map[x1][y1] is not None:
				surrounding_positions.append( coord )


	return surrounding_positions

def updateWorld(world):
# forward movement >
	movement_speed = 0
	
	if(keyPressedNow( pygame.K_UP )):
		movement_speed = 0.3

	if(keyPressedNow( pygame.K_DOWN )):
		movement_speed = -0.2

	moveCameraForward(movement_speed, True)
	camera_pos = (camX,camY,camZ) = getCameraPosition()

	# if camX < HALF_DIMENSION:
	# 	camX = camX+25

	# adjust the height
	new_height = current_height(world, camera_pos)# (camX+25,camY,camZ-25))

	setCameraPosition(camX,new_height,camZ)

	(heading, pitch, roll) = getCameraRotation()

	(virgilX, virgilZ) = polarToCartesian(heading - 20, 6)

	world.virgilX = camX + virgilX
	world.virgilY = camY
	world.virgilZ = camZ + virgilZ

	if (new_height > 4 and abs(heading) < 42):
		world.drawVirgil = True

	##print heading

# angled movement >
	rotation_angle = 0

	if(keyPressedNow( pygame.K_LEFT )):
		rotation_angle = 1	
	if(keyPressedNow( pygame.K_RIGHT )):
		rotation_angle = -1

	world.thetaLion = math.atan2(-1*(camX - world.lionX), -1*(camZ - world.lionZ))#math.atan2(-x, -z)
	world.thetaLeopard = math.atan2(-1*(camX - world.leopardX), -1*(camZ-world.leopardZ))
	world.thetaSheWolf = math.atan2(-1*(camX - world.sheWolfX), -1*(camZ-world.sheWolfZ))
	world.thetaVirgil = math.atan2(-1*(camX - world.virgilX), -1*(camZ-world.virgilZ))

	adjustCameraRotation(rotation_angle, 0, 0)


def current_height(world,pos):
	(x,y,z) = pos

	intX = int(round(x))
	intZ = int(round(z))

	if x-intX >= 0: # then the other corners are above it
		otherX = intX + 1
	else: # then the other corners are below it
		otherX = intX - 1

	if z-intZ >= 0: # then the other corners are above it
		otherZ = intZ + 1
	else: # then the other corners are below it
		otherZ = intZ - 1


	# x_percentage_done = abs(x-intX)
	# z_percentage_done = abs(z-intZ)
	# x_percentage_left = abs(x-otherX)
	# z_percentage_left = abs(z-otherZ)

	# corner1 = world.height_map[intX]  [intZ]
	# corner2 = world.height_map[intX]  [otherZ]
	# corner3 = world.height_map[otherX][intZ]
	# corner4 = world.height_map[otherX][otherZ]

	# x_diff_1 = corner1*x_percentage_done + corner2*x_percentage_left
	# x_diff_2 = corner3*x_percentage_done + corner4*x_percentage_left

	# interpolated_height = (x_diff_1*z_percentage_done + x_diff_2*z_percentage_left) + 2

	corner_height_coords = [(intX,intZ),(intX,otherZ),(otherX,intZ),(otherX,otherZ)]
	corner_heights = [world.height_map[x][z]+1 for (x,z) in corner_height_coords]
	avg_height = sum(corner_heights)/len(corner_heights)

	# corner_height_coords = [(intX/5,intZ/5),(intX/5,otherZ/5),(otherX/5,intZ/5),(otherX/5,otherZ/5)]

	# x_percentage_done = abs(intX - x)
	# z_percentage_done = abs(intZ - z)
	# x_percentage_left = abs(otherX - x)
	# z_percentage_left = abs(otherZ - z)

	# interpolated_heights = [
	# 	world.height_map[intX/5]  [intZ/5]   *x_percentage_left *z_percentage_left,
	# 	world.height_map[intX/5]  [otherZ/5] *x_percentage_left *z_percentage_done,
	# 	world.height_map[otherX/5][intZ/5]   *x_percentage_done *z_percentage_left,
	# 	world.height_map[otherX/5][otherZ/5] *x_percentage_done *z_percentage_done
	# ]

	# print interpolated_heights

	# interpolated_height = -5*(sum(interpolated_heights)/len(interpolated_heights))


	# corner_heights = [-5*world.height_map[x][z]+1 for (x,z) in corner_height_coords]

	# avg_height = sum(corner_heights)/len(corner_heights)


	return avg_height #interpolated_height

def drawWorld(world):
	draw3D(world.terrain,x=DIMENSION/2,y=0,z=DIMENSION/2, scale=1) #, anglex=20, angley=20)

	for tree in world.trees:
		tree.draw()

	draw3D(world.lion, world.lionX, world.height_map[world.lionX][40]+3, world.lionZ, angley = math.degrees(world.thetaLion), anglez = 0)
	draw3D(world.leopard, world.leopardX, world.height_map[world.leopardX][40]+3, world.leopardZ, angley=math.degrees(world.thetaLeopard), anglez=0)
	draw3D(world.sheWolf, world.sheWolfX, world.height_map[world.sheWolfX][40]+3, world.sheWolfZ, angley=math.degrees(world.thetaSheWolf), anglez=0)
	if world.drawVirgil:
		draw3D(world.virgil, world.virgilX, world.virgilY, world.virgilZ, angley = math.degrees(world.thetaVirgil))




	# gate
	draw3D(world.gate_pole_1, 58.5, 0, 30, anglex=180)
	draw3D(world.gate_pole_2, 53.5, 0, 30, anglex=180)
	draw3D(world.gate_top, 56,3,30)
	draw3D(world.gate_board, 56,3,31)

runGraphics(startWorld, updateWorld, drawWorld)
	

