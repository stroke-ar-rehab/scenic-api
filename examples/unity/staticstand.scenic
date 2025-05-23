from scenic.simulators.unity.actions import *
from scenic.simulators.unity.behaviors import *
model scenic.simulators.unity.model
import trimesh
import random

behavior StaticStandTrain():
    take SpeakAction("Stand")
    take PlayVideoAction("first.mov")
    take StopAction()
    count = 0
    while True:
        if ego.gameObject.joint_angles:
            if not CheckSeated(ego.gameObject.joint_angles.rightKnee, ego.gameObject.joint_angles.leftKnee):
                count += 1
                break
        wait

    take DoneAction()
    print("done", count)

ego = new Scenicavatar at (0,0,0),
    with behavior StaticStandTrain()


# record ball.gameObject.object_state as "state"

# record ego.gameObject.joint_angles as "angles"