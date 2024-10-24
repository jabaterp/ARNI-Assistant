squareLength = 14.2875
squareSeparation = 1.5875

offsetBase = 3.175 #height from base to top of board
offsetFront = 77.7875 #distance from bottom of board to center of base
boardEdge = 42.8625 #distance from last square to end of table (MM)
shortestPieceHeight = 15.875
heightAbove = 38
boardLocs = []
joints = []
squareSpacialLocs = {}
baseAngle = 0
#INITIAL POSITION (0,0) is between (0,3) and (0,4)

#Joint heights from base to top
jointHeights = [40, 65, 74, 66.5]

class joint:
    height
    currHeight
    angle
    initHeight
    initAngle

    def __init__(self, height, angle, initHeight, initAngle, currHeight):
        self.height = height
        self.angle = angle
        self.initHeight = initHeight
        self.initAngle = initAngle
        self.currHeight = currHeight


class square:
    boardPosX
    boardPosY
    spacialX
    spacialY

    angles = [] #Base up to top
    hoverAngles = [] # angles at first position before grab

    def __init__(self, bpx, bpy, sx,sy):
        self.boardPosX = bpx
        self.boardPosY = bpy
        self.spacialX = sx
        self.spacialY = sy

#(0,0) is bottom left square of chess board in relation to robot
def initBoard():
    x = 0
    y = 0
    while x < 8
        boardLocs.push([])
        while y < 8
            sx = ((x+1)-4.5)*squareLength + squareSeparation*(x+1)
            sy = (y+1)*squareLength + squareSeparation*(y+1)
            curr = square(x,y,sx, sy)
            boardLocs[x].push(curr)
            code = sx+":"+sy+":"+heightAbove+":A"
            code2 = sx+":"+sy+":"+heightAbove+":B"
            squareSpacialLocs[code] = curr
            squareSpacialLocs[code2] = curr
            y+=1
        y= 0
        x+=1


def initJoints():
    baseAngle = 0
    baseHeight = 0
    for height in jointHeights
        joint = joint(height, 0, baseHeight, 0, currHeight+height)
        joints.push(joint)
        baseHeight += height


def record(x, y, z):


def calcArmPositions():
    #robotY = y+offsetFront
    #baseAngle = (180/math.pi)*(math.atan(x/robotY))
    #robotZ = z+offsetBase

    thirdJoint =0
    secJoint=0
    secHeight = joints[1].height
    thirdHeight = joints[2].height
    while secJoint < 180
        while thirdJoint < 180
            x = secHeight*math.sin(secJoint)
            angledX = x*sin(baseAngle)
            y = secHeight*math.cos(secJoint)

            thirdJoint+=1

        secJoint+=1


def calcJoint(joint):
    height = initHeight + joint.height*math.cos(angle+initAngle)
    joint.currHeight = height


def rotateJoint(jointNum):




