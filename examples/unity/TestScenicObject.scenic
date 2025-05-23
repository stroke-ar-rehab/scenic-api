from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
import random

# ego = new Scenicavatar at (0,0,0)

ball = new Tennisball at (0,1,1)

init_right = new Init_hand_r at (0.8, 1, 1)

init_left = new Init_hand_l at (-0.8, 1, 1)

init_pos = new Init_object_pos at (0, 0, 1)

target = new Target_point at (0,1,0)

box = new Box at (0,2,0)
sponge = new Sponge at (0, 3, 0)
tb = new Toothbrush at (0, 4, 0)
tp = new Toothpaste at (0, 5, 0)
sh = new Shelf at (0, -1, 0)
fork = new Fork at (0, -4, 0)
cup = new Cup at (0, -3, 0)

ego = new Scenicavatar at (0,0,0)

