from scenic.simulators.unity.actions import *

# Language: scenic (python)
# This file defines all shared scenic behaviors. In order to use any behavior defined
# here, add "from scenic.simulators.vr.behaviors import *" to the top of the scenic file

# TODO: Fill out behaviors

behavior Train(obj, init_right, init_left, init_pos, target):
    take SpeakAction("Put your hand to the spheres")
    take PlayVideoAction("first.mov")
    take StopAction()
    while True:
        if ObjectWithLeftHand(ego, init_left) and ObjectWithRightHand(ego, init_right):
            break
        wait

    take SpeakAction("Grab the Orange")    
    take PlayVideoAction("second.mov")
    take StopAction()
    while True:
        if ObjectGrasped(obj):
            break
        wait

    take SpeakAction("Place it on the target")
    take PlayVideoAction("third.mov")
    take StopAction()
    while True:
        if ObjectCollide(target, obj):
            break
        wait 
    
    take SpeakAction("Place it back to the original position")
    take PlayVideoAction("fourth.mov")
    take StopAction()
    while True:
        if ObjectCollide(obj, init_pos):
            break
        wait

    take DoneAction()


behavior Idle():
    while True:
        # print(distance from ego to self)
        take IdleAction()

behavior ShootBall(vec : Vector, string : str):
    take ShootAction(vec, string)
    take StopAction()

behavior MoveTo(v):
    dist = 1000
    while not (dist < 0.5):
        take MoveToAction(v)
        dist = distance from self to v


behavior PlayDialogue(string: str):
    take DialogueTrigger(string)