from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
import random

cup = new Cup at (0, 1, 1)

init_right = new Init_hand_r at (0.8, 1, 1)

init_left = new Init_hand_l at (-0.8, 1, 1)

init_pos = new Init_object_pos at (0, 0, 1)

box = new Box at (0,1,0)


behavior ShelfTrain(obj, init_right, init_left, init_pos, box):
    take SpeakAction("Put your hand to the spheres")
    take PlayVideoAction("first.mov")
    take StopAction()
    while True:
        if ego.gameObject.joint_angles:
            if CheckDistance(ego.gameObject.joint_angles.leftPalm, init_left.gameObject.position, 0.05) and CheckDistance(ego.gameObject.joint_angles.rightPalm, init_right.gameObject.position, 0.05):
                break
        wait

    take SpeakAction("Grab the cup")    
    take PlayVideoAction("second.mov")
    take StopAction()
    while True:
        if obj.gameObject.object_state:
            if obj.gameObject.object_state.grabbed:
                break
        wait

    take SpeakAction("Place it into the box")
    take PlayVideoAction("third.mov")
    take StopAction()
    while True:
        if ObjectCollide(box.gameObject.position, obj.gameObject.position):
            break
        wait 
    
    take SpeakAction("Place it back to the original position")
    take PlayVideoAction("fourth.mov")
    take StopAction()
    while True:
        if ObjectCollide(obj.gameObject.position, init_pos.gameObject.position):
            break
        wait

    take DoneAction()
    print("done")


ego = new Scenicavatar at (0,0,0),
    with behavior ShelfTrain(sponge, init_right, init_left, init_pos, target)


# record ball.gameObject.object_state as "state"

# record ego.gameObject.joint_angles as "angles"