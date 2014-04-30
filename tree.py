from graphics3d import *

import math
from random import randint
import time
import threading

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
       
