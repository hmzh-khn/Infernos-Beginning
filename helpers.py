DIMENSION = 67

# create initial map with heights 0
initialHeights = [[0 for setHeight in range(DIMENSION)] for index in range(DIMENSION)]

# always pass in smalled value first?
def isBoundedBy(currentPos, corner1, corner2, inclusive=True):
	(x1, y1) = corner1
	(x2, y2) = corner2
	(currentX, currentY) = currentPos

	if inclusive:
		return x1 <= currentX <= x2 and y1 <= currentY <= y2
	else:
		return x1 < currentX < x2 and y1 < currentY < y2
		