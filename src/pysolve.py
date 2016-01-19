import sys
import os
import re
import copy
import visual
import time
import wx

from visual import scene
from visual import vector
from visual import pi
from visual import display

from visual import rotate

from visual import color
from visual import arrow
from visual import sphere
from visual import rate

framesPath = "frames"   # Where to save animation frames

frameCount = 1            # number the frames

# make a subdir for all the animation frames
# yes, this is the best way to do it in python (there is no atomic "make if does not exist")

try: 
    os.makedirs(framesPath)
except OSError:
    if not os.path.isdir(framesPath):
        raise

scene.autoscale = False       # Dont jump in and out durring the animation

scene.userzoom = False
scene.userspin = False

scene.range = vector( 3.8,3.8,3.8 )               # doesn't work unless you explicity set this. Bug?
scene.forward = vector( -0.5,-0.5,-0.75 )

scene.center = vector( 1,1,0)           # cubes are on 0,1,2 grid.

print("pysolve - solve for 3x3 cube 1.00")

# 1 - straight piece
# 2 - corner piece
chain = [1, 1, 2, 2, 2, 1, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1]

# create the corner dictionary
# the key is the entry face
# the value is a list of possible exit faces for a corner piece
C = {}
C[(0,0,1)] =    [(0,1,0),   (1,0,0),    (0,-1,0),   (-1,0,0)]
C[(0,1,0)] =    [(0,0,1),   (1,0,0),    (0,0,-1),   (-1,0,0)]
C[(1,0,0)] =    [(0,0,1),   (0,1,0),    (0,0,-1),   (0,-1,0)]
C[(0,0,-1)] =   [(0,1,0),   (1,0,0),    (0,-1,0),   (-1,0,0)]
C[(0,-1,0)] =   [(0,0,1),   (1,0,0),    (0,0,-1),   (-1,0,0)]
C[(-1,0,0)] =   [(0,0,1),   (0,1,0),    (0,0,-1),   (0,-1,0)]
arrowlist = {}

# build all the arrows initially
for x in range(3):
    for y in range(3):
        for z in range(3):

            # pos specifies the starting point of the arrow, which is in the center of the cube
            arrowlist[(x,y,z)] = visual.arrow( axis=(1,1,1), 
                                          opacity=1.0, material=visual.materials.diffuse, pos=(1-x,1-y,1-z), visible = False)


originSphere = sphere(radius=0.1) # visually mark the begining of the chain with a sphere

# tweak this for how fast your computer is
fps = 60                     ## Frames per second

# tweak this for how fast you want the moves to run 
mps = 5                      ## moves per second


rpm = (fps/mps)             ## Computed rotations per move (higher this is, the smoother the rotation will appear)


winPause= 1                  ## How long in seconds to freeze after solution found
winMoves=127                 ## Number of moves until 1st solution (found emperically by this very program!)


fpw = (winPause*fps)                    ## computed frames per win - how many frames to pause for

fpr = (winMoves*mps) + (winPause*fps)   ## frames per rotation (this computes a value to have the 1st solution land just before the 1st rotation is complete)

rpf = (2.0*pi) / fpr                    ## computed radians per frame


# rotate one step

def showFrame():    
    scene.forward =rotate( scene.forward , angle= rpf, axis=scene.up)
    rate(fps)
                

def DrawSSS(sequence):

    # make all the boxes invisible
    for b in arrowlist:
        arrowlist[b].visible = False

    prev = None  # keep track of previous cube becuase arrows go from middle of one cube to middle of next one
  
    for pos,xyz in enumerate(sequence):

        bcolor =  color.hsv_to_rgb( ( (pos/2.0)/27.0 , 0.85, 0.85 ) )   # nice color space to show progress

        if prev==None:          ## need two boxes to have an arrow

            # Show the starting point with a dot
            originSphere.pos = xyz
            originSphere.color = bcolor 

        else:
                        
            arrowlist[xyz].color = bcolor
 
            (px,py,pz) = prev
            (bx,by,bz) = xyz
            arrowlist[xyz].pos = prev
            arrowlist[xyz].axis = (bx-px, by-py, bz-pz)
            arrowlist[xyz].visible = True
            
        prev=xyz

    for rotationStep in range( rpm ):
        showFrame()
     

def PlaceNext(idx, sss, last_piece_position, last_piece_entry_face):

    DrawSSS(sequence)
    # are we done, if so declare success
    if idx >= 27:
        print(sequence)
        for e in range(fpw):     ## pause a moment for applause!
            showFrame()
        return

    idx += 1

    # need to make a _copy_ of the data structure, not pass by reference
    # we'll pass this copy to the recursively call function
    # making a copy avoids the need to prune blocks away after a failed block placement
    sss1 = copy.deepcopy(sss)

    # iterate over the possible faces of the previous block
    subindex = 0
    for delta in [(0, 0, 1), (0, 1, 0), (1, 0, 0), (0, 0, -1), (0, -1, 0), (-1, 0, 0)]:

        subindex += 1
        # calculate new position
        new_position = tuple(map(lambda x, y: x + y, last_piece_position, delta))
        (x2, y2, z2) = new_position

        # throw away any position not in the cube
        if x2 not in range(3) or y2 not in range(3) or z2 not in range(3):
            continue

        # throw away any potential location already filled
        if sss[x2][y2][z2] > 0:
            continue

        # throw away any location not supported by previous block type
        (x1, y1, z1) = last_piece_position

        # analyze for straight-through pieces
        if sss[x1][y1][z1] == 1:
            # only one possible location for new piece
            # which is directly across from last piece entry face
            new_delta = tuple([foo * -1 for foo in last_piece_entry_face])
            allowed_position = tuple(map(lambda x, y: x + y, last_piece_position, new_delta))
            if new_position != allowed_position:
                continue

        # analyze for corner type pieces
        elif sss[x1][y1][z1] == 2:
            # four possible locations for new piece
            if delta not in C[last_piece_entry_face]:
                continue

        # the new piece position has passed all our rejection tests so
        # put next piece there and keep going
        saved_lpp = last_piece_position
        saved_lpef = last_piece_entry_face

        last_piece_entry_face = tuple(map(lambda x, y: x - y, last_piece_position, (x2, y2, z2)))
        last_piece_position = (x2, y2, z2)  # where is the block
        sss1[x2][y2][z2] = chain[idx-1]
        sequence.append((x2, y2, z2))

        PlaceNext(idx, sss1, last_piece_position, last_piece_entry_face)

        # we returned so it must have failed
        sss1[x2][y2][z2] = 0
        last_piece_position = saved_lpp
        last_piece_entry_face = saved_lpef
        del sequence[len(sequence)-1]

    return


# the main program runs forever
while True:

    # block array states
    # 0 - empty
    # 1-27 the block id in the chain

    # the 3x3x3 cube structure used record if a cell is occupied
    sss = [[[0 for x in range(3)] for x in range(3)] for x in range(3)]

    # sequence maintains an ordered list of tuples representing the XYZ
    # coordinates of the blocks as they are placed
    sequence = []

    # place the first piece
    idx = 1

    # start in one corner at location (0, 0, 0)
    sss[0][0][0] = chain[idx-1]
    last_piece_position = (0, 0, 0)  # where is the block
    last_piece_entry_face = (0, 0, -1)  # where is entry face
    sequence.append((0, 0, 0))

    # get the ball rolling
    PlaceNext(idx, sss, last_piece_position, last_piece_entry_face)



