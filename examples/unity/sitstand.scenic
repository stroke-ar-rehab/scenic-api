from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
import random


behavior SitStandTrain():
    take SpeakAction("Sit")
    take PlayVideoAction("first.mov")
    take StopAction()
    while True:
        if ego.gameObject.joint_angles:
            if CheckSeated(ego.gameObject.joint_angles.rightKnee, ego.gameObject.joint_angles.leftKnee):
                break
        wait

    take SpeakAction("Stand")
    take PlayVideoAction("first.mov")
    take StopAction()
    while True:
        if ego.gameObject.joint_angles:
            if not CheckSeated(ego.gameObject.joint_angles.rightKnee, ego.gameObject.joint_angles.leftKnee):
                break
        wait

    take DoneAction()
    print("done")

ego = new Scenicavatar at (0,0,0),
    with behavior SitStandTrain()


# record ball.gameObject.object_state as "state"

# record ego.gameObject.joint_angles as "angles"