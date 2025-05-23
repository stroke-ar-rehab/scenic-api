from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
from scenic.core.regions import MeshVolumeRegion
import random

behavior SendText():
    take TextAction("hi")
    # while (distance from cup to target) > 0.5:
    #    print(distance from cup to target)

behavior SendText2():
    take TextAction("hi")

behavior GreetPlayer():
    do Idle() for 2 seconds
    do PlayDialogue("greet_player")


workspace = Workspace(RectangularRegion((0,0,0), 0, 10, 10))
floor = workspace

table = new Table at (0, 0.5, 0), 
    facing directly toward (0,0,0.0), 
    with behavior SendText(), 
    with width 1.8,
    with length 1,
    with height 1.85


#                                   x  y  z       width length
spawnRegion = (RectangularRegion((0.5,0.5,0.5), 0, 0.2, 0.2))

target = new Target on table

# cupPosition = new OrientedPoint on table

cup = new Cup on spawnRegion,
    with width 0.2,
    with length 0.2,
    with height 0.2

assistant = new Avatar at (0, 2.5, 0), facing toward table, with behavior GreetPlayer


# terminate when (distance from cup to target) < 0.5

# terminate after 60 seconds

