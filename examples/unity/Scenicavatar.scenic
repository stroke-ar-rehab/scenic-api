from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
import random


sponge1 = new Sponge at (0, 1, 1),
    facing directly toward (0, 90 ,0)

sponge2 = new Sponge at (0, 1, 2),
    with pitch 0 deg, 
    with yaw 0 deg, 
    with roll -20 deg,

ego = new Scenicavatar at (0,0,0)

# init_right = new Init_hand_r at (0.8, 1, 1)

# init_left = new Init_hand_l at (-0.8, 1, 1)

# init_pos = new Init_object_pos at (0, 0, 1)

# target = new Target_point at (0,1,0)

# ego = new Scenicavatar at (0,0,0),
#     with behavior Train(sponge, init_right, init_left, init_pos, target)


# record ball.gameObject.object_state as "state"

# record ego.gameObject.joint_angles as "angles"