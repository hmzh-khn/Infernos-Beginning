"""
This is a simple 3D interactive graphics and animation library for Python.
Author: Andrew Merrill, Catlin Gabel School
Version: 0.71 Beta (last updated May, 2011)

This code is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike license
see http://creativecommons.org/licenses/by-nc-sa/3.0/ for details

Note: You must have the Pygame and PyOpenGL libraries installed for this to work.
        You can download Pygame from http://www.pygame.org/
        You can download PyOpenGL from http://pyopengl.sourceforge.net/

This has been tested with Python 2.6.6, Pygame 1.9.1, and PyOpenGL 3.0.1.
"""

import sys, math, re, os, os.path, random, struct
import zipfile, cStringIO, xml.etree.ElementTree
import pygame

import OpenGL
OpenGL.ERROR_CHECKING = False

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.lists

class World:
    pass

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
class Angles3D:
    def __init__(self, heading, pitch, roll):
        self.heading = heading
        self.pitch = pitch
        self.roll = roll

class Viewport:
    def __init__(self, label, x, y, width, height):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cameraPosition = (0,0,0)
        self.cameraRotation = (0,0,0)
        
class GameLibInfo:
    def __init__(self):
        self.initialize()
        
    def initialize(self):
        self.version = "0.71"
        self.world = None
        self.fonts = dict()
        self.eventListeners = dict()
        self.frameRate = 60
        self.windowWidth = 0
        self.windowHeight = 0
        self.viewportWidth = 0
        self.viewportHeight = 0
        self.viewports = dict()
        self.currentViewport = None
        self.background = (0,0,0)
        self.foreground = (1,1,1)
        self.nextEventType = pygame.USEREVENT
        self.arrayHandler = OpenGL.arrays.lists.ListHandler()
        self.textureIDs = dict()
        self.FPStime = 0
        self.FPSinterval = 0
        self.FPScount = 0
        self.cameraPosition = Point3D(0,0,0)
        self.cameraAngles = Angles3D(0,0,0)
        self.keysPressedNow = dict()
        self.polygonCount = 0
        self.fieldOfView=45
        self.nearClip=0.1
        self.farClip=1000.0
        self.textureMapsEnabled = False
        self.lightingEnabled = False
        self.numLights = 0
        self.lights = []
        self.fogMode = 0
        self.numPushedMatrices = 0
        self.useNewCamera = True
        self.enableSelection = False
        self.selectColorDict = {} # key = color, value = ID
        self.selectColorIDDict = {} # key = ID, value = color
        self.selectionDrawingOn = False
        self.useInterleavedArrays = True
        self.START_MODE = 1
        self.EVENT_MODE = 2
        self.UPDATE_MODE = 3
        self.DRAW_MODE = 4
        self.currentMode = self.START_MODE
        self.joysticks = []
        self.joystickLabels = []  # list of dictionaries
        self.numJoysticks = 0
        self.joystickDeadZone = 0.05
        self.joystickLabelDefault = [["X", "Y"]]
        self.joystickLabelDefaults = {
            "Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Logitech Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Controller (Gamepad F310)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],
            "Controller (Wireless Gamepad F710)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],

            "Saitek Aviator Stick" : [["X", "Y", "LeftThrottle", "Twist", "RightThrottle"]],
            "Saitek Pro Flight Throttle Quadrant" : [["LeftThrottle", "CenterThrottle", "RightThrottle"]]
            }

        
    def initializeListeners(self):
        onKeyPress(lambda world,key: 0)
        onKeyRelease(lambda world,key: 0)
        onMousePress(lambda world,x,y,button: 0)
        onMouseRelease(lambda world,x,y,button: 0)
        onWheelForward(lambda world,x,y: 0)
        onWheelBackward(lambda world,x,y: 0)
        onMouseMotion(lambda world,x,y,dx,dy,b1,b2,b3: 0)
        onGameControllerStick(lambda world,device,axis,value: 0)
        onGameControllerDPad(lambda world,device,pad,xvalue,yvalue: 0)
        onGameControllerButtonPress(lambda world,device,button: 0)
        onGameControllerButtonRelease(lambda world,device,button: 0)

    def initializeJoysticks(self):
        self.numJoysticks = pygame.joystick.get_count()
        for id in range(self.numJoysticks):
            self.joysticks.append(pygame.joystick.Joystick(id))
            self.joystickLabels.append(dict())
            self.joysticks[id].init()
            stickname = self.joysticks[id].get_name()
            if stickname in self.joystickLabelDefaults:
                print "recognized a " + stickname
                labelList = self.joystickLabelDefaults[stickname]
            else:
                print "unknown game controller: " + stickname
                labelList = self.joystickLabelDefault
            for labels in labelList:
                gameControllerSetStickAxesNames(labels, id)
            print "    with axes:", gameControllerGetStickAxesNames()

    def loadColors(self, colorsList):
        self.colorsList = colorsList
        self.colorTable3D = dict()
        for (name, red, green, blue, hexcolor) in colorsList:
            self.colorTable3D[name] = (red/255.0, green/255.0, blue/255.0)
        self.colorTable3D['clear'] = (0,0,0,0)

    def loadKeys(self, keyList):
        self.keyList = keyList
        self.key2nameDict = dict()
        self.name2keyDict = dict()
        for (code, nameList) in keyList:
            self.key2nameDict[code] = nameList[0]
            for name in nameList:
                self.name2keyDict[name] = code
        

    def startAnimation(self):
        self.clock = pygame.time.Clock()
        self.startTime = pygame.time.get_ticks()
        self.keepRunning = True
        self.FPScount = 0
        if self.FPSinterval > 0:
            self.FPStime = pygame.time.get_ticks() + self.FPSinterval

    def maybePrintFPS(self):
        self.FPScount += 1
        if self.FPSinterval > 0:
            time = pygame.time.get_ticks()
            if time > self.FPStime + self.FPSinterval:
                print getActualFrameRate(), " (" + str(_GLI.polygonCount) + " polygons)"
                self.FPStime = time
                self.FPScount = 0

    def getTextureID(self, textureName):
        if textureName is None:
            return 0
        elif textureName in self.textureIDs:
            return self.textureIDs[textureName]
        elif isinstance(textureName, tuple):
            (data, filename) = textureName
            if filename in self.textureIDs:
                return self.textureIDs[filename]
        return loadTexture(textureName)

    def enableTextureMaps(self):
        if self.textureMapsEnabled:
            return
        self.textureMapsEnabled = True
        glEnable(GL_TEXTURE_2D)
        #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

    def handleNumPy(self):
        global numpy
        try:
            import numpy
            self.hasNumPy = True
            print "using numpy"
        except ImportError:
            self.hasNumPy = False

    def handleOldOpenGLVersions(self):
        openglVersion = glGetString(GL_VERSION)
        if openglVersion < "1.5":
            import OpenGL.GL.ARB.vertex_buffer_object as ARBVBO
            global glGenBuffers, glBindBuffer, glBufferData
            glGenBuffers = ARBVBO.glGenBuffersARB
            glBindBuffer = ARBVBO.glBindBufferARB
            glBufferData = ARBVBO.glBufferDataARB
        if openglVersion < "1.4":
            self.hasWindowPos = False
        else:
            self.hasWindowPos = True
        if openglVersion < "1.3":
            import OpenGL.GL.ARB.transpose_matrix as ARBTransposeMatrix
            global glMultTransposeMatrixf
            glMultTransposeMatrixf = ARBTransposeMatrix.glMultTransposeMatrixfARB
        if openglVersion < "1.2":
            print "Your Open GL Version ("+openglVersion+") is too old"

        
_GLI = GameLibInfo()

def makeGraphicsWindow(width, height, fullscreen=False):
    initGraphics()
    setGraphicsMode(width, height, fullscreen)
    print getOpenGLVersion()
    _GLI.handleOldOpenGLVersions()
    _GLI.handleNumPy()

def initGraphics():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    _GLI.initialize()
    _GLI.initializeListeners()
    _GLI.initializeJoysticks()
    _GLI.graphicsInited = True

def endGraphics():
    _GLI.keepRunning = False

def setGraphicsMode(width, height, fullscreen=False):
    _GLI.windowWidth = width
    _GLI.windowHeight = height
    _GLI.viewportWidth = width
    _GLI.viewportHeight = height
    flags = 0
    if fullscreen == True:
        flags = flags | pygame.FULLSCREEN
    flags = flags | pygame.OPENGL | pygame.HWSURFACE | pygame.DOUBLEBUF
    _GLI.screen = pygame.display.set_mode((width, height), flags)
    glViewport(0, 0, width, height)
    setProjection()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glShadeModel(GL_SMOOTH)
    glEnableClientState(GL_VERTEX_ARRAY)
    _GLI.textureIDs = dict()


def getScreenSize():
    initGraphics()
    info = pygame.display.Info()
    return (info.current_w, info.current_h)

def getAllScreenSizes():
    initGraphics()
    return pygame.display.list_modes()

def setProjection(fieldOfView=_GLI.fieldOfView, nearClip=_GLI.nearClip, farClip=_GLI.farClip):
    _GLI.fieldOfView = fieldOfView
    _GLI.nearClip = nearClip
    _GLI.farClip = farClip
    _applyProjection()

def setFieldOfView(fieldOfView):
    _GLI.fieldOfView = fieldOfView
    _applyProjection()

def setClipRange(nearClip=_GLI.nearClip, farClip=_GLI.farClip):
    _GLI.nearClip = nearClip
    _GLI.farClip = farClip
    _applyProjection()

def _applyProjection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = float(_GLI.viewportWidth) / float(_GLI.viewportHeight)
    gluPerspective(_GLI.fieldOfView, aspect, _GLI.nearClip, _GLI.farClip)
    glMatrixMode(GL_MODELVIEW)

def enableInterleavedArrays(isEnabled):
    _GLI.useInterleavedArrays = isEnabled

def setBackground(background):
    if isinstance(background, str):
        _GLI.background = lookupColor3D(background)
    else:
        _GLI.background = background
    glClearColor(_GLI.background[0], _GLI.background[1], _GLI.background[2], 1.0)


def getActualFrameRate():
    return _GLI.clock.get_fps()

def displayFPS(interval):
    _GLI.FPSinterval = interval*1000
    _GLI.FPStime = pygame.time.get_ticks()
    _GLI.FPScount = 0

def getWindowWidth():
    return _GLI.windowWidth

def getWindowHeight():
    return _GLI.windowHeight

def getViewportWidth():
    return _GLI.viewportWidth

def getViewportHeight():
    return _GLI.viewportHeight


def setWindowTitle(title):
    pygame.display.set_caption(str(title))

def lookupColor3D(color):
    if color in _GLI.colorTable3D:
        return _GLI.colorTable3D[color]
    else:
        return color
    
def getColorsList():
    return [color[0] for color in _GLI.colorsList]

def getOpenGLVersion():
    return "OpenGL " + glGetString(GL_VERSION) + " " + glGetString(GL_VENDOR) + " " + glGetString(GL_RENDERER) + " graphics3d " + _GLI.version



def createViewport(label, x, y, width, height):
    viewport = Viewport(label, x, y, width, height)
    _GLI.viewports[label] = viewport
    _GLI.currentViewport = viewport

def useViewportCamera(label):
    if _GLI.currentViewport != None:
        _GLI.currentViewport.cameraPosition = getCameraPosition()
        _GLI.currentViewport.cameraRotation = getCameraRotation()
    _GLI.currentViewport = _GLI.viewports[label]
    _GLI.viewportWidth = _GLI.currentViewport.width
    _GLI.viewportHeight = _GLI.currentViewport.height
    (x,y,z) = _GLI.currentViewport.cameraPosition
    (h,p,r) = _GLI.currentViewport.cameraRotation
    setCameraPosition(x,y,z)
    setCameraRotation(h,p,r)

def useViewport(label):
    useViewportCamera(label)
    x = _GLI.currentViewport.x
    y = _GLI.currentViewport.y
    width = _GLI.currentViewport.width
    height = _GLI.currentViewport.height
    setViewport(x, y, width, height)


# this should normally not be called from outside the library
#  provided for backwards compatibility
def setViewport(x, y, width, height):
    _GLI.viewportWidth = width
    _GLI.viewportHeight = height
    glViewport(x,  _GLI.windowHeight - (y+height), width, height)
    _applyProjection()
    glLoadIdentity()
    setupCamera()
    _drawLights()






def _getTextureData(texture):
    if isinstance(texture, str):
        textureImage = pygame.image.load(texture)
        textureFileName = texture
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
    elif isinstance(texture, Canvas2D):
        textureImage = texture.image
        textureData = texture.getImageData()
        textureFileName = None
    else:
        (textureFileObject, textureFileName) = texture
        if textureFileName in _GLI.textureIDs:
            return _GLI.textureIDs[textureFileName]
        textureImage = pygame.image.load(textureFileObject, textureFileName)
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
    width = textureImage.get_width()
    height = textureImage.get_height()
    return (width, height, textureFileName, textureData)
 
def loadTexture(texture, alias=None, scale=None):
    if isinstance(texture,str):
        textureImage = pygame.image.load(texture)
        if scale is not None:
            textureImage = pygame.transform.scale(textureImage, scale)
        textureFileName = texture
        textureData = pygame.image.tostring(textureImage, "RGBA", True)
        width = textureImage.get_width()
        height = textureImage.get_height()
    else:   
        (width, height, textureFileName, textureData) = _getTextureData(texture)
    _GLI.enableTextureMaps()
    textureID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    if textureFileName is not None:
        _GLI.textureIDs[textureFileName] = textureID
    if alias is not None:
        _GLI.textureIDs[alias] = textureID
    return textureID


def setTexture(model, textureName):
    model.textureID = _GLI.getTextureID(textureName)

def updateTexture(model, texture):
    (width, height, textureFileName, textureData) = _getTextureData(texture)
    textureID = model.textureID
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, width, height, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
    

def makeFog(density=0.05, color=(1,1,1), mode=1):
    glEnable(GL_FOG)
    if mode == 1:
        glFogi(GL_FOG_MODE, GL_EXP)
    if mode == 2:
        glFogi(GL_FOG_MODE, GL_EXP2)

    glFogf(GL_FOG_DENSITY, density)
    glFogfv(GL_FOG_COLOR, lookupColor3D(color))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    _GLI.fogDensity = density
    _GLI.fogMode = mode
    _GLI.fogColor = color

def removeFog():
    glDisable(GL_FOG)
    _GLI.fogMode = 0


# returns the distance at which the fraction of visible color has dropped to the given value
def getFogRange(visibility=0.005):
    if _GLI.fogMode == 0:
        return 1e100
    elif _GLI.fogMode == 1:
        return (-math.log(visibility)) / _GLI.fogDensity
    elif _GLI.fogMode == 2:
        return math.sqrt(-math.log(visibility)) / _GLI.fogDensity

def setWireFrame(wireframe, width=1):
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(width)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
 
#########################################################

def loadSound(filename, volume=1):
    sound = pygame.mixer.Sound(filename)
    if volume != 1:
        sound.set_volume(volume)
    return sound

def playSound(sound, repeat=False):
    if repeat:
        sound.play(-1)
    else:
        sound.play()

def stopSound(sound):
    sound.stop()

def loadMusic(filename, volume=1):
    pygame.mixer.music.load(filename)
    if volume != 1:
        pygame.mixer.music.set_volume(volume)

def playMusic(repeat=False):
    if repeat:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play()

def stopMusic():
    pygame.mixer.music.stop()
    
    
#########################################################

def onKeyPress(listenerFunction):
    _GLI.eventListeners["keydown"] = listenerFunction

def onKeyRelease(listenerFunction):
    _GLI.eventListeners["keyup"] = listenerFunction
    
def onMousePress(listenerFunction):
    _GLI.eventListeners["mousedown"] = listenerFunction
    
def onMouseRelease(listenerFunction):
    _GLI.eventListeners["mouseup"] = listenerFunction

def onWheelForward(listenerFunction):
    _GLI.eventListeners["wheelforward"] = listenerFunction

def onWheelBackward(listenerFunction):
    _GLI.eventListeners["wheelbackward"] = listenerFunction

def onMouseMotion(listenerFunction):
    _GLI.eventListeners["mousemotion"] = listenerFunction

def onGameControllerStick(listenerFunction):
    _GLI.eventListeners["stickmotion"] = listenerFunction
    
def onGameControllerDPad(listenerFunction):
    _GLI.eventListeners["dpadmotion"] = listenerFunction
    
def onGameControllerButtonPress(listenerFunction):
    _GLI.eventListeners["joybuttondown"] = listenerFunction
    
def onGameControllerButtonRelease(listenerFunction):
    _GLI.eventListeners["joybuttonup"] = listenerFunction

def onTimer(listenerFunction, interval):
    if _GLI.nextEventType > pygame.NUMEVENTS:
        raise ValueError, "too many timer listeners"
    _GLI.eventListeners["timer" + str(_GLI.nextEventType)] = listenerFunction
    pygame.time.set_timer(_GLI.nextEventType, interval)
    _GLI.nextEventType += 1



#########################################################

def getMousePosition():
    return pygame.mouse.get_pos()

def getMouseButton(button):
    return pygame.mouse.get_pressed()[button-1]

def hideMouse():
    pygame.mouse.set_visible(False)

def showMouse():
    pygame.mouse.set_visible(True)

def moveMouse(x, y):
    pygame.mouse.set_pos((int(x), int(y)))

def isKeyPressed(key):
    if key in _GLI.name2keyDict:
        key = _GLI.name2keyDict[key]
    return _GLI.keysPressedNow.get(key, False)

def getKeyName(key):
    if key in _GLI.key2nameDict:
        return _GLI.key2nameDict[key]
    else:
        return None


#########################################################

def numGameControllers():
    return _GLI.numJoysticks

def gameControllerNumStickAxes(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numaxes()
    else:
        return 0

def gameControllerNumDPads(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numhats()
    else:
        return 0

def gameControllerNumButtons(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numbuttons()
    else:
        return 0

def gameControllerSetDeadZone(deadzone):
    _GLI.joystickDeadZone = deadzone

def gameControllerGetStickAxesNames(device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        axes = labelDict.keys()
        axes.sort(key=lambda axis: labelDict[axis])
        return axes
    return []

def gameControllerStickAxis(axis, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        labelDict = _GLI.joystickLabels[device]
        if axis in labelDict:
            axis = labelDict[axis]
        if axis < joystick.get_numaxes():
            value = joystick.get_axis(axis)
            if abs(value) > _GLI.joystickDeadZone:
                return value
    return 0            

def gameControllerSetStickAxesNames(axesList, device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        for i in range(len(axesList)):
            labelDict[axesList[i]] = i
        
def gameControllerButton(button, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        button -= 1
        if button >= 0 and button < joystick.get_numbuttons():
            value = joystick.get_button(button)
            return (value == 1)
    return False            

def gameControllerDPadX(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dx
    return 0            

def gameControllerDPadY(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dy
    return 0

            
#########################################################
# use animate for non-interactive animations
##def animate(drawFunction, timeLimit, frameRate=_GLI.frameRate):
##    def startWorld():
##        pass
##    def timeExpired(world):
##        if getElapsedTime() > timeLimit:
##            _GLI.keepRunning = False
##        return world
##    def drawAnimationFrame(world):
##        drawFunction(getElapsedTime())
##    runGraphics(startWorld, timeExpired, drawAnimationFrame, frameRate)

# use run for interactive programs like games
def runGraphics(startFunction, updateFunction, drawFunction, frameRate=_GLI.frameRate):
    try:
        _GLI.startAnimation()
        _GLI.world = World()
        _GLI.startFunction = startFunction
        _GLI.updateFunction = updateFunction
        _GLI.drawFunction = drawFunction
        startFunction(_GLI.world)
        while _GLI.keepRunning:
            _GLI.currentMode = _GLI.EVENT_MODE
            eventlist = pygame.event.get()
            _GLI.world.guiEventList = eventlist
            for event in eventlist:
                if event.type == pygame.QUIT:
                    _GLI.keepRunning = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        _GLI.keepRunning = False
                    else:
                        _GLI.keysPressedNow[event.key] = True
                        _GLI.eventListeners["keydown"](_GLI.world, event.key)
                elif event.type == pygame.KEYUP:
                    _GLI.keysPressedNow[event.key] = False
                    _GLI.eventListeners["keyup"](_GLI.world, event.key)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        _GLI.eventListeners["mousedown"](_GLI.world, event.pos[0], event.pos[1], event.button)
                    elif event.button == 4:
                        _GLI.eventListeners["wheelforward"](_GLI.world, event.pos[0], event.pos[1])
                    elif event.button == 5:
                        _GLI.eventListeners["wheelbackward"](_GLI.world, event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button <= 3:
                        _GLI.eventListeners["mouseup"](_GLI.world, event.pos[0], event.pos[1], event.button)
                elif event.type == pygame.MOUSEMOTION:
                    if event.rel[0] != 0 or event.rel[1] != 0:
                        button1 = (event.buttons[0] == 1)
                        button2 = (event.buttons[1] == 1)
                        button3 = (event.buttons[2] == 1)
                        _GLI.eventListeners["mousemotion"](_GLI.world, event.pos[0],event.pos[1],event.rel[0],event.rel[1],button1,button2,button3)

                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) < _GLI.joystickDeadZone:
                        joystickValue = 0
                    else:
                        joystickValue = event.value
                    _GLI.eventListeners["stickmotion"](_GLI.world, event.joy, event.axis, joystickValue)
                elif event.type == pygame.JOYHATMOTION:
                    _GLI.eventListeners["dpadmotion"](_GLI.world, event.joy, event.hat, event.value[0], event.value[1])
                elif event.type == pygame.JOYBUTTONUP:
                    _GLI.eventListeners["joybuttonup"](_GLI.world, event.joy, event.button+1)
                elif event.type == pygame.JOYBUTTONDOWN:
                    _GLI.eventListeners["joybuttondown"](_GLI.world, event.joy, event.button+1)

                elif event.type >= pygame.USEREVENT:   # timer event
                    _GLI.eventListeners["timer"+str(event.type)](_GLI.world)
            _GLI.currentMode = _GLI.UPDATE_MODE
            updateFunction(_GLI.world)
            _render()
            pygame.display.flip()
            _GLI.maybePrintFPS()
            _GLI.clock.tick(frameRate)
    finally:
        pygame.quit()


def _render():
    _GLI.currentMode = _GLI.DRAW_MODE
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    _drawLights()
    _GLI.polygonCount = 0
    _GLI.numPushedMatrices = 0
    _GLI.drawFunction(_GLI.world)
    while _GLI.numPushedMatrices > 0:
        glPopMatrix()
        _GLI.numPushedMatrices -= 1
    


def getWorld():
    return _GLI.world

def getElapsedTime():
    return pygame.time.get_ticks() - _GLI.startTime

def resetTime():
    _GLI.startTime = pygame.time.get_ticks()

#########################################################

def getPixelColor(x,y):
    data = glReadPixels(x, _GLI.windowHeight - y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
    (r, g, b) = struct.unpack("BBB", data)
    return (r, g, b)

def getPixelDistance(x,y):
    [[depth]] = glReadPixels(x, _GLI.windowHeight - y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
    depth = (depth - 0.5) * 2.0
    far = _GLI.farClip
    near = _GLI.nearClip
    z = (-2.0 * far * near) / (depth * (far-near) - (far+near))
    return z

#########################################################

def useNewCamera(newCamera):
    _GLI.useNewCamera = newCamera

def setupCamera():
    if _GLI.useNewCamera:
        glRotate(-_GLI.cameraAngles.roll, 0, 0, 1)
        glRotate(-_GLI.cameraAngles.pitch, 1, 0, 0)
        glRotate(-_GLI.cameraAngles.heading, 0, 1, 0)
        glTranslate(-_GLI.cameraPosition.x, -_GLI.cameraPosition.y, -_GLI.cameraPosition.z)
    else:
        glRotate(-_GLI.cameraAngles.heading, 1, 0, 0)
        glRotate(-_GLI.cameraAngles.pitch, 0, 1, 0)
        glRotate(-_GLI.cameraAngles.roll, 0, 0, 1)
        glTranslate(-_GLI.cameraPosition.x, -_GLI.cameraPosition.y, -_GLI.cameraPosition.z)

def getCameraPosition():
    return (_GLI.cameraPosition.x, _GLI.cameraPosition.y, _GLI.cameraPosition.z)

def setCameraPosition(x, y, z):
    _GLI.cameraPosition.x = x
    _GLI.cameraPosition.y = y
    _GLI.cameraPosition.z = z

def adjustCameraPosition(x, y, z):
    _GLI.cameraPosition.x += x
    _GLI.cameraPosition.y += y
    _GLI.cameraPosition.z += z

def moveCameraForward(distance, flat=False):
    moveCamera(distance, 0, 0, flat)
def moveCameraBackward(distance, flat=False):
    moveCamera(-distance, 0, 0, flat)
def strafeCameraLeft(distance, flat=False):
    moveCamera(distance, 90, 0, flat)
def strafeCameraRight(distance, flat=False):
    moveCamera(distance, -90, 0, flat)


def moveCamera(distance, headingOffset=0, pitchOffset=0, flat=False):
    heading = _GLI.cameraAngles.heading + headingOffset
    pitch = _GLI.cameraAngles.pitch + pitchOffset
    if flat:
        (dx, dz) = polarToCartesian(heading, distance)
        dy = 0
    else:
        (dx, dy, dz) = sphericalToCartesian(heading, pitch, distance)
    adjustCameraPosition(dx, dy, dz)


# converts spherical coordinates to cartesian vector components
# inputs:
#   heading: the angle, in degrees, of ccw rotation around the Y axis (in the XZ plane)
#   pitch: the angle, in degrees, of ccw rotation around the X axis (in the YZ plane)
#   length: the desired length of the resulting vector
# result: a tuple (x,y,z) with the three cartesian components of the resulting vector

def sphericalToCartesian(heading, pitch, length):
    pitch = pitch / 180.0 * 3.1415926535897931
    heading = heading / 180.0 * 3.1415926535897931
    cos_pitch = math.cos(pitch)
    sin_pitch = math.sin(pitch)
    cos_heading = math.cos(heading)
    sin_heading = math.sin(heading)
    dx = length * cos_pitch * -sin_heading
    dy = length * sin_pitch
    dz = length * cos_pitch * -cos_heading
    return (dx,dy,dz)

def cartesianToSphericalAngles(x, y, z):
    heading = math.degrees(math.atan2(-x, -z))
    base = math.sqrt(x**2 + z**2)
    pitch = math.degrees(math.atan2(y, base))
    return (heading, pitch)

def polarToCartesian(heading, length):
    heading = heading / 180.0 * 3.1415926535897931
    dx = length * -math.sin(heading)
    dz = length * -math.cos(heading)
    return (dx,dz)

def cartesianToPolarAngle(x, z):
    return math.degrees(math.atan2(-x, -z))

###########

def setCameraRotation(heading, pitch, roll):
    _GLI.cameraAngles.heading = heading
    _GLI.cameraAngles.pitch = pitch
    _GLI.cameraAngles.roll = roll

def adjustCameraRotation(heading, pitch, roll):
    _GLI.cameraAngles.heading += heading
    _GLI.cameraAngles.pitch += pitch
    _GLI.cameraAngles.roll += roll

def getCameraRotation():
    return (_GLI.cameraAngles.heading, _GLI.cameraAngles.pitch, _GLI.cameraAngles.roll)

#########################################################
#########################################################
#########################################################

class Canvas2D:

    def __init__(self, width, height, opacity=0.8, frameRate=0):
        self.width = width
        self.height = height
        self.transparent = True # opacity < 1
        self.opacity = int(255*opacity)
        surfaceflags = 0
        if self.transparent:
            surfaceflags |= pygame.SRCALPHA
        self.image = pygame.Surface((width,height), surfaceflags)
        self.dirty = True
        self.frameRate = frameRate
        if self.frameRate > 0:
            self.framesToWait = _GLI.frameRate / float(self.frameRate)
        else:
            self.framesToWait = 0
        self.frameCount = self.framesToWait

    def getImageData(self):
        self.frameCount += 1
        if self.dirty and self.frameCount >= self.framesToWait:
            self.imageData = pygame.image.tostring(self.image, "RGBA", True)
            self.dirty = False
            self.frameCount = 0
        return self.imageData

    def lookupColor(self, color):
        if self.transparent:
            a = self.opacity
        else:
            a = 255
        if isinstance(color, str):
            color = lookupColor3D(color)
        if len(color) == 3:
            (r,g,b) = color
        elif len(color) == 4:
            (r,g,b,a) = color
            a = int(a*255)
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        return (r,g,b,a)

def clearCanvas2D(canvas, color='clear'):
    canvas.image.fill(canvas.lookupColor(color))
    canvas.dirty = True

def drawPoint2D(canvas, x, y, color=_GLI.foreground):
    canvas.image.set_at((int(x),int(y)), canvas.lookupColor(color))
    canvas.dirty = True

def drawLine2D(canvas, x1, y1, x2, y2, color=_GLI.foreground, thickness=1):
    pygame.draw.line(canvas.image, canvas.lookupColor(color), (int(x1),int(y1)), (int(x2),int(y2)), int(thickness))
    canvas.dirty = True

def drawCircle2D(canvas, x, y, radius, color=_GLI.foreground, thickness=1):
    pygame.draw.circle(canvas.image, canvas.lookupColor(color), (int(x),int(y)), int(radius), int(thickness))
    canvas.dirty = True

def fillCircle2D(canvas, x, y, radius, color=_GLI.foreground):
    drawCircle2D(canvas, x, y, radius, color, 0)

def drawEllipse2D(canvas, x, y, width, height, color=_GLI.foreground, thickness=1):
    pygame.draw.ellipse(canvas.image, canvas.lookupColor(color), pygame.Rect(int(x-width/2), int(y-height/2), int(width), int(height)), int(thickness))
    canvas.dirty = True

def fillEllipse2D(canvas, x, y, width, height, color=_GLI.foreground):
    drawEllipse2D(canvas, x, y, width, height, color, 0)

def drawRectangle2D(canvas, x, y, width, height, color=_GLI.foreground, thickness=1):
    pygame.draw.rect(canvas.image, canvas.lookupColor(color), pygame.Rect(int(x),int(y),int(width),int(height)), int(thickness))
    canvas.dirty = True

def fillRectangle2D(canvas, x, y, width, height, color=_GLI.foreground):
    drawRectangle2D(canvas, x, y, width, height, color, 0)

def drawPolygon2D(canvas, pointlist, color=_GLI.foreground, thickness=1):
    pygame.draw.polygon(canvas.image, canvas.lookupColor(color), pointlist, int(thickness))
    canvas.dirty = True
    
def fillPolygon2D(canvas, pointlist, color=_GLI.foreground):
    drawPolygon2D(canvas, pointlist, color, 0)


def drawString2D(canvas, text, x, y, font=None, bold=False, italic=False, size=30, color=_GLI.foreground):
    fontSignature = (font,size,bold,italic)
    if fontSignature not in _GLI.fonts:
        font = pygame.font.SysFont(font, size, bold, italic)
        _GLI.fonts[fontSignature] = font
    else:
        font = _GLI.fonts[fontSignature]
    color = canvas.lookupColor(color)
    textimage = font.render(str(text), False, color)
    if canvas.transparent:
        textimage.set_alpha(canvas.opacity)
    canvas.image.blit(textimage, (int(x), int(y)))
    canvas.dirty = True
    return (textimage.get_width(), textimage.get_height())

def sizeString(text, font=None, bold=False, italic=False, size=30):
    fontSignature = (font,size,bold,italic)
    if fontSignature not in _GLI.fonts:
        font = pygame.font.SysFont(font, size, bold, italic)
        _GLI.fonts[fontSignature] = font
    else:
        font = _GLI.fonts[fontSignature]
    textimage = font.render(str(text), False, (1,1,1))
    return (textimage.get_width(), textimage.get_height())
 
def getFontList():
    return pygame.font.get_fonts()

#########################################################

def loadImage(filename, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):
    image = pygame.image.load(filename)
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        image = pygame.transform.rotozoom(image, rotate, scale)
    return image

def drawImage2D(canvas, image, x, y, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        image = pygame.transform.rotozoom(image, rotate, scale)
    if canvas.transparent:
        image.set_alpha(canvas.opacity)
    canvas.image.blit(image, (int(x-image.get_width()/2),int(y-image.get_height()/2)))
    canvas.dirty = True

def getImageWidth(image):
    return image.get_width()

def getImageHeight(image):
    return image.get_height()

def getImagePixel(image, x, y):
    return image.get_at((int(x),int(y)))

def resizeImage(image, width, height):
    return pygame.transform.scale(image, (int(width), int(height)))

def saveImage(image, filename):
    pygame.image.save(image, filename)


#########################################################
#########################################################

def draw3D(model, x=0, y=0, z=0, anglex=0, angley=0, anglez=0, scale=1):
    glPushMatrix()
    if x != 0 or y != 0 or z != 0:
        glTranslate(x, y, z)
    if angley != 0:
        glRotate(angley, 0, 1, 0)
    if anglex != 0:
        glRotate(anglex, 1, 0, 0)
    if anglez != 0:
        glRotate(anglez, 0, 0, 1)
    if scale != 1:
        glEnable(GL_RESCALE_NORMAL)
        glScale(scale, scale, scale)
    model.draw()
    if scale != 1:
        glDisable(GL_RESCALE_NORMAL)
    glPopMatrix()

def draw2D(canvas, x, y):
    if _GLI.selectionDrawingOn:
        return
    # _GLI.hasWindowPos = False # TESTING!
    if _GLI.textureMapsEnabled:
        glDisable(GL_TEXTURE_2D)
    if _GLI.lightingEnabled:
        glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    if _GLI.hasWindowPos:
        if _GLI.currentViewport != None:
            cv = _GLI.currentViewport
            x += cv.x
            y += cv.y
        y = _GLI.windowHeight - (y + canvas.height)
        glWindowPos2d(x,y)
    else:
        y = _GLI.viewportHeight - (y + canvas.height)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, _GLI.viewportWidth, 0, _GLI.viewportHeight)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2d(x,y)
    glDrawPixels(canvas.width, canvas.height, GL_RGBA, GL_UNSIGNED_BYTE, canvas.getImageData())
    if not _GLI.hasWindowPos:
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    if _GLI.textureMapsEnabled:
        glEnable(GL_TEXTURE_2D)
    if _GLI.lightingEnabled:
        glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

#################################################################    

def rotateXAxis(angle):
    glPushMatrix()
    glRotate(angle, 1, 0, 0)
    _GLI.numPushedMatrices += 1
    
def rotateYAxis(angle):
    glPushMatrix()
    glRotate(angle, 0, 1, 0)
    _GLI.numPushedMatrices += 1
    
def rotateZAxis(angle):
    glPushMatrix()
    glRotate(angle, 0, 0, 1)
    _GLI.numPushedMatrices += 1

def rotateAroundVector(angle, x, y, z):
    glPushMatrix()
    glRotate(angle, x, y, z)
    _GLI.numPushedMatrices += 1

    
def translateAxes(x=0, y=0, z=0):
    glPushMatrix()
    glTranslate(x,y,z)
    _GLI.numPushedMatrices += 1

def endTransformation():
    glPopMatrix()
    _GLI.numPushedMatrices -= 1



##########################################################################

def addLight(x=0, y=0, z=0, intensity=1.0):
    if not _GLI.lightingEnabled:
        _GLI.lightingEnabled = True
        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.3, 0.3, 0.3));
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    lightNum = GL_LIGHT0 + _GLI.numLights
    _GLI.numLights += 1
    glLightfv(lightNum, GL_DIFFUSE, (intensity, intensity, intensity, 1.0))
    glLightfv(lightNum, GL_POSITION, (x,y,z,1) )
    _GLI.lights.append( (x,y,z,1) )
    glEnable(lightNum)

def _drawLights():
    if _GLI.lightingEnabled and not _GLI.selectionDrawingOn:
        for lightNum in range(len(_GLI.lights)):
            glLightfv(GL_LIGHT0 + lightNum, GL_POSITION, _GLI.lights[lightNum])


def setAmbientLight(intensity=0.3):
    if not _GLI.lightingEnabled:
        _GLI.lightingEnabled = True
        glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (intensity,intensity,intensity));
    

############################################################################
    
def makeColorsWebPage():
    web = file("colors.html", "w")
    web.write("""<html><head><title>Colors</title></head>
                 <body><center>
                 <h1>Color Names and Values</h1>
                 <table>
              """)
    count = 0
    for (name, red, green, blue, hexcode) in _GLI.colorsList:
        if count % 4 == 0:
            if count > 0:
                web.write('</tr>')
            web.write('<tr>\n')   
        fontcolor = '#000000'
        r = int(red)
        g = int(green)
        b = int(blue)
        if (r+g+b) < 250:
            fontcolor = '#FFFFFF'
        web.write("""<td bgcolor="%s" align=center width=200 height=75>
                  <font color="%s"><b>%s<br>(%d,%d,%d)</b></font></td>""" % (hexcode, fontcolor, name, r, g, b))
        count = count+1
    web.write('</tr></table></center></body></html>')
    web.close()


_GLI.loadColors([
("aliceblue",240,248,255,"#f0f8ff"),
("antiquewhite",250,235,215,"#faebd7"),
("aqua",0,255,255,"#00ffff"),
("aquamarine",127,255,212,"#7fffd4"),
("azure",240,255,255,"#f0ffff"),
("beige",245,245,220,"#f5f5dc"),
("bisque",255,228,196,"#ffe4c4"),
("black",0,0,0,"#000000"),
("blanchedalmond",255,235,205,"#ffebcd"),
("blue",0,0,255,"#0000ff"),
("blueviolet",138,43,226,"#8a2be2"),
("brown",165,42,42,"#a52a2a"),
("burlywood",222,184,135,"#deb887"),
("cadetblue",95,158,160,"#5f9ea0"),
("chartreuse",127,255,0,"#7fff00"),
("chocolate",210,105,30,"#d2691e"),
("coral",255,127,80,"#ff7f50"),
("cornflowerblue",100,149,237,"#6495ed"),
("cornsilk",255,248,220,"#fff8dc"),
("crimson",220,20,60,"#dc143c"),
("cyan",0,255,255,"#00ffff"),
("darkblue",0,0,139,"#00008b"),
("darkcyan",0,139,139,"#008b8b"),
("darkgoldenrod",184,134,11,"#b8860b"),
("darkgray",169,169,169,"#a9a9a9"),
("darkgreen",0,100,0,"#006400"),
("darkgrey",169,169,169,"#a9a9a9"),
("darkkhaki",189,183,107,"#bdb76b"),
("darkmagenta",139,0,139,"#8b008b"),
("darkolivegreen",85,107,47,"#556b2f"),
("darkorange",255,140,0,"#ff8c00"),
("darkorchid",153,50,204,"#9932cc"),
("darkred",139,0,0,"#8b0000"),
("darksalmon",233,150,122,"#e9967a"),
("darkseagreen",143,188,143,"#8fbc8f"),
("darkslateblue",72,61,139,"#483d8b"),
("darkslategray",47,79,79,"#2f4f4f"),
("darkslategrey",47,79,79,"#2f4f4f"),
("darkturquoise",0,206,209,"#00ced1"),
("darkviolet",148,0,211,"#9400d3"),
("deeppink",255,20,147,"#ff1493"),
("deepskyblue",0,191,255,"#00bfff"),
("dimgray",105,105,105,"#696969"),
("dimgrey",105,105,105,"#696969"),
("dodgerblue",30,144,255,"#1e90ff"),
("firebrick",178,34,34,"#b22222"),
("floralwhite",255,250,240,"#fffaf0"),
("forestgreen",34,139,34,"#228b22"),
("fuchsia",255,0,255,"#ff00ff"),
("gainsboro",220,220,220,"#dcdcdc"),
("ghostwhite",248,248,255,"#f8f8ff"),
("gold",255,215,0,"#ffd700"),
("goldenrod",218,165,32,"#daa520"),
("gray",128,128,128,"#808080"),
("green",0,128,0,"#008000"),
("greenyellow",173,255,47,"#adff2f"),
("grey",128,128,128,"#808080"),
("honeydew",240,255,240,"#f0fff0"),
("hotpink",255,105,180,"#ff69b4"),
("indianred",205,92,92,"#cd5c5c"),
("indigo",75,0,130,"#4b0082"),
("ivory",255,255,240,"#fffff0"),
("khaki",240,230,140,"#f0e68c"),
("lavender",230,230,250,"#e6e6fa"),
("lavenderblush",255,240,245,"#fff0f5"),
("lawngreen",124,252,0,"#7cfc00"),
("lemonchiffon",255,250,205,"#fffacd"),
("lightblue",173,216,230,"#add8e6"),
("lightcoral",240,128,128,"#f08080"),
("lightcyan",224,255,255,"#e0ffff"),
("lightgoldenrodyellow",250,250,210,"#fafad2"),
("lightgray",211,211,211,"#d3d3d3"),
("lightgreen",144,238,144,"#90ee90"),
("lightgrey",211,211,211,"#d3d3d3"),
("lightpink",255,182,193,"#ffb6c1"),
("lightsalmon",255,160,122,"#ffa07a"),
("lightseagreen",32,178,170,"#20b2aa"),
("lightskyblue",135,206,250,"#87cefa"),
("lightslategray",119,136,153,"#778899"),
("lightslategrey",119,136,153,"#778899"),
("lightsteelblue",176,196,222,"#b0c4de"),
("lightyellow",255,255,224,"#ffffe0"),
("lime",0,255,0,"#00ff00"),
("limegreen",50,205,50,"#32cd32"),
("linen",250,240,230,"#faf0e6"),
("magenta",255,0,255,"#ff00ff"),
("maroon",128,0,0,"#800000"),
("mediumaquamarine",102,205,170,"#66cdaa"),
("mediumblue",0,0,205,"#0000cd"),
("mediumorchid",186,85,211,"#ba55d3"),
("mediumpurple",147,112,219,"#9370db"),
("mediumseagreen",60,179,113,"#3cb371"),
("mediumslateblue",123,104,238,"#7b68ee"),
("mediumspringgreen",0,250,154,"#00fa9a"),
("mediumturquoise",72,209,204,"#48d1cc"),
("mediumvioletred",199,21,133,"#c71585"),
("midnightblue",25,25,112,"#191970"),
("mintcream",245,255,250,"#f5fffa"),
("mistyrose",255,228,225,"#ffe4e1"),
("moccasin",255,228,181,"#ffe4b5"),
("navajowhite",255,222,173,"#ffdead"),
("navy",0,0,128,"#000080"),
("oldlace",253,245,230,"#fdf5e6"),
("olive",128,128,0,"#808000"),
("olivedrab",107,142,35,"#6b8e23"),
("orange",255,165,0,"#ffa500"),
("orangered",255,69,0,"#ff4500"),
("orchid",218,112,214,"#da70d6"),
("palegoldenrod",238,232,170,"#eee8aa"),
("palegreen",152,251,152,"#98fb98"),
("paleturquoise",175,238,238,"#afeeee"),
("palevioletred",219,112,147,"#db7093"),
("papayawhip",255,239,213,"#ffefd5"),
("peachpuff",255,218,185,"#ffdab9"),
("peru",205,133,63,"#cd853f"),
("pink",255,192,203,"#ffc0cb"),
("plum",221,160,221,"#dda0dd"),
("powderblue",176,224,230,"#b0e0e6"),
("purple",128,0,128,"#800080"),
("red",255,0,0,"#ff0000"),
("rosybrown",188,143,143,"#bc8f8f"),
("royalblue",65,105,225,"#4169e1"),
("saddlebrown",139,69,19,"#8b4513"),
("salmon",250,128,114,"#fa8072"),
("sandybrown",244,164,96,"#f4a460"),
("seagreen",46,139,87,"#2e8b57"),
("seashell",255,245,238,"#fff5ee"),
("sienna",160,82,45,"#a0522d"),
("silver",192,192,192,"#c0c0c0"),
("skyblue",135,206,235,"#87ceeb"),
("slateblue",106,90,205,"#6a5acd"),
("slategray",112,128,144,"#708090"),
("slategrey",112,128,144,"#708090"),
("snow",255,250,250,"#fffafa"),
("springgreen",0,255,127,"#00ff7f"),
("steelblue",70,130,180,"#4682b4"),
("tan",210,180,140,"#d2b48c"),
("teal",0,128,128,"#008080"),
("thistle",216,191,216,"#d8bfd8"),
("tomato",255,99,71,"#ff6347"),
("turquoise",64,224,208,"#40e0d0"),
("violet",238,130,238,"#ee82ee"),
("wheat",245,222,179,"#f5deb3"),
("white",255,255,255,"#ffffff"),
("whitesmoke",245,245,245,"#f5f5f5"),
("yellow",255,255,0,"#ffff00"),
("yellowgreen",154,205,50,"#9acd32")])

_GLI.loadKeys([
    (pygame.K_UP, ['up','up arrow']),
    (pygame.K_DOWN, ['down','down arrow']),
    (pygame.K_RIGHT, ['right','right arrow']),
    (pygame.K_LEFT, ['left','left arrow']),
    (pygame.K_BACKSPACE, ['backspace']),
    (pygame.K_SPACE, ['space', ' ']),
    (pygame.K_RETURN, ['enter', 'return']),
    (pygame.K_TAB, ['tab']),
    
    (pygame.K_a, ['a']),
    (pygame.K_b, ['b']),
    (pygame.K_c, ['c']),
    (pygame.K_d, ['d']),
    (pygame.K_e, ['e']),
    (pygame.K_f, ['f']),
    (pygame.K_g, ['g']),
    (pygame.K_h, ['h']),
    (pygame.K_i, ['i']),
    (pygame.K_j, ['j']),
    (pygame.K_k, ['k']),
    (pygame.K_l, ['l']),
    (pygame.K_m, ['m']),
    (pygame.K_n, ['n']),
    (pygame.K_o, ['o']),
    (pygame.K_p, ['p']),
    (pygame.K_q, ['q']),
    (pygame.K_r, ['r']),
    (pygame.K_s, ['s']),
    (pygame.K_t, ['t']),
    (pygame.K_u, ['u']),
    (pygame.K_v, ['v']),
    (pygame.K_w, ['w']),
    (pygame.K_x, ['x']),
    (pygame.K_y, ['y']),
    (pygame.K_z, ['z']),
    (pygame.K_0, ['0']),
    (pygame.K_1, ['1']),
    (pygame.K_2, ['2']),
    (pygame.K_3, ['3']),
    (pygame.K_4, ['4']),
    (pygame.K_5, ['5']),
    (pygame.K_6, ['6']),
    (pygame.K_7, ['7']),
    (pygame.K_8, ['8']),
    (pygame.K_9, ['9']),

    (pygame.K_BACKQUOTE, ['`' ,'backquote', 'grave', 'grave accent']),
    (pygame.K_MINUS, ['-','minus','dash','hyphen']),
    (pygame.K_EQUALS, ['=','equals']),
    (pygame.K_LEFTBRACKET, ['[','left bracket']),
    (pygame.K_RIGHTBRACKET, [']','right bracket']),
    (pygame.K_BACKSLASH, ['backslash', '\\']),
    (pygame.K_SEMICOLON, [';','semicolon']),
    (pygame.K_QUOTE, ['quote', '\'']),
    (pygame.K_COMMA, [',','comma']),
    (pygame.K_PERIOD, ['.','period']),
    (pygame.K_SLASH, ['/','slash','divide']),

    (pygame.K_DELETE, ['delete']),
    (pygame.K_INSERT, ['insert']),
    (pygame.K_HOME, ['home']),
    (pygame.K_END, ['end']),
    (pygame.K_PAGEUP, ['page up']),
    (pygame.K_PAGEDOWN, ['page down']),
    (pygame.K_CLEAR, ['clear']),
    (pygame.K_PAUSE, ['pause']),

    (pygame.K_F1, ['F1']),
    (pygame.K_F2, ['F2']),
    (pygame.K_F3, ['F3']),
    (pygame.K_F4, ['F4']),
    (pygame.K_F5, ['F5']),
    (pygame.K_F6, ['F6']),
    (pygame.K_F7, ['F7']),
    (pygame.K_F8, ['F8']),
    (pygame.K_F9, ['F9']),
    (pygame.K_F10, ['F10']),
    (pygame.K_F11, ['F11']),
    (pygame.K_F12, ['F12']),
    (pygame.K_F13, ['F13']),
    (pygame.K_F14, ['F14']),
    (pygame.K_F15, ['F15']),

    (pygame.K_RSHIFT, ['right shift']),
    (pygame.K_LSHIFT, ['left shift']),
    (pygame.K_RCTRL, ['right ctrl']),
    (pygame.K_LCTRL, ['left ctrl']),
    (pygame.K_RALT, ['right alt']),
    (pygame.K_LALT, ['left alt']),
    (pygame.K_RMETA, ['right meta']),
    (pygame.K_LMETA, ['left meta']),
    (pygame.K_LSUPER, ['left windows']),
    (pygame.K_RSUPER, ['right windows']),

    (pygame.K_NUMLOCK, ['numlock']),
    (pygame.K_CAPSLOCK, ['capslock']),
    (pygame.K_SCROLLOCK, ['scrollock']),
    (pygame.K_MODE, ['mode']),
    (pygame.K_HELP, ['help']),
    (pygame.K_PRINT, ['print','print screen','prtsc']),
    (pygame.K_SYSREQ, ['sysrq']),
    (pygame.K_BREAK, ['break']),
    (pygame.K_MENU, ['menu']),
    (pygame.K_POWER, ['power']),
    (pygame.K_EURO, ['euro']),
    
    (pygame.K_KP0, ['keypad 0','0']),
    (pygame.K_KP1, ['keypad 1','1']),
    (pygame.K_KP2, ['keypad 2','2']),
    (pygame.K_KP3, ['keypad 3','3']),
    (pygame.K_KP4, ['keypad 4','4']),
    (pygame.K_KP5, ['keypad 5','5']),
    (pygame.K_KP6, ['keypad 6','6']),
    (pygame.K_KP7, ['keypad 7','7']),
    (pygame.K_KP8, ['keypad 8','8']),
    (pygame.K_KP9, ['keypad 9','9']),
    (pygame.K_KP_PERIOD, ['keypad period']),
    (pygame.K_KP_DIVIDE, ['keypad divide']),
    (pygame.K_KP_MULTIPLY, ['keypad multiply']),
    (pygame.K_KP_MINUS, ['keypad minus']),
    (pygame.K_KP_PLUS, ['keypad plus']),
    (pygame.K_KP_EQUALS, ['keypad equals']),
    (pygame.K_KP_ENTER, ['keypad enter'])
])

##    (pygame.K_EXCLAIM, ['!','exclaimation','exclaimation point']),
##    (pygame.K_QUOTEDBL, ['"','double quote']),
##    (pygame.K_HASH, ['#','hash','pound','pound sign']),
##    (pygame.K_DOLLAR, ['$','dollar','dollar sign']),
##    (pygame.K_AMPERSAND, ['&','ampersand','and']),
##    (pygame.K_LEFTPAREN, ['(','left parenthesis']),
##    (pygame.K_RIGHTPAREN, [')','right parenthesis']),
##    (pygame.K_ASTERISK, ['*','asterisk','star','multiply']),
##    (pygame.K_PLUS, ['+','plus','add']),
##    (pygame.K_COLON, [':','colon']),
##    (pygame.K_LESS, ['<','less-than']),
##    (pygame.K_GREATER, ['>','greater-than']),
##    (pygame.K_QUESTION, ['?','question','question mark']),
##    (pygame.K_AT, ['@','at','at sign']),
##    (pygame.K_CARET, ['^','caret']),
##    (pygame.K_UNDERSCORE, ['_','underscore']),



#############################################################################
#############################################################################
#############################################################################

class Collada:

    def __init__(self, filename, stats=True):
        self.givenFilename = filename
        (self.daeFile, self.zipMode) = self.determineDAE(filename)
        self.stats = stats
        self.up_axis = None
        self.images = dict()        # key is image_id, value is pathname to image file
        self.effects = dict()       # key is effect_id, value is an MaterialEffect object
        self.materials = dict()     # key is material_id, value is effect_id
        self.geometries = dict()    # key is geometry_id, value is list of GeometryPrimitive objects
        self.nodes = dict()         # key is node_id, value is Node object
        self.visual_scenes = dict() # key is visual_scene_id, value is Node object for the Model node
        self.scene = None           # visual_scene id for primary visual_scene
        self.minx = self.miny = self.minz = float('infinity')
        self.maxx = self.maxy = self.maxz = -float('infinity')
        self.sumx = self.sumy = self.sumz = 0
        self.countVertices = 0
        self.countPolygons = 0
       
        self.read(self.daeFile)
        self.components = self.buildComponentList()

        if self.stats:
            self.avgx = self.sumx / float(self.countVertices)
            self.avgy = self.sumy / float(self.countVertices)
            self.avgz = self.sumz / float(self.countVertices)
            print "read "+self.givenFilename+" with "+str(self.countPolygons)+" polygons"
            fmt = ".3f"
            print "   x avg = " + format(self.avgx, fmt) + " ranging from " + format(self.minx, fmt) + " to " + format(self.maxx, fmt)
            print "   y avg = " + format(self.avgy, fmt) + " ranging from " + format(self.miny, fmt) + " to " + format(self.maxy, fmt)
            print "   z avg = " + format(self.avgz, fmt) + " ranging from " + format(self.minz, fmt) + " to " + format(self.maxz, fmt)            

    def determineDAE(self, givenFilename):
        if not os.path.exists(givenFilename):
            raise ValueError, "ERROR: no such file: " + givenFilename
        if givenFilename.endswith('.dae'):
            return (givenFilename, False)
        elif os.path.isdir(givenFilename):
            modelsdir = os.path.join(givenFilename, "models")
            if os.path.isdir(modelsdir):
                filelist = os.listdir(modelsdir)
                filedir = modelsdir
            else:
                filelist = os.listdir(givenFilename)
                filedir = givenFilename
            daefiles = [name for name in filelist if name.endswith('.dae')]
            if len(daefiles) > 1:
                raise ValueError, 'ERROR: too many .dae files in ' + givenFilename
            if len(daefiles) == 0:
                raise ValueError, 'ERROR: no .dae files found in ' + givenFilename
            return (os.path.join(filedir, daefiles[0]), False)
        elif givenFilename.endswith('.zip'):
            ziparchive = zipfile.ZipFile(givenFilename)
            zipcontents = ziparchive.namelist()
            self.ziparchiveFiles = dict()
            for original in zipcontents:
                self.ziparchiveFiles[original.lower()] = original
            daefiles = [self.ziparchiveFiles[name] for name in self.ziparchiveFiles if name.endswith('.dae')]
            if len(daefiles) > 1:
                raise ValueError, 'ERROR: too many .dae files in ' + givenFilename
            if len(daefiles) == 0:
                raise ValueError, 'ERROR: no .dae files found in ' + givenFilename
            daefile = ziparchive.open(daefiles[0])
            self.ziparchive = ziparchive
            return (daefile, True) 
        else:
            raise ValueError, 'ERROR: not a .dae file or folder: ' + givenFilename

    @staticmethod
    def tag(tag):
        return str(xml.etree.ElementTree.QName('http://www.collada.org/2005/11/COLLADASchema', tag))

    def read(self, filename):
        print "reading " + self.givenFilename
        self.tree = xml.etree.ElementTree.parse(filename)
        root = self.tree.getroot()
        self.readAsset(root.find(Collada.tag('asset')))
        self.images = self.readLibraryImages(root.find(Collada.tag('library_images')))
        self.effects = self.readLibraryEffects(root.find(Collada.tag('library_effects')))
        self.materials = self.readLibraryMaterials(root.find(Collada.tag('library_materials')))
        self.geometries = self.readLibraryGeometries(root.find(Collada.tag('library_geometries')))
        self.readLibraryNodes(root.find(Collada.tag('library_nodes')))
        self.visual_scenes = self.readLibraryVisualScenes(root.find(Collada.tag('library_visual_scenes')))
        self.scene = self.readScene(root.find(Collada.tag('scene')))
        
    def readAsset(self, asset):
        up_axis_element = asset.find(Collada.tag('up_axis'))
        if up_axis_element is None:
            self.up_axis = 'Z_UP'
        else:
            self.up_axis = up_axis_element.text
        assert self.up_axis in ['X_UP', 'Y_UP', 'Z_UP'], "unknown up_axis type: "+str(self.up_axis)

    def readLibraryImages(self, library_images):
        images = dict()
        if library_images is None:
            return
        imagelist = library_images.findall(Collada.tag('image'))
        for image in imagelist:
            image_id = image.get('id')
            init_from = image.find(Collada.tag('init_from'))
            image_name = init_from.text
            if not self.zipMode:
                images[image_id] = os.path.join(os.path.dirname(self.daeFile), image_name)
            else:
                image_name = self.ziparchiveFiles[image_name.lstrip('./').lower()]
                image_data = self.ziparchive.open(image_name).read()
                image_file_object = cStringIO.StringIO(image_data)
                images[image_id] = (image_file_object, os.path.join(self.givenFilename, image_name))
        return images
        
    def readLibraryEffects(self, library_effects):
        effects = dict()
        effectlist = library_effects.findall(Collada.tag('effect'))
        for effect in effectlist:
            effect_id = effect.get('id')
            profile_common = effect.find(Collada.tag('profile_COMMON'))
            samplers = dict() # key is newparam sid, value is sampler source text
            surfaces = dict() # key is newparam sid, value is init_from text
            newparam_elements = profile_common.findall(Collada.tag('newparam'))
            for newparam in newparam_elements:
                newparam_id = newparam.get('sid')
                for newparam_child in newparam.getchildren():
                    if newparam_child.tag == Collada.tag('surface'):
                        init_from = newparam_child.find(Collada.tag('init_from'))
                        surfaces[newparam_id] = init_from.text
                    elif newparam_child.tag == Collada.tag('sampler2D'):
                        source = newparam_child.find(Collada.tag('source'))
                        samplers[newparam_id] = source.text
                    else:
                        assert False, 'unknown newparam type: ' + str(newparam_child.tag)
            technique = profile_common.find(Collada.tag('technique'))
            shader = technique.find(Collada.tag('lambert'))
            if shader is None:
                shader = technique.find(Collada.tag('phong'))
            if shader is not None:
                diffuse = shader.find(Collada.tag('diffuse'))
                colorElement = diffuse.find(Collada.tag('color'))
                effectType = Collada.MaterialEffect()
                if colorElement is not None:
                    diffuseColor = [float(n) for n in colorElement.text.split()]
                    assert len(diffuseColor) == 4
                    effectType.diffuse = diffuseColor
                else:
                    texture = diffuse.find(Collada.tag('texture'))
                    if texture is not None:
                        textureSampler = texture.get('texture')
                        sampler_surface = samplers[textureSampler]
                        surface_image = surfaces[sampler_surface]
                        image_file = self.images[surface_image]
                        effectType.texture = image_file
                    else:
                        assert False, "unknown diffuse type"
            else:
                shader = technique.find(Collada.tag('constant'))
                if shader is not None:
                    # really bad handling of constant shaders - this is not right
                    transparent = shader.find(Collada.tag('transparent'))
                    colorElement = transparent.find(Collada.tag('color'))
                    effectType = Collada.MaterialEffect()
                    effectType.diffuse = [float(n) for n in colorElement.text.split()]
                else:
                    print "WARNING: unknown shader type in effect " + effect_id
                    effectType = None

            effects[effect_id] = effectType
        return effects

    def readLibraryMaterials(self, library_materials):
        materials = dict()
        materiallist = library_materials.findall(Collada.tag('material'))
        for material in materiallist:
            material_id = material.get('id')
            instance_effect = material.find(Collada.tag('instance_effect'))
            effect = instance_effect.get('url').lstrip('#')
            assert effect in self.effects
            materials[material_id] = effect
        return materials

    def readLibraryGeometries(self, library_geometries):
        geometries = dict()
        
        sources = dict()
            # key is source_id
            # value is a dictionary
            #    where key is param name(like X,Y,Z,S,T) and value is list of floats for that param
            
        vertices = dict()
            # key is vertices_id
            # value is a dictionary
            #     where key is semantic name (like POSITION,NORMAL) and value is source id
            
        for geometry in library_geometries.getchildren():
            geometry_id = geometry.get('id')
            primitives = list()
            mesh = geometry.find(Collada.tag('mesh'))
            for meshchild in mesh.getchildren():
                if (meshchild.tag == Collada.tag('source')):
                    self.readMeshSource(meshchild, sources)
                elif (meshchild.tag == Collada.tag('vertices')):
                    self.readMeshVertices(meshchild, vertices)
                elif (meshchild.tag == Collada.tag('triangles')):
                    primitives.append(self.readMeshPrimitive(meshchild, Collada.GeometryTriangles(), sources, vertices))
                elif (meshchild.tag == Collada.tag('lines')):
                    primitives.append(self.readMeshPrimitive(meshchild, Collada.GeometryLines(),sources, vertices))
                else:
                    print "WARNING: unhandled mesh type: "+meshchild.tag+" in geometry "+geometry_id
            geometries[geometry_id] = primitives
                    
        return geometries
                    
    def readMeshSource(self, source, sources):
        source_id = source.get('id')
        assert source_id not in sources
        float_array = source.find(Collada.tag('float_array'))
        float_array_id = float_array.get('id')
        float_array_count = int(float_array.get('count'))
        float_array_text_list = float_array.text.split()
        assert len(float_array_text_list) == float_array_count, 'float array length error for '+float_array_id+' '+str(len(float_array_text_list))+' != '+str(float_array_count)
        technique_common = source.find(Collada.tag('technique_common'))
        accessor = technique_common.find(Collada.tag('accessor'))
        accessor_count = int(accessor.get('count'))
        accessor_source = accessor.get('source').lstrip('#')
        accessor_stride = int(accessor.get('stride'))
        assert accessor_source == float_array_id, 'accessor_source '+accessor_source+' != float_array_id '+float_array_id
        assert accessor_count * accessor_stride == float_array_count
        accessor_children = accessor.getchildren()
        assert len(accessor_children) == accessor_stride
        source_data = dict() # key is param name, value is data list
        for param_offset in range(len(accessor_children)):
            param = accessor_children[param_offset]
            assert param.tag == Collada.tag('param'), 'unknown accessor child: '+param.tag
            param_name = param.get('name')
            param_data = [float(float_array_text_list[i]) for i in range(param_offset, len(float_array_text_list), accessor_stride)]
            assert len(param_data) == accessor_count
            source_data[param_name] = param_data
        sources[source_id] = source_data

    def readMeshVertices(self, verticesElement, vertices):
        vertices_id = verticesElement.get('id')
        assert vertices_id not in vertices
        vertices_data = dict() # key is semantic name, value is source id
        for vertices_child in verticesElement.getchildren():
            assert vertices_child.tag == Collada.tag('input')
            vertices_input = vertices_child
            semantic = vertices_input.get('semantic')
            assert semantic in ['POSITION', 'NORMAL', 'TEXCOORD']
            source = vertices_input.get('source').lstrip('#')
            assert semantic not in vertices_data
            vertices_data[semantic] = source
        vertices[vertices_id] = vertices_data

    def readMeshPrimitive(self, element, primitive, sources, vertices):
        primitive.material = element.get('material')
        count = int(element.get('count'))
        mySources = dict()  # key is semantic, value is source id
        myOffsets = dict()  # key is semantic, value is offset
        maxoffset = 0
        inputChildren = element.findall(Collada.tag('input'))
        for inputElement in inputChildren:
            semantic = inputElement.get('semantic')
            assert semantic in ['VERTEX', 'POSITION', 'NORMAL', 'TEXCOORD']
            source = inputElement.get('source').lstrip('#')
            offset = int(inputElement.get('offset'))
            if offset > maxoffset:
                maxoffset = offset
            if semantic == 'VERTEX':
                assert source in vertices
                for vertices_semantic in vertices[source]:
                    mySources[vertices_semantic] = vertices[source][vertices_semantic]
                    myOffsets[vertices_semantic] = offset
            else:
                mySources[semantic] = source
                myOffsets[semantic] = offset
        pElement = element.find(Collada.tag('p'))
        primitive_list = map(int, pElement.text.split())
        stride = maxoffset+1
        assert len(primitive_list) == count * primitive.verticesPerPrimitive * stride
        assert 'POSITION' in mySources
        assert 'POSITION' in myOffsets
        positionIndices = [primitive_list[i] for i in range(myOffsets['POSITION'], len(primitive_list), stride)]
        assert len(positionIndices) == count*primitive.verticesPerPrimitive
        source = sources[mySources['POSITION']]
        primitive.positions = self.getXYZCoordinatesFromSource(source, positionIndices)
        self.computeStats(primitive.positions)
        assert len(primitive.positions) == count*primitive.verticesPerPrimitive
        if 'NORMAL' in mySources:
            normalIndices = [primitive_list[i] for i in range(myOffsets['NORMAL'], len(primitive_list), stride)]
            source = sources[mySources['NORMAL']]
            primitive.normals = self.getXYZCoordinatesFromSource(source, normalIndices)
        if 'TEXCOORD' in mySources:
            texcoordIndices = [primitive_list[i] for i in range(myOffsets['TEXCOORD'], len(primitive_list), stride)]
            source = sources[mySources['TEXCOORD']]
            primitive.texcoords = self.getSTCoordinatesFromSource(source, texcoordIndices)
            #primitive.texcoords = [(source['S'][i], source['T'][i]) for i in texcoordIndices]
        self.countPolygons += count
        return primitive

    def getXYZCoordinatesFromSource(self, source, indices):
        return [(source['X'][i], source['Y'][i], source['Z'][i]) for i in indices]
        #if self.up_axis == 'Y_UP':
        #    return [(source['X'][i], source['Y'][i], source['Z'][i]) for i in indices]
        #elif self.up_axis == 'Z_UP':
        #    return [(source['X'][i], source['Z'][i], -source['Y'][i]) for i in indices]
        #elif self.up_axis == 'X_UP':
        #    return [(-source['Y'][i], source['X'][i], source['Z'][i]) for i in indices]
        #assert False, "unknown up_axis: " + str(self.up_axis)

    def getSTCoordinatesFromSource(self, source, indices):
        return [(source['S'][i], source['T'][i]) for i in indices]
        #if self.up_axis == 'Y_UP':
        #    return [(source['S'][i], source['T'][i]) for i in indices]
        #elif self.up_axis == 'Z_UP':
        #    return [(source['S'][i], -source['T'][i]) for i in indices]
        #elif self.up_axis == 'X_UP':
        #    return [(source['S'][i], source['T'][i]) for i in indices]  # what should this one be?
        #assert False, "unknown up_axis: " + str(self.up_axis)


    def computeStats(self, positions):
        if self.stats:
            Xs = [x for (x,y,z) in positions]
            Ys = [y for (x,y,z) in positions]
            Zs = [z for (x,y,z) in positions]
            self.minx = min(self.minx, min(Xs))
            self.miny = min(self.miny, min(Ys))
            self.minz = min(self.minz, min(Zs))
            self.maxx = max(self.maxx, max(Xs))
            self.maxy = max(self.maxy, max(Ys))
            self.maxz = max(self.maxz, max(Zs))
            self.sumx += sum(Xs)
            self.sumy += sum(Ys)
            self.sumz += sum(Zs)
            self.countVertices += len(Xs)

    def readLibraryNodes(self, library_nodes):
        if library_nodes is not None:
            self.readChildNodes(library_nodes)

    def readChildNodes(self, parentNode):
        nodelist = list()
        nodeElementList = parentNode.findall(Collada.tag('node'))
        if nodeElementList is None:
            return nodelist
        for node_element in nodeElementList:
            node = self.readNode(node_element)
            nodelist.append(node)
        return nodelist

    def readNode(self, node_element):
        node_id = node_element.get('id')
        assert node_id not in self.nodes
        node = Collada.Node(node_id)
        self.nodes[node_id] = node
        matrix_elements = node_element.findall(Collada.tag('matrix'))
        for matrix_element in matrix_elements:
            node.matrices.append([float(n) for n in matrix_element.text.split()])
        instance_geometries = node_element.findall(Collada.tag('instance_geometry'))
        for instance_geometry_element in instance_geometries:
            geometry_id = instance_geometry_element.get('url').lstrip('#')
            assert geometry_id in self.geometries, 'unknown geometry id: '+str(geometry_id)
            instance_geometry = Collada.InstanceGeometry(geometry_id, self.geometries[geometry_id])
            bind_material = instance_geometry_element.find(Collada.tag('bind_material'))
            technique_common = bind_material.find(Collada.tag('technique_common'))
            instance_materials = technique_common.findall(Collada.tag('instance_material'))
            for instance_material in instance_materials:
                symbol = instance_material.get('symbol')
                target = instance_material.get('target').lstrip('#')
                effect = self.materials[target]
                materialEffect = self.effects[effect]
                instance_geometry.materials[symbol] = materialEffect
            node.instanceGeometries.append(instance_geometry)
        node.nodes = self.readChildNodes(node_element)
        instance_nodes = node_element.findall(Collada.tag('instance_node'))
        for instance_node in instance_nodes:
            instance_node_id = instance_node.get('url').lstrip('#')
            #assert instance_node_id in self.nodes, 'unknown instance node url: '+ str(instance_node_id)
            #node.nodes.append(self.nodes[instance_node_id])
            node.instance_nodes.append(instance_node_id)
        return node

    def readLibraryVisualScenes(self, library_visual_scenes):
        visual_scenes = dict()
        visual_scene_elements = library_visual_scenes.findall(Collada.tag('visual_scene'))
        for visual_scene in visual_scene_elements:
            visual_scene_id = visual_scene.get('id')
            mainNode = None
            node_elements = visual_scene.findall(Collada.tag('node'))
            for node_element in node_elements:
                node_id = node_element.get('id')
                #if node_id not in ['Model', 'Camera']:
                #    print "node_id =", node_id
                if node_id != 'Camera':
                    assert mainNode == None
                    mainNode = self.readNode(node_element)
            visual_scenes[visual_scene_id] = mainNode
        return visual_scenes

    def readScene(self, scene):
        instance_visual_scene = scene.find(Collada.tag('instance_visual_scene'))
        instance_visual_scene_id = instance_visual_scene.get('url').lstrip('#')
        assert instance_visual_scene_id in self.visual_scenes
        return instance_visual_scene_id
    
    def buildComponentList(self):
        rootNode = self.visual_scenes[self.scene]
        components = self.buildComponentsForNode(rootNode, [])
        return components

    def buildComponentsForNode(self, node, matrices):
        assert(matrices != None)
        components = list()
        matrices = matrices[:]
        matrices.extend(node.matrices)
        assert(matrices != None)
        for instanceGeometry in node.instanceGeometries:
            for geometryPrimitive in instanceGeometry.geometryPrimitives:
                if geometryPrimitive.getVertexCount() == 0 :
                    print "WARNING: empty geometry primitive in geometry id " + instanceGeometry.id  + " in node " + node.id
                else:
                    cigp = Collada.InstanceGeometryPrimitive(instanceGeometry, geometryPrimitive, matrices)
                    if cigp.material is None:
                        print "WARNING: no material specified for geometry id " + instanceGeometry.id  
                    else:
                        components.append(cigp)
        for childNode in node.nodes:
            components.extend(self.buildComponentsForNode(childNode, matrices))
        for instanceNode in node.instance_nodes:
            components.extend(self.buildComponentsForNode(self.nodes[instanceNode], matrices))
        return components

    def getComponents(self):
        return self.components


    class Node:
        def __init__(self, node_id):
            self.id = node_id
            self.matrices = []
            self.instanceGeometries = list() # list of InstanceGeometry objects
            self.nodes = list()  # list of child Node objects
            self.instance_nodes = list()
            
    class MaterialEffect:
        def __init__(self):
            self.texture = None
            self.diffuse = None
            
    class GeometryPrimitive:
        def __init__(self):
            self.material = None
            self.positions = list()
            self.normals = list()
            self.texcoords = list()
        def getVertexCount(self):
            return len(self.positions)
        def getPolygonCount(self):
            return len(self.positions) / self.verticesPerPrimitive

    class GeometryTriangles(GeometryPrimitive):
        def __init__(self):
            Collada.GeometryPrimitive.__init__(self)
            self.openGLPrimitive = GL_TRIANGLES
            self.verticesPerPrimitive = 3

    class GeometryLines(GeometryPrimitive):
        def __init__(self):
            Collada.GeometryPrimitive.__init__(self)
            self.openGLPrimitive = GL_LINES
            self.verticesPerPrimitive = 2



    class InstanceGeometry:
        def __init__(self, geometry_id, geometry):
            self.id = geometry_id
            self.geometryPrimitives = geometry
            self.materials = dict()  # key is material symbol, value is MaterialEffect object

    class InstanceGeometryPrimitive:
        def __init__(self, instanceGeometry, geometryPrimitive, matrices):
            self.geometry = geometryPrimitive
            self.material = instanceGeometry.materials[geometryPrimitive.material]
            self.matrices = matrices
            #self.matrices.reverse()

#############################################################################
#############################################################################
#############################################################################
#############################################################################

class Shape3D:

    def __init__(self):
        self.selectionID = None
        self.bufferIDDict = {} # key = selection ID, value = Color Buffer ID

    class Buffers:
        def __init__(self, vertexList, normalList, colorList, texCoordList):
            self.numVertexes = len(vertexList)
            self.selectionColorBufferID = 0
            if not _GLI.useInterleavedArrays:
                self.vertexBufferID   = self.configureVBOBuffer(vertexList)
                self.normalBufferID   = self.configureVBOBuffer(normalList)
                self.colorBufferID    = self.configureVBOBuffer(colorList)
                self.texCoordBufferID = self.configureVBOBuffer(texCoordList)
            else: 
                colors = False
                textures = False
                normals = False
                colorParts = 3
                if normalList is not None and normalList != []:
                    normals = True
                if texCoordList is not None and texCoordList != []:
                    textures = True
                elif colorList is not None and colorList != []:
                    colors = True
                if normals:
                    if textures:
                        self.format = GL_T2F_N3F_V3F
                    elif colors:
                        self.format = GL_C4F_N3F_V3F
                        colorParts = 4
                    else:
                        self.format = GL_N3F_V3F
                else:
                    if textures:
                        self.format = GL_T2F_V3F
                    elif colors:
                        self.format = GL_C3F_V3F
                    else:
                        self.format = GL_V3F
                dataList = []
                for i in range(len(vertexList)):
                    if textures:
                        dataList.extend(texCoordList[i])
                    elif colors:
                        if colorParts == len(colorList[i]):
                            dataList.extend(colorList[i])
                        elif colorParts == 4 and len(colorList[i]) == 3:
                            dataList.extend(colorList[i])
                            dataList.append(1.0)
                        elif colorParts == 3 and len(colorList[i]) == 4:
                            dataList.extend(colorList[i][:3])
                    if normals:
                        dataList.extend(normalList[i])
                    dataList.extend(vertexList[i])
                self.bufferID = self.configureVBOBuffer(dataList)

                if _GLI.enableSelection:
                    self.vertexBufferID = self.configureVBOBuffer(vertexList)
                

        def configureVBOBuffer(self, dataList):
            if dataList is None or len(dataList)==0:
                return 0
            bufferID = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, bufferID)
            if _GLI.hasNumPy:
                dataArray = numpy.array(dataList, dtype=numpy.float32)
            else:
                dataArray = _GLI.arrayHandler.asArray(dataList, GL_FLOAT)
            glBufferData(GL_ARRAY_BUFFER, dataArray, GL_STATIC_DRAW)
            return bufferID

        def delete(self):
            glDeleteBuffers(1, GLuint(self.bufferID))

        def select(self):
            if _GLI.enableSelection and _GLI.selectionDrawingOn:
                glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferID)
                glVertexPointer(3, GL_FLOAT, 0, None)

                if self.selectionColorBufferID != 0:
                    glBindBuffer(GL_ARRAY_BUFFER, self.selectionColorBufferID)
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointer(3, GL_FLOAT, 0, None)
                else:
                    glDisableClientState(GL_COLOR_ARRAY)
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)
                    
            elif _GLI.useInterleavedArrays:
                glBindBuffer(GL_ARRAY_BUFFER, self.bufferID)
                glInterleavedArrays(self.format, 0, None)
                
            else:
                # if interleaved arrays is broken (like some versions of windows)
                glBindBuffer(GL_ARRAY_BUFFER, self.vertexBufferID)
                glVertexPointer(3, GL_FLOAT, 0, None)
                
                glBindBuffer(GL_ARRAY_BUFFER, self.normalBufferID)
                if self.normalBufferID == 0:
                    glDisableClientState(GL_NORMAL_ARRAY)
                else:
                    glEnableClientState(GL_NORMAL_ARRAY)
                    glNormalPointer(GL_FLOAT, 0, None)
                    
                glBindBuffer(GL_ARRAY_BUFFER, self.colorBufferID)
                if self.colorBufferID == 0:
                    glDisableClientState(GL_COLOR_ARRAY)
                else:
                    glEnableClientState(GL_COLOR_ARRAY)
                    glColorPointer(3, GL_FLOAT, 0, None)
                    
                glBindBuffer(GL_ARRAY_BUFFER, self.texCoordBufferID)
                if self.texCoordBufferID == 0:
                    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
                else:
                    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                    glTexCoordPointer(2, GL_FLOAT, 0, None)


    def delete(self):
        self.buffers.delete()

    def setTexture(self, texture):
        self.textureID = _GLI.getTextureID(texture)
        return self.textureID

    def useTexture(self, textureID=None):
        if textureID is None:
            textureID = self.textureID
        if _GLI.enableSelection and _GLI.selectionDrawingOn:
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, textureID)
    
    def countPolygons(self, numPolygons):
        _GLI.polygonCount += numPolygons

    def setSelectionID(self, selectionID):
        # this was originally written by Austin Hunter '11
        if _GLI.enableSelection and (_GLI.selectionDrawingOn or _GLI.currentMode != _GLI.DRAW_MODE):
            self.selectionID = selectionID
            if self.selectionID not in _GLI.selectColorIDDict:
                # this selectionID has never been used before - generate a new color
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                while color in _GLI.selectColorDict:
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                (r, g, b) = color
                floatColor = (r/255.0, g/255.0, b/255.0)
                _GLI.selectColorIDDict[self.selectionID] = floatColor # 0-1 float colors
                _GLI.selectColorDict[color] = self.selectionID # 0-255 integer colors
            if self.selectionID not in self.bufferIDDict:
                # this selectionID has never been used for this model
                floatColor = _GLI.selectColorIDDict[self.selectionID]
                colorList = [floatColor] * self.buffers.numVertexes
                self.buffers.selectionColorBufferID = self.buffers.configureVBOBuffer(colorList)
                self.bufferIDDict[self.selectionID] = self.buffers.selectionColorBufferID
            else:
                # this selectionID has been used on this model before
                self.buffers.selectionColorBufferID = self.bufferIDDict[self.selectionID]

#############################################################################

def enableSelection():
    _GLI.enableSelection = True

def disableSelection():
    _GLI.enableSelection = False

def setSelectionLabel(model, label):
    model.setSelectionID(label)

def getSelectedObject(x, y):
    if _GLI.enableSelection:
            
        _GLI.selectionDrawingOn = True
        glDrawBuffer(GL_AUX1)
        if _GLI.fogMode != 0:
            glDisable(GL_FOG)
        _render()
        glDrawBuffer(GL_BACK)
        _GLI.selectionDrawingOn = False
        if _GLI.fogMode != 0:
            glEnable(GL_FOG)
        
        glReadBuffer(GL_AUX1)
        data = glReadPixels(x, getWindowHeight() - y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
        glReadBuffer(GL_BACK)
        (r, g, b) = struct.unpack("BBB", data)
        if (r, g, b) in _GLI.selectColorDict:
            ID = _GLI.selectColorDict[(r, g, b)]
            return ID
    return None
    
#############################################################################
#############################################################################

class GridShape3D(Shape3D):
  
  def __init__(self, rows, cols, colors, texture):
      Shape3D.__init__(self)
      self.rows = rows
      self.cols = cols
      self.colors = colors
      self.setTexture(texture)
      self.vertices = []
      self.normals = []
      self.textures = []
      for row in xrange(self.rows+1):
          self.vertices.append([0]*(cols+1))
          self.normals.append([0]*(cols+1))
          self.textures.append([0]*(cols+1))

  def save(self):
      self.vertexList = []
      self.colorList = []
      self.normalList = []
      self.texCoordList = []
      colorIndex = 0
      for row in xrange(self.rows):
          colorIndex = row % len(self.colors)
          for col in xrange(self.cols):
              self.saveVertex(row, col)
              self.saveVertex(row, col+1)
              self.saveVertex(row+1, col+1)
              self.saveVertex(row+1, col)
              color = self.colors[colorIndex]
              self.colorList.extend([lookupColor3D(color)] * 4)
              colorIndex = (colorIndex+1) % len(self.colors)
      if self.textureID == 0:
          self.texCoordList = None
      else:
          self.colorList = None
      self.buffers = self.Buffers(self.vertexList, self.normalList, self.colorList, self.texCoordList)  

  def saveVertex(self, r, c):
      vertex = self.vertices[r][c]
      self.vertexList.append( (vertex[0], vertex[1], vertex[2]) )
      normal = self.normals[r][c]
      self.normalList.append( (normal[0], normal[1], normal[2]) )
      texture = self.textures[r][c]
      self.texCoordList.append( (texture[0], texture[1]) )

  def draw(self):
      self.useTexture()
      self.buffers.select()
      glDrawArrays(GL_QUADS, 0, self.rows*self.cols*4)
      self.countPolygons(self.rows*self.cols)
    
#############################################################################

class Sphere3D(GridShape3D):
    def __init__(self, radius, detailLevel=12, colors=[(0,0,0),(1,1,1)], texture=None):
        rows = detailLevel
        cols = detailLevel*2
        GridShape3D.__init__(self, rows, cols, colors, texture)
        self.radius = float(radius)
        for row in xrange(rows+1):
            for col in xrange(cols+1):
                sliceangle = row * (math.pi / rows)
                r = self.radius * math.sin(sliceangle)
                y = self.radius * math.cos(sliceangle)
                wedgeangle = col * (2*math.pi / cols)
                x = r * math.cos(wedgeangle)
                z = r * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, y/self.radius, z/self.radius)
                self.textures[row][col] = ( (cols-col)/float(cols), (rows-row)/float(rows) )
        self.save()

#######################################################################################

class Cylinder3D(GridShape3D):
    def __init__(self, height, radius, slices=6, wedges=12, colors=[(0,0,0),(1,1,1)], texture=None):
        GridShape3D.__init__(self, slices, wedges, colors, texture)
        self.height = float(height)
        self.radius = float(radius)
        thickness = self.height / slices
        for row in xrange(self.rows+1):
            for col in xrange(self.cols+1):
                y = thickness*(self.rows/2.0) - thickness*row
                wedgeangle = col * (2*math.pi / self.cols)
                x = self.radius * math.cos(wedgeangle)
                z = self.radius * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, 0, z/self.radius)
                self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
        self.save()

#######################################################################################

class Cone3D(GridShape3D):
    def __init__(self, height, radius, slices=6, wedges=12, colors=[(0,0,0),(1,1,1)], texture=None):
        GridShape3D.__init__(self, slices, wedges, colors, texture)
        self.height = float(height)
        self.radius = float(radius)
        thickness = self.height / slices
        radius_step = float(radius) / slices
        for row in xrange(self.rows+1):
            for col in xrange(self.cols+1):
                y = thickness*row
                wedgeangle = col * (2*math.pi / self.cols)
                radius = self.radius - (row * radius_step)
                x = radius * math.cos(wedgeangle)
                z = radius * math.sin(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x/self.radius, 0, z/self.radius)  # wrong!!!
                self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
        self.save()

#######################################################################################

class Torus3D(GridShape3D):
    def __init__(self, majorRadius, minorRadius, slices=12, wedges=8, colors=[(0,0,0),(1,1,1)], texture=None):
        GridShape3D.__init__(self, slices, wedges, colors, texture)
        self.majorRadius = float(majorRadius)
        self.minorRadius = float(minorRadius)
        for row in xrange(self.rows+1):
            for col in xrange(self.cols+1):
                sliceangle = row * (2*math.pi / self.rows)
                cx = majorRadius * math.cos(sliceangle)
                cz = majorRadius * math.sin(sliceangle)      
                wedgeangle = col * (2*math.pi / self.cols)      
                y = minorRadius * math.sin(wedgeangle)
                x = cx + minorRadius * math.cos(sliceangle) * math.cos(wedgeangle)
                z = cz + minorRadius * math.sin(sliceangle) * math.cos(wedgeangle)
                self.vertices[row][col] = (x, y, z)
                self.normals[row][col] = (x-cx, y, z-cz)
                #self.textures[row][col] = ( (self.cols-col)/float(self.cols), (self.rows-row)/float(self.rows) )
                self.textures[row][col] = ( (col)/float(self.cols), (row)/float(self.rows) )
        self.save()

###############################################################################################################

class Rect3D(GridShape3D):
    def __init__(self, width=1, height=1, colors=[(0,0,0),(1,1,1)], texture=None, textureRepeat=1):
        self.width = float(width)
        self.height = float(height)
        if width == height:
            rows = textureRepeat
            cols = textureRepeat
        elif width > height:
            cols = textureRepeat
            rows = int(math.ceil((self.height / (self.width/textureRepeat))))
        else:
            rows = textureRepeat
            cols = int(math.ceil(self.width / (self.height/textureRepeat)))

        GridShape3D.__init__(self, rows, cols, colors, texture)
        
        w = self.width/2.0
        h = self.height/2.0
        xstep = self.width/cols
        ystep = self.height/rows

        for row in xrange(rows+1):
            for col in xrange(cols+1):
                x = col * xstep - w
                y = row * ystep - h
                z = 0
                self.vertices[row][col] = (x,y,z)
                self.normals[row][col] = (0,0,1)
                self.textures[row][col] = ( col, row )
        self.save()

#######################################################################################

class Box3D(Shape3D):
    def __init__(self, width=1, height=1, depth=1, colors=[(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1)], texture=None):
        Shape3D.__init__(self)
        self.width = width
        self.height = height
        self.depth = depth
        self.setTexture(texture)
        w = float(width)/2.0
        h = float(height)/2.0
        d = float(depth)/2.0
        vertices = [ (-w,h,-d), (-w,h,d), (w,h,d), (w,h,-d),        # top
                     (-w,-h,d), (-w,-h,-d), (w,-h,-d), (w,-h,d),    # bottom
                     (-w,h,d), (-w,-h,d), (w,-h,d), (w,h,d),        # front
                     (w,h,d), (w,-h,d), (w,-h,-d), (w,h,-d),        # right
                     (w,h,-d), (w,-h,-d), (-w,-h,-d), (-w,h,-d),    # back
                     (-w,h,-d), (-w,-h,-d), (-w,-h,d), (-w,h,d) ]   # left
        normals = [ (0,1,0), (0,1,0), (0,1,0), (0,1,0),
                    (0,-1,0), (0,-1,0), (0,-1,0), (0,-1,0),
                    (0,0,1), (0,0,1), (0,0,1), (0,0,1),
                    (1,0,0), (1,0,0), (1,0,0), (1,0,0),
                    (0,0,-1), (0,0,-1), (0,0,-1), (0,0,-1),
                    (-1,0,0), (-1,0,0), (-1,0,0), (-1,0,0) ]
        colorList = None
        texCoords = None
        if self.textureID == 0:
            colorList = []
            for side in range(6):
                colorList.extend([lookupColor3D(colors[side])] * 4)
        else:
            texCoords = [ (0,1), (0,0), (1,0), (1,1) ] * 6
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)
        
    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_QUADS, 0, 24)
        self.countPolygons(6)

#############################################################################

class Lines3D(Shape3D):
    def __init__(self, vertices, color=(1,1,1), width=1):
        Shape3D.__init__(self)
        self.textureID = 0
        self.numVertices = len(vertices)
        self.width = width
        if self.numVertices % 2 == 1:
            raise ValueError, "the number of vertices in your lines must be even"
        #vertices = [ ( float(x1), float(y1), float(z1) ),
        #             ( float(x2), float(y2), float(z2) ) ]
        normals = None
        texCoords = None
        color = lookupColor3D(color)
        colorList = [color] * self.numVertices
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)
        
    def draw(self):
        #self.useTexture()
        glLineWidth(self.width)
        self.buffers.select()
        glDrawArrays(GL_LINES, 0, self.numVertices)
        self.countPolygons(self.numVertices/2)

#############################################################################


##class Triangles3D(Shape3D):
##    def __init__(self, vertices, color=(1,1,1), texCoords=[], texture=None):
##        Shape3D.__init__(self)
##        self.setTexture(texture)
##        self.numVertices = len(vertices)
##        if self.numVertices % 3 == 1:
##            raise ValueError, "the number of vertices in your triangles must be a multiple of 3"
##        normals = []
##        for i in range(0,self.numVertices,3):
##            normals.append(makeNormal(vertices[i], vertices[i+1], vertices[i+2]))
##            normals.append(makeNormal(vertices[i+1], vertices[i+2], vertices[i]))
##            normals.append(makeNormal(vertices[i+2], vertices[i], vertices[i+1]))
##        color = lookupColor3D(color)
##        colorList = [color] * self.numVertices
##        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)
##
##    def draw(self):
##        #self.useTexture()
##        #glLineWidth(self.width)
##        self.buffers.select()
##        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
##        self.countPolygons(self.numVertices/3)

class Terrain3D(Shape3D):
    def __init__(self, heights, cellSize=1, colors=["black","white"], texture=None, textureRepeat=1):
        Shape3D.__init__(self)
        self.heights = heights
        self.size = len(heights) - 1
        self.cellSize = cellSize
        self.textureRepeat = textureRepeat
        self.textureCells = self.size / self.textureRepeat
        self.setTexture(texture)

        vertices = []
        texCoords = []
        for x in range(self.size):
            for z in range(self.size):
                vertices += self.triangle(x,z, x,z+1, x+1,z+1)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,0,z,1), self.tex2(x,1,z,1)]
                vertices += self.triangle(x,z, x+1,z+1, x+1,z)
                if texture is not None:
                    texCoords += [self.tex2(x,0,z,0), self.tex2(x,1,z,1), self.tex2(x,1,z,0)]
        self.numVertices = len(vertices)
        normals = []
        for i in range(0,self.numVertices,3):
            normals.append(self.makeNormal(vertices[i], vertices[i+1], vertices[i+2]))
            normals.append(self.makeNormal(vertices[i+1], vertices[i+2], vertices[i]))
            normals.append(self.makeNormal(vertices[i+2], vertices[i], vertices[i+1]))
        colors = [lookupColor3D(color) for color in colors]
        colors3 = []
        for color in colors:
            colors3 += [color,color,color]
        colorList = colors3 * (self.numVertices/len(colors3) + 1)
        self.buffers = self.Buffers(vertices, normals, colorList, texCoords)

    def draw(self):
        self.useTexture()
        self.buffers.select()
        glDrawArrays(GL_TRIANGLES, 0, self.numVertices)
        self.countPolygons(self.numVertices/3)

    def shift(self, coord):
        return (coord-self.size/2) * self.cellSize
    def triangle(self, x1,z1, x2,z2, x3,z3):
        return [(self.shift(x1), self.heights[x1][z1], self.shift(z1)),
                (self.shift(x2), self.heights[x2][z2], self.shift(z2)),
                (self.shift(x3), self.heights[x3][z3], self.shift(z3))]
    def tex(self, coord, offset):
        coord = (coord + offset) % self.textureCells
        if coord == 0 and offset == 1:
            return 1.0
        else:
            return coord / float(self.textureCells)
    def tex2(self, x,dx,z,dz):
        return (self.tex(x,dx), self.tex(z,dz))

    def makeNormal(self, (x,y,z), (x1,y1,z1), (x2,y2,z2)):
        ax = x1-x
        ay = y1-y
        az = z1-z
        bx = x2-x
        by = y2-y
        bz = z2-z
        cx = ay*bz - az*by
        cy = az*bx - ax*bz
        cz = ax*by - ay*bx
        length = math.sqrt(cx*cx + cy*cy + cz*cz)
        return (cx/length,cy/length,cz/length)
 


#############################################################################

class ColladaModel3D(Shape3D):
    def __init__(self, filename):
        Shape3D.__init__(self)
        self.model = Collada(filename, False)
        self.components = list()
        colorList = None
        for component in self.model.getComponents():
            geometry = component.geometry
            material = component.material
            material.textureID = 0
            if material.texture is not None:
                material.textureID = self.setTexture(material.texture)
            elif material.diffuse is None:
                print "WARNING: no diffuse color or texture"
            component.buffers = self.Buffers(geometry.positions, geometry.normals, None, geometry.texcoords)
            self.components.append(component)
        print "   contains " + str(len(self.components)) + " subcomponents"
        
    
    def draw(self):
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_RESCALE_NORMAL)
        glPushMatrix()
        glRotate(-90,1,0,0)
        for component in self.components:
            geometry = component.geometry
            material = component.material
            self.useTexture(material.textureID)
            if material.diffuse is not None:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, material.diffuse)
            else:
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (1,1,1,1))
            if component.matrices != []:
                glPushMatrix()
                for matrix in component.matrices:
                    glMultTransposeMatrixf(matrix)
            component.buffers.select()
            glDrawArrays(geometry.openGLPrimitive, 0, geometry.getVertexCount())
            if component.matrices != []:
                glPopMatrix()
            self.countPolygons(geometry.getPolygonCount())
        glPopMatrix()
        glDisable(GL_RESCALE_NORMAL)
        glEnable(GL_COLOR_MATERIAL)

###################################################################
# Backward Compatibility

addKeyPressedListener = onKeyPress
addKeyReleasedListener = onKeyRelease
addMousePressedListener = onMousePress
addMouseReleasedListener = onMouseRelease
addWheelForwardListener = onWheelForward
addWheelBackwardListener = onWheelBackward
addMouseMotionListener = onMouseMotion
addGameControllerStickListener = onGameControllerStick
addGameControllerDPadListener = onGameControllerDPad
addGameControllerButtonPressedListener = onGameControllerButtonPress
addGameControllerButtonReleasedListener = onGameControllerButtonRelease
addTimerListener = onTimer
keyPressedNow = isKeyPressed

#############


