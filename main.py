from graphics3d import *
from helpers import *

makeGraphicsWindow(800, 600)

# constants
PEAK_HEIGHT = 6
HEIGHT_DROP = 0.5
MOUNTAIN_LAYERS = 10

currentLayer = MOUNTAIN_LAYERS # for developer use

def startWorld(world):
	setCameraPosition(0,10,0)

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
			if( isBoundedBy( currentPos,(3,5),(6,8) )):
				heights[listNum][index] = 3

			# mountain
			elif( isBoundedBy( currentPos,(10,20),(10,20) ) ):
				level_height = PEAK_HEIGHT

				heights[listNum][index] = level_height

				heights = create_mountain_ring(world, heights, (listNum,index), level_height - HEIGHT_DROP, MOUNTAIN_LAYERS)




			# valley
			elif( isBoundedBy( currentPos,(41,5),(65,40) ) ):
				heights[listNum][index] = 0

			# plain with gates and Charon at the end
			elif( isBoundedBy( currentPos,(50,50),(54,50) ) ):
				level_height = -PEAK_HEIGHT

				heights[listNum][index] = level_height

				heights = create_valley_ring(world, heights, (listNum,index), level_height + HEIGHT_DROP, MOUNTAIN_LAYERS)

	return heights

# creates ring of the mountain
def create_mountain_ring(world, heights, center_point, level_height, layer_number):
	global currentLayer
	if currentLayer > layer_number:
		currentLayer = layer_number
		print currentLayer

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
		print currentLayer

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
	
	camera_pos = getCameraPosition()


# forward movement >
	movement_speed = 0
	
	if(keyPressedNow( pygame.K_UP )):
		movement_speed = 1
	if(keyPressedNow( pygame.K_DOWN )):
		movement_speed = -1

	moveCameraForward(movement_speed, True)

# angled movement >
	rotation_angle = 0

	if(keyPressedNow( pygame.K_LEFT )):
		rotation_angle = 1	
	if(keyPressedNow( pygame.K_RIGHT )):
		rotation_angle = -1

	adjustCameraRotation(rotation_angle, 0, 0)




def drawWorld(world):
	draw3D(world.terrain, y=1, scale=5) #, anglex=20, angley=20)

runGraphics(startWorld, updateWorld, drawWorld)
	

