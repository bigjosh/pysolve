import sys
import os
import re
import copy
import visual
import time

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
boxlist = {}

# build all the boxes initially
for x in range(3):
    for y in range(3):
        for z in range(3):
            boxlist[(x,y,z)] = visual.box(length=.95, height=.95, width=.95,
                                          opacity=0.7, material=visual.materials.wood, pos=(x,y,z), visible = False)
def DrawSSS(sequence):
    global boxlist

    # make all the boxes invisible
    for b in boxlist:
        boxlist[b].visible = False

    # make only the boxes succesfully placed visible
    for xyz in sequence:
        boxlist[xyz].visible = True

    visual.rate(10)


def PlaceNext(idx, sss, last_piece_position, last_piece_entry_face):

    DrawSSS(sequence)
    # are we done, if so declare success
    if idx >= 27:
        print(sequence)
        time.sleep(1)
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



