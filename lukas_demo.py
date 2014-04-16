
from lukas_graphics3d import *
import math
import random
import time
import threading

makeGraphicsWindow(1024, 768, True)

print getOpenGLVersion()
setProjection(45, 5, 3050)

RES_DISTANCE = 2000 #1000
LOW_RES_COUNTER = 2
#17,33,65
PIECE_SIZE = 33#65#65
GRID_SPACING = 1#1#1 #30
DRAW_GRID_SPACING = 25#30#30#30

PASSES = 8#8#8#7
total = 2

for index in range(PASSES):
    total = total+(total-1)

LAND_SIZE = (total-1)*(GRID_SPACING)

REDUCTION_VALUE = 0.45 #0.5
RANGE = 1500#2000#600#2000#4000#1000#6000#1000#600#35#21 #15

def calculate_coordinates():
    current_passes = 0
    x= z = (LAND_SIZE)/2 #.0
    coordinates={(-x,z):0,(x,z):0,(x,-z):0,(-x,-z):0,}
    squares = [((-x,z),(x,z),(x,-z),(-x,-z))]
    daimonds = []
    while current_passes < PASSES:
        current_passes = current_passes + 1
        new_squares = []
        daimonds = []
        for (point1,point2,point3,point4) in squares:
            #1 2
            #4 3
            #find center
            max_X = max(point1[0],point3[0])
            min_X = min(point1[0],point3[0])
            max_Z = max(point1[1],point3[1])
            min_Z = min(point1[1],point3[1])
            X_difference = max_X-min_X
            Z_difference = max_Z-min_Z
            square_midpoint = (min_X+(X_difference/2),min_Z+(Z_difference/2))
            #print "square midpoint: ",square_midpoint
            #print "square midpoint coordinate: ",square_midpoint
            random_alteration = ((random.random()*2)-1)*RANGE*(REDUCTION_VALUE**current_passes)
            center_height = random_alteration+calculate_average([(point1[0],coordinates[point1],point1[1]),
                                               (point2[0],coordinates[point2],point2[1]),
                                               (point3[0],coordinates[point3],point3[1]),
                                               (point4[0],coordinates[point4],point4[1])])
            coordinates[square_midpoint] = center_height
            #find and append diamonds
            daimond_opposite_point = (point1[0]-(square_midpoint[0]-point1[0]),square_midpoint[1])
            daimond1 = (daimond_opposite_point,point1,square_midpoint,point4)
            daimond_opposite_point = (square_midpoint[0],point2[1]-(square_midpoint[1]-point1[1]))
            daimond2 = (point1,daimond_opposite_point,point2,square_midpoint)
            daimond_opposite_point = (point2[0]-(square_midpoint[0]-point2[0]),square_midpoint[1])
            daimond3 = (square_midpoint,point2,daimond_opposite_point,point3)
            daimond_opposite_point = (square_midpoint[0],point3[1]-(square_midpoint[1]-point4[1]))
            daimond4 = (point4,square_midpoint,point3,daimond_opposite_point)
            daimonds.extend([daimond1,daimond2,daimond3,daimond4])
            #find new squares
            pn1 = point1 #check
            pn2 = (square_midpoint[0],point1[1]) #check
            pn3 = square_midpoint #check
            pn4 = (point1[0],square_midpoint[1]) #check
            new_squares.append((pn1,pn2,pn3,pn4))
            pn5 = pn2 #check
            pn6 = point2 #check
            pn7 = (point2[0],square_midpoint[1]) #check
            pn8 = square_midpoint
            new_squares.append((pn5,pn6,pn7,pn8))
            pn9 = square_midpoint
            pn10 = pn7
            pn11 = point3
            pn12 = (square_midpoint[0],point4[1])
            new_squares.append((pn9,pn10,pn11,pn12))
            pn13 = pn4
            pn14 = square_midpoint
            pn15 = (square_midpoint[0],point4[1])
            pn16 = point4
            new_squares.append((pn13,pn14,pn15,pn16))
            
        squares = new_squares
        
        for (point1,point2,point3,point4) in daimonds:
            # 2
            #1 3
            # 4
            daimond_midpoint = (point1[0] + ((point3[0]-point1[0])/2), point4[1]+((point2[1]-point4[1])/2))
            #print daimond_midpoint
            average_list = []
            average = 0

            limit = LAND_SIZE/2
            if -limit<= point1[0] <=limit:
                if -limit<= point1[1] <=limit:

            #if point1 in coordinates:
                    average_list.append(point1)
            if point2 in coordinates:
                average_list.append(point2)
            if point3 in coordinates:
                average_list.append(point3)
            if point4 in coordinates:
                average_list.append(point4)
            for point in average_list:
                average = average+coordinates[point]
            average = average/len(average_list)
            random_alteration = ((random.random()*2)-1)*RANGE*(REDUCTION_VALUE**current_passes)
            coordinates[daimond_midpoint] = average+random_alteration
    print "==========HEIGHTS LOADED=========="
    coordinate_keys = sorted(coordinates.keys(), key=lambda position: position[1])
    #coordinate_keys = coordinates.keys()
    Zrows = [coordinate_keys[0][1]]
    
    terrain3D_heights = []
    for key in coordinate_keys:
        if key[1] not in Zrows:
            Zrows.append(key[1])

    row = []
    row_keys = []
    for Z in Zrows:
        for key in coordinate_keys:
            if key[1] == Z:
                row_keys.append(key)
        row_keys = sorted(row_keys, key=lambda XZ: XZ[0], reverse=True)
        for key in row_keys:
            row.append(coordinates[key])
        terrain3D_heights.append(row)
        row_keys = []
        row = []

    return coordinates,terrain3D_heights

def calculate_average(list_of_points):
    #print list_of_points
    limit = LAND_SIZE/2
    average_list = []
    for point in list_of_points:
        if -limit<= point[0] <=limit:
            if -limit<= point[2] <=limit:
                average_list.append(point)
    average = 0
    for point in average_list:
        average = average+point[1]

    #print average_list
    if len(average_list) == 0:
        average = 0
    else:
        average = average/len(average_list)
    return average


def myKeyPressedFunction(world, key):
    if key == pygame.K_SPACE:
        #world.mode = world.mode * -1
        #world.terrain.delete()
        initialize(world)
    if key == pygame.K_p:
        world.movement_speed = 0
    if key == pygame.K_w:
        if world.wireframe == False:
            setWireFrame(True)
            world.wireframe = True
        elif world.wireframe == True:
            setWireFrame(False)
            world.wireframe = False

class terrain_piece:
    def __init__(self,low_res_coordinate_heights,grid_spacing):
        self.has_high_res_model = False
        self.high_res_model = None
        self.low_res_model = Terrain3D(low_res_coordinate_heights,grid_spacing,texture="ground texture night.png",textureRepeat=16)

    def load_high_res(self,coordinate_heights):
        self.high_res_model = Terrain3D(coordinate_heights,DRAW_GRID_SPACING,texture="ground texture night.png",textureRepeat=16)
        self.has_high_res_model = True

def load_high_res_terrain(world):
    #load high-resolution terrain pieces
    print "==========LOADING TERRAIN RUNNING:=========="
    for piece in world.terrain_pieces:
        #print "loading high-res for: ",piece
        world.terrains[piece].load_high_res(world.terrain_pieces[piece])
    print "==========LOADING TERRAIN DONE:=========="
    
#####################################################################################################
#####################################################################################################
#####################################################################################################
def startWorld(world):
    #enableInterleavedArrays(False)
    #makeFog(0.0010, (1.0,1.0,1.0), 1)#density, color, type day-time fog
    makeFog(0.0005, (0.0,0.0,0.0), 1)#density, color, type night-time fog
    #setAmbientLight(0.3) #night
    #setAmbientLight(1.0) #day
    world.wireframe = False
    onKeyPress(myKeyPressedFunction)
    world.current_state = "loading"
    world.loading = 0

    world.skydome = Sphere3D(3000, 8, texture="skydome night.jpg")
    
    #the angles you are facing
    world.angleX = 0 #up - down
    world.angleY = 0 #left - right
    world.angleZ = 0 # forward - backward

    #this is your position
    world.positionX = 0
    world.positionY = 0
    world.positionZ = 0

    
    world.mode = 1
    world.movement_speed = 0.1
    world.rotate_speed = 0.5
    

    #if the camera has rotated or not
    world.camera_rotate = False

    #if the camera is moved or not
    world.move_camera = [0, 0, 0]
    
    
    
    #creates the 2d canvas to draw 2d things
    world.loading_canvas = Canvas2D(500,100,1.0)
    world.controls_target = Canvas2D(20,20,0.7)
    drawCircle2D(world.controls_target, 10,10,10,"black",1)

    world.controls_speed = Canvas2D(50,70,0.7)
    #drawRectangle2D(world.controls_speed, 0,0,10,50,"red",1)

    initialize(world)
#####################################################################################################
#####################################################################################################
#####################################################################################################

def initialize(world):

    startTime = time.clock()
    (coordinates,coordinate_heights) = calculate_coordinates()
    endTime = time.clock()
    print "time taken :"+str(endTime-startTime)
    
    #print "length of coordinate_heights",len(coordinate_heights)
    num_squares_side = (((len(coordinate_heights)-PIECE_SIZE)/(PIECE_SIZE-1))+1)
    #print "number of side pieces: ",num_squares_side

    terrain_piece_coordinates = {}
    world.terrain_pieces = {}
    for Xindex in range(num_squares_side):
        for Zindex in range(num_squares_side):
            terrain_piece_coordinates[(Xindex,Zindex)] = []
            world.terrain_pieces[(Xindex,Zindex)] = []

        #piece arrangement
    #(0,0)   (1,0)   (2,0)
    #(0,1)   (1,1)   (2,1)
    #(0,2)   (1,2)   (2,2)    
    
    for (X,Z) in terrain_piece_coordinates:
        spacing = (PIECE_SIZE-1)*GRID_SPACING
        startX = X*spacing
        endX =  (X+1)*spacing
        startZ = Z*spacing
        endZ = (Z+1)*spacing
        Xcount = startX
        while Xcount <= endX:
            Zcount = startZ
            while Zcount <= endZ:
                terrain_piece_coordinates[X,Z].append((Xcount,Zcount))
                Zcount = Zcount+1
            Xcount = Xcount+1

    starting_coordinateX = -((LAND_SIZE-1)/2)
    starting_coordinateZ = (LAND_SIZE-1)/2
    for piece in terrain_piece_coordinates:
        coordinate_keys = sorted(terrain_piece_coordinates[piece], key=lambda position: position[1])
        piece_row = []
        rowZ = coordinate_keys[0][1]
        for (x,z) in coordinate_keys:
            if z != rowZ:
                world.terrain_pieces[piece].append(piece_row)
                piece_row = []
                rowZ = z
            piece_row.append(coordinates[starting_coordinateX+((x-1)*GRID_SPACING),starting_coordinateZ-((z-1)*GRID_SPACING)])
        world.terrain_pieces[piece].append(piece_row)

    #############################
    world.terrains = {}
    for piece in world.terrain_pieces:
        #world.terrains[piece] = [None,None]
        low_res_coordinate_heights = []
        row_counter = LOW_RES_COUNTER
        
        for height_row in world.terrain_pieces[piece]:
            row = []
            if row_counter == LOW_RES_COUNTER:
                point_counter = LOW_RES_COUNTER
                for point in height_row:
                    if point_counter == LOW_RES_COUNTER:
                        row.append(point)
                    point_counter = point_counter-1
                    if point_counter == 0:
                        point_counter = LOW_RES_COUNTER
                        
            row_counter = row_counter-1
            if row_counter == 0:
                row_counter = LOW_RES_COUNTER
            if row != []:
                low_res_coordinate_heights.append(row)
        world.terrains[piece] = terrain_piece(low_res_coordinate_heights,2*DRAW_GRID_SPACING)

############################################################
##        ##MATCH SEAMS TO LOW RESOLUTION VERSION## - DOES NOT SEEM TO WORK: possibly floating point offset
##        counter = LOW_RES_COUNTER
##        for row_index in range(len(world.terrain_pieces[piece])):
##            if counter == 1:
##                average1 = [0,0]
##                if 0 <= row_index-1 <= PIECE_SIZE:
##                    average1[0] = average1[0]+world.terrain_pieces[piece][row_index-1][0]
##                    average1[1] = average1[1]+1
##                if 0 <= row_index+1 <= PIECE_SIZE:
##                    average1[0] = average1[0]+world.terrain_pieces[piece][row_index+1][0]
##                    average1[1] = average1[1]+1
##                world.terrain_pieces[piece][row_index][0] = average1[0]/average1[1]
##                average2 = [0,0]
##                if 0 <= row_index-1 <= PIECE_SIZE:
##                    average2[0] = average2[0]+world.terrain_pieces[piece][row_index-1][0]
##                    average2[1] = average2[1]+1
##                if 0 <= row_index+1 <= PIECE_SIZE:
##                    average2[0] = average2[0]+world.terrain_pieces[piece][row_index+1][0]
##                    average2[1] = average2[1]+1
##                world.terrain_pieces[piece][row_index][0] = average2[0]/average2[1]
##                counter = LOW_RES_COUNTER
##            else:
##                counter = counter-1
##
##        counter = LOW_RES_COUNTER
##        for row_index in (0,-1):
##            counter = LOW_RES_COUNTER
##            for point_index in range(len(world.terrain_pieces[piece][row_index])):
##                if counter == 1:
##                    average = [0,0]
##                    if 0 <= point_index-1 <= PIECE_SIZE:
##                        average[0] = average[0]+world.terrain_pieces[piece][row_index][point_index-1]
##                        average[1] = average[1]+1
##                    if 0 <= point_index+1 <= PIECE_SIZE:
##                        average[0] = average[0]+world.terrain_pieces[piece][row_index+1][point_index+1]
##                        average[1] = average[1]+1
##                    world.terrain_pieces[piece][row_index][point_index] = average[0]/average[1]
##                else:
##                    counter = counter+1
##                    
##        

    #=======================THREAD=======================
    #thread = threading.Thread(target=load_high_res_terrain,args=(world,))
    #thread.start()
    load_high_res_terrain(world)

    world.current_state = "game"
#####################################################################################################
#####################################################################################################
#####################################################################################################

def updateWorld(world):
    if world.current_state == "game":
        Xrotate = Yrotate = Zrotate = 0
        if keyPressedNow(pygame.K_UP):
            Yrotate = 1
        if keyPressedNow(pygame.K_DOWN):
            Yrotate = -1
        if keyPressedNow(pygame.K_RIGHT):
            Xrotate = -1
        if keyPressedNow(pygame.K_LEFT):
            Xrotate = 1

        if keyPressedNow(pygame.K_PAGEUP):
            world.movement_speed = world.movement_speed + 0.01
        if keyPressedNow(pygame.K_PAGEDOWN):
            world.movement_speed = world.movement_speed - 0.01

        moveCameraForward(world.movement_speed)
        adjustCameraRotation(world.rotate_speed*Xrotate, world.rotate_speed*Yrotate, world.rotate_speed*Zrotate)

        clearCanvas2D(world.controls_speed)
        drawString2D(world.controls_speed, world.movement_speed, 0, 10,color="black")
        fps = getActualFrameRate()
        drawString2D(world.controls_speed, fps, 0, 40,color="black")

def rotate_camera(X, Y, Z):
    X_rotate = (math.cos(Y)*math.cos(Z)) + ((math.cos(X)*math.sin(Z))) + (math.sin(X)*math.sin(Y)*math.cos(Z)) + ((math.sin(X)*math.sin(Z))-(math.cos(X)*math.sin(Y)*math.cos(Z)))
    Y_rotate = 0
    Z_rotate = 0
    return [X_rotate, Y_rotate, Z_rotate]


def checkResolution(world):
    pass


def drawWorld(world):
    if world.current_state == "game":
        (CX,CY,CZ) = getCameraPosition()
        draw3D(world.skydome, CX, CY-500, CZ)
        if world.mode == 1:
            for (keyX,keyZ) in world.terrains:
                #print world.terrains[keyX,keyZ].low_res_model
                starting_coordinateX = -((LAND_SIZE-1)/2)
                starting_coordinateZ = (LAND_SIZE-1)/2
                piece_width = (PIECE_SIZE-1)*DRAW_GRID_SPACING
                localX = (piece_width/2) + (piece_width*keyX)
                localZ = (piece_width/2) + (piece_width*keyZ)
                X = starting_coordinateX+localX
                Z = starting_coordinateZ-localZ
        
                Xdifference = CX-X
                Zdifference = CZ-Z
                distance = math.sqrt((Xdifference**2)+(Zdifference**2))
                if world.terrains[keyX,keyZ].has_high_res_model == True and distance <=RES_DISTANCE:
                    draw3D(world.terrains[keyX,keyZ].high_res_model, X, 0, Z, 0,90,0)
                
                elif world.terrains[keyX,keyZ].has_high_res_model == False or RES_DISTANCE <= distance <= (RES_DISTANCE+2000):
                    draw3D(world.terrains[keyX,keyZ].low_res_model, X, 0, Z, 0,90,0)
        draw2D(world.controls_target,512,384)
        draw2D(world.controls_speed, 50, 50)
    
    
 

displayFPS(2)

runGraphics(startWorld, updateWorld, drawWorld) 
