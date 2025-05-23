import time
from scenic.core.simulators import Action
from scenic.core.vectors import Vector
from scenic.core.object_types import OrientedPoint, Point
from scenic.simulators.unity.client import *
import json
import os
import uuid
import numpy as np
import math
from typing import Any


class SpeakAction(Action):
    """
    Represents an action where an object speaks a given sentence.

    Attributes:
        actionName (str): The name of the action, set to "Speak".
        sentence (str): The sentence that the object will speak.

    Methods:
        applyTo(obj, sim): Applies the speak action to the specified object within the simulation.
    """

    def __init__(self, sentence):
        self.actionName = "Speak"
        self.sentence = sentence

    def applyTo(self, obj, sim):
        obj.gameObject.SpeakAction(self.sentence)


class ShowAction(Action):
    """
    Represents an action to show the appearance of a specified object in the simulation.

    Attributes:
        actionName (str): The name of the action, set to "show".
        objectName (str): The name of the object whose appearance should be shown.

    Methods:
        applyTo(obj, sim): Applies the show action to the specified object within the simulation.
    """

    def __init__(self, objectName):
        self.actionName = "Show"
        self.objectName = objectName

    def applyTo(self, obj, sim):
        obj.gameObject.ShowAction(self.objectName)


class HideAction(Action):
    """
    Represents an action to hide the appearance of a specified object in the simulation.

    Attributes:
        actionName (str): The name of the action, set to "Hide".
        objectName (str): The name of the object whose appearance should be hidden.

    Methods:
        applyTo(obj, sim): Applies the hide action to the specified object within the simulation.
    """

    def __init__(self, objectName):
        self.actionName = "Hide"
        self.objectName = objectName

    def applyTo(self, obj, sim):
        obj.gameObject.HideAction(self.objectName)


class SendImageAndTextRequestAction(Action):
    """
    Represents an action takes an image and text and send to vision language model for analysis.
    You may only call this action on real objects (i.e. Objects that don't appear in setup)
    You may check the results of this action by calling RequestActionResult(ego)

    Attributes:
        actionName (str): The name of the action, set to "SendImageAndTextRequest".
        instruction (str): The instruction text included to the vision language model query.

    Methods:
        applyTo(obj, sim): Applies the SendImageAndTextRequest action to the specified object within the simulation.
    """

    def __init__(self, instruction):
        self.actionName = "SendImageAndTextRequest"
        self.instruction = instruction

    def applyTo(self, obj, sim):
        obj.gameObject.SendImageAndTextRequestAction(self.instruction)


def RequestActionResult(ego):
    """
    Checks whether the SendImageAndTextRequestAction returns positive result.

    Input Arguments:
        1. ego (Unity object): The Unity object representing the avatar.

    Output Arguments:
        bool: True if the task is marked as done in avatar status, False otherwise.
    """
    # print(f"status: {ego.gameObject.avatar_status}")
    if not ego.gameObject.avatar_status:
        print("None")
        return False
    if ego.gameObject.avatar_status.feedback:
        print(ego.gameObject.avatar_status.feedback)
    return ego.gameObject.avatar_status.taskDone


class SnapshotAction(Action):
    """
    Represents an actions of taking a snapshot, sending to Google Cloud, and logging into JSON file

    Attributes:
        caption (str): The state of the exercise at the time of the snapshot. If this action is taken at the beginning of the program, caption = "before". If the action is take at the end of the program, caption = "after".
        logs (dict): dicitonary of logs

    Methods:
        applyTo(obj, sim): uploads the snapshot to google cloud and logs the image id of the snapshot.
    """

    def __init__(self, caption, logs):
        self.caption = caption
        self.logs = logs

    def applyTo(self, obj, sim):
        image_id = str(uuid.uuid4())

        # assign unique id to image
        obj.gameObject.TakeSnapshot(image_id)
        self.logs[str(self.caption)] = image_id
        # os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        # if os.path.exists(self.json_path):
        #     with open(self.json_path, "r") as f:
        #         try:
        #             data = json.load(f)
        #         except json.JSONDecodeError:
        #             return
        # else:
        #     return
        # data[str(self.caption)] = image_id
        # # Write updated log back to file
        # with open(self.json_path, "w") as f:
        #     json.dump(data, f, indent=4)


class PlayVideoAction(Action):
    """
    Represents an action where an object plays a specified video file.

    Attributes:
        actionName (str): The name of the action, set to "PlayVideo".
        fn (str): The filename of the video to be played.

    Methods:
        applyTo(obj, sim): Applies the play video action to the specified object within the simulation.
    """

    def __init__(self, fn):
        self.actionName = "PlayVideo"
        self.fn = fn

    def applyTo(self, obj, sim):
        obj.gameObject.PlayVideoAction(self.fn)


class DoneAction(Action):
    """
    Represents an action that marks an object's exercise is done.

    Attributes:
        actionName (str): The name of the action, set to "Done".

    Methods:
        applyTo(obj, sim): Applies the done action to the specified object within the simulation.
    """

    def __init__(self):
        self.actionName = "Done"

    def applyTo(self, obj, sim):
        obj.gameObject.DoneAction()


class StartRecordingAction(Action):
    def __init__(self):
        self.actionName = "StartRecording"

    def applyTo(self, obj, sim):
        obj.gameObject.StartRecordingAction()


class StopRecordingAction(Action):
    def __init__(self):
        self.actionName = "StopRecording"

    def applyTo(self, obj, sim):
        obj.gameObject.StopRecordingAction()


class RecordVideoAndEvaluateAction(Action):
    """
    Represents an action that triggers video recording and evaluation 
    for an object based on a provided instruction.

    Attributes:
        instruction (str): The instruction used to evaluate the recorded video.
        actionName (str): The name of the action, set to "RecordVideoAndEvaluate".

    Methods:
        applyTo(obj, sim): Applies the action to the specified object in the simulation,
                           invoking the video recording and evaluation routine on the Unity side.
    """

    def __init__(self, instruction):
        self.RecordVideoAndEvaluate = "RecordVideoAndEvaluate"
        self.instruction = instruction

    def applyTo(self, obj, sim):
        obj.gameObject.RecordVideoAndEvaluateAction(self.instruction)


class AskQuestionAction(Action):
    """
    Represents an aciton that ask question and get answer.

    Attributes:
        actionName (str): The name of the action, set to "AskQuestion".
        question (str): The question being asked.

    Methods:
        applyTo(obj, sim): Applies the stop action to the specified object within the simulation.
    """

    def __init__(self, question):
        self.actionName = "AskQuestion"
        self.question = question

    def applyTo(self, obj, sim):
        obj.gameObject.AskQuestionAction(self.question)

class DisposeQueriesAction(Action):
    '''
    Dispose all the Queries running on the bakcground
    
    Attributes:
        actionName (str): The name of the action, set to "DisposeQueries".

    Methods:
        applyTo(obj, sim): Applies the dispsoe queries to the specified object within the simulation.
    '''
    
    def __init__(self):
        self.actionName = "DisposeQueries"
        
    def applyTo(self, obj, sim):
        obj.gameObject.DisposeQueriesAction()


def LogPain(ego, logs):
    '''
    This function will open the file and add ego's status to the json and save it.

    Input Arguments:
        1. ego (Unity Object): contains information about patient status
        2. logs (dict): dictionary where pain, fatigue and dizziness will be stored

    Output Arguments:
        void
    '''
    response = ego.gameObject.avatar_status.pain.split("|")
    body_part, description, scale = "", "", ""
    if len(response) > 2: 
        body_part, description, scale = response
    
    logs["Pain"] = [ego.gameObject.avatar_status.pain != "Not mentioned", body_part.strip(), description.strip(), scale.strip() + "/10"]
    logs["Fatigue"] = [False, ""]
    logs["Dizziness"] = [False, ""]


def PainRecorded(ego):
    """
    Checks if the avatar has reported any pain, fatigue, dizziness, or other symptoms.

    Input Arguments:
        1. ego (object): The ego object containing the avatar's status information, including symptom reports.

    Output Arguments:
        bool: Returns True if pain, fatigue, dizziness, and any other symptom are all recorded as True. Otherwise, returns False.
    """
    if not ego.gameObject.avatar_status:
        return False
    if ego.gameObject.avatar_status.pain and ego.gameObject.avatar_status.fatigue and ego.gameObject.avatar_status.dizziness and ego.gameObject.avatar_status.anything:
        print("Recorded pain")
        return True
    return False

def ThumbsUp(ego):
    """
    Checks whether the avatar is performing a thumbs-up gesture with either hand.

    Input Arguments:
        1. ego (object): The ego object containing the avatar's joint angle data for both hands.

    Output Arguments:
        bool: Returns True if the index, middle, ring, and pinky fingers are flexed (angle > 95 degrees)
              and the thumb is extended (angle < 20 degrees) on either the left or right hand.
              Otherwise, returns False.
    """
    if not ego.gameObject.joint_angles:
        return False
    left_thumb = ego.gameObject.joint_angles.leftThumbCMCFlexion
    left_index = ego.gameObject.joint_angles.leftIndexPIPFlexion
    left_middle = ego.gameObject.joint_angles.leftMiddlePIPFlexion
    left_ring = ego.gameObject.joint_angles.leftRingPIPFlexion
    left_pinky = ego.gameObject.joint_angles.leftPinkyPIPFlexion

    right_thumb = ego.gameObject.joint_angles.rightThumbCMCFlexion
    right_index = ego.gameObject.joint_angles.rightIndexPIPFlexion
    right_middle = ego.gameObject.joint_angles.rightMiddlePIPFlexion
    right_ring = ego.gameObject.joint_angles.rightRingPIPFlexion
    right_pinky = ego.gameObject.joint_angles.rightPinkyPIPFlexion
    return (left_index < 95 and left_middle < 95 and left_ring < 95 and left_pinky < 95 and left_thumb > 120) or (right_index < 95 and right_middle < 95 and right_ring < 95 and right_pinky < 95 and right_thumb > 120)


class CircularTrajectoryCounter:
    """
    This class contains functions to check whether a circular hand motion (e.g. wiping table in a circle)
    is performed with a given repetition. To use this class to check for circular trajectory, create an instance and only call checkCompleted().

    **Sample Scenic Code**
    ctc = CircularTrajectoryCounter()
    while not ctc.checkCompleted(ego, repetition = 3, arm = "Right"):
        wait
    take SpeakAction('Action is performed!')
    """

    def __init__(self, noise_threshold: float = 1e-3, smooth_window: int = 5):
        """
        Parameters:
            noise_threshold (float): Minimum angle change (in radians) to consider (filters out noise)
            smooth_window (int): The window size for the moving average filter
        """
        self.trajectory = []
        self.noise_threshold = noise_threshold
        self.smooth_window = smooth_window

    def smooth_trajectory(self, traj: list[tuple]) -> list[tuple]:
        n = len(traj)
        if n == 0 or n < self.smooth_window:
            return traj  # Not enough points to smooth

        smoothed = []
        half_window = self.smooth_window // 2
        for i in range(n):
            # Determine window boundaries
            start = max(0, i - half_window)
            end = min(n, i + half_window + 1)
            window_points = traj[start:end]
            # Compute element-wise average over the window
            avg_point = tuple(sum(coords) / len(window_points)
                              for coords in zip(*window_points))
            smoothed.append(avg_point)
        return smoothed

    def project_to_plane(self, traj: list[tuple]) -> list[tuple]:
        arr = np.array(traj)  # shape (n, 3)
        # Compute variance for each axis (column)
        variances = np.var(arr, axis=0)
        # Identify the axis with the smallest variance
        drop_index = np.argmin(variances)
        # Remove that axis and return 2D coordinates
        projected = np.delete(arr, drop_index, axis=1)
        return projected.tolist()

    def estimate_center(self, points: list[tuple]) -> tuple:
        if not points:
            return (0, 0)
        xs, ys = zip(*points)
        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)
        return (center_x, center_y)

    def compute_polar_angle(self, point: tuple, center: tuple) -> float:
        # Shift point relative to center
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        return math.atan2(dy, dx)

    def unwrap_angle(self, angle_diff: float) -> float:
        # Ensure the diff is in the range (-pi, pi)
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        return angle_diff

    def count_circles(self) -> int:
        if not self.trajectory or len(self.trajectory) < 10:
            return 0

        # Smooth the trajectory to reduce noise
        # smooth_traj = self.smooth_trajectory(self.trajectory)
        smooth_traj = self.trajectory

        # Project the 3D smoothed trajectory onto a 2D plane
        projected = self.project_to_plane(smooth_traj)

        # Estimate the center of rotation (using the centroid)
        center = self.estimate_center(projected)

        circle_count = 0
        cumulative_angle = 0.0

        # Compute the starting angle (polar coordinate) of the first point
        previous_angle = self.compute_polar_angle(projected[0], center)

        for point in projected[1:]:
            current_angle = self.compute_polar_angle(point, center)
            angle_diff = current_angle - previous_angle

            # Unwrap the angle difference to avoid discontinuity (jump across -pi/pi)
            angle_diff = self.unwrap_angle(angle_diff)

            # Skip small changes to filter out noise
            if abs(angle_diff) < self.noise_threshold:
                previous_angle = current_angle
                continue

            cumulative_angle += angle_diff
            previous_angle = current_angle

            # Count full loops
            if abs(cumulative_angle) >= 2 * math.pi:
                circle_count += 1
                # Subtract a full rotation while preserving the sign of the rotation.
                cumulative_angle -= (2 * math.pi) * \
                    (1 if cumulative_angle > 0 else -1)
        return circle_count

    def checkCompleted(self, ego, repetition: int, arm: str) -> bool:
        """
        Checks whether the required number of repetitions is completed.
        THIS IS THE ONLY FUNCTION YOU SHOULD CALL IN THIS CLASS.

        Input Arguments:
            1. ego (Unity object): contains position of the required hand
            2. repetition (int): number of repetitions required to complete the task
            3. arm (str): Which arm(s) to check. Must be one of:
                - "Left": Check only the left elbow.
                - "Right": Check only the right elbow.

        Output Arguemnts:
            bool: true when the required number of repetitions of circular action is reached, else false.
        """
        if not ego.gameObject.joint_angles:
            return False
        if arm == "Left":
            hand = ego.gameObject.joint_angles.leftPalm
        elif arm == "Right":
            hand = ego.gameObject.joint_angles.rightPalm
        else:
            raise ValueError(f"Invalid arm option: {arm}")
        hand = tuple(hand)
        self.trajectory.append(hand)
        return self.count_circles() >= repetition


class CheckDuration:
    """
    Monitor a named boolean condition over time and report when it has
    held continuously for a specified duration. To use, pass the name of
    a function defined in the same file, then call `checkCompleted()` at
    regular intervals (e.g., every 0.1 seconds).

    **Sample Scenic Code**
    cd = CheckDuration("CheckElbowExtension", 2, ego, "Right")
    while not cd.checkCompleted():
        wait()
    take SpeakAction('Right arm remained straightened for 2 seconds')
    """

    def __init__(self,
                 condition_name: str,
                 duration: int,
                 *args: Any,
                 **kwargs: Any):
        """
        Parameters:
            condition_name (str):
                The name of a function (returning bool) defined in this file.
                This function must check if a physical action is completed.
                CANNOT BE "RequestActionResult", "PainRecorded", "DetectedPain", etc.
            duration (int):
                The required time in seconds that the condition must remain True.
            *args: Any
                Positional arguments to pass to the condition function.
            **kwargs: Any
                Keyword arguments to pass to the condition function.
        """
        # Lookup the function by name in the global namespace
        try:
            func = globals()[condition_name]
        except KeyError:
            raise ValueError(f"No function named '{condition_name}' found in globals()")

        if not callable(func):
            raise ValueError(f"Global '{condition_name}' is not callable")

        self.condition = func
        self.args = args
        self.kwargs = kwargs
        self.duration = duration * 10 # Convert seconds into 0.1-second ticks
        self.count = 0

    def checkCompleted(self) -> bool:
        """
        Checks whether the named condition has been continuously True for
        the required duration. THIS IS THE ONLY FUNCTION YOU SHOULD CALL.

        Returns:
            bool:
                True when the condition has been True for the full duration in ticks,
                False otherwise.
        """
        if self.condition(*self.args, **self.kwargs):

            self.count += 1
            if self.count >= self.duration:
                return True
        else:
            self.count = 0
        return False




def CheckElbowExtension(ego, arm):
    """
    Checks whether the elbow extension angle(s) of the specified arm(s) meet or exceed 165 degrees.
    Called when instructed to staighten arm. (e.g. "Extend your arm", "keep your arm straight")

    Input Arguments:
        1. ego (Unity object): contains the joint angle values
        2. arm (str): Which arm(s) to check. Must be one of:
                   - "Left": Check only the left elbow.
                   - "Right": Check only the right elbow.
                   - "Both": Check both elbows.

    Output Arguments:
        bool: True if the specified arm(s) are extended (i.e., elbow angle ≥ 150 degrees), else False.
    """
    if not ego.gameObject.joint_angles:
        return False
    if arm == "Both":
        return ego.gameObject.joint_angles.leftElbow >= 150 and ego.gameObject.joint_angles.rightElbow >= 150
    elif arm == "Left":
        return ego.gameObject.joint_angles.leftElbow >= 150
    elif arm == "Right":
        return ego.gameObject.joint_angles.rightElbow >= 150
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def CheckElbowBend(ego, arm):
    """
    Checks whether the elbow angle(s) of the specified arm(s) is lower than 90 degrees.
    Called when instructed to bend arm.

    Input Arguments:
        1. ego (Unity object): contains the joint angle values
        2. arm (str): Which arm(s) to check. Must be one of:
                   - "Left": Check only the left elbow.
                   - "Right": Check only the right elbow.
                   - "Both": Check both elbows.

    Output Arguments:
        bool: True if the specified arm(s) are bended (i.e., elbow angle <= 90 degrees), else False.
    """
    if not ego.gameObject.joint_angles:
        return False
    if arm == "Both":
        return ego.gameObject.joint_angles.leftElbow <= 90 and ego.gameObject.joint_angles.rightElbow <= 90
    elif arm == "Left":
        return ego.gameObject.joint_angles.leftElbow <= 90
    elif arm == "Right":
        return ego.gameObject.joint_angles.rightElbow <= 90
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def CheckShoulderFlexion(ego, arm):
    """
    Checks whether the shoulder flexion angle(s) of the specified arm(s) meet or exceed 80 degrees.

    Input Arguments:
        1. ego: contains the joint angle values
        2. arm (str): Specifies which arm(s) to check. Must be one of:
                   - "Left": Check only the left shoulder.
                   - "Right": Check only the right shoulder.
                   - "Both": Check both shoulders.

    Output Arguments:
        bool: True if the specified arm(s) have shoulder flexion ≥ 80 degrees, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    if arm == "Both":
        return ego.gameObject.joint_angles.leftShoulderAbductionFlexion >= 80 and ego.gameObject.joint_angles.rightShoulderAbductionFlexion >= 80
    elif arm == "Left":
        return ego.gameObject.joint_angles.leftShoulderAbductionFlexion >= 80
    elif arm == "Right":
        return ego.gameObject.joint_angles.rightShoulderAbductionFlexion >= 80
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def CheckSeated(ego):
    """
    Checks whether the avatar is seated.

    Input Arguments:
        1. ego: contains the hip flexion value of the avatar.

    Output Arguments:
        bool: True if the hip flexion of the avatar is over 50 degrees, representing sitting, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    return True if ego.gameObject.joint_angles.hipFlexion >= 10 else False


def CheckStanding(ego):
    """
    Checks whether the avatar is standing.

    Input Arguments:
        1. ego: contains the hip flexion value of the avatar.

    Output Arguments:
        bool: True if the hip flexion of the avatar is lower than 10 degrees, representing standing, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    return True if ego.gameObject.joint_angles.hipFlexion < 10 else False


def CheckTrunkFlexed(ego):
    """
    Checks whether the avatar is leaning forward or tilting forward.

    Input Arguments:
        1. ego: contains the trunk tilt value of the avatar.

    Output Arguments:
        bool: True if the trunk tilt of the avatar is over 30 degrees, representing leaning forward, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    print(ego.gameObject.joint_angles.trunkTilt)
    return True if ego.gameObject.joint_angles.trunkTilt >= 30 else False


def TaskIsDone(ego):
    """
    Checks whether the current task has been completed by the avatar.

    Input Arguments:
        1. ego (Unity object): The Unity object representing the avatar.

    Output Arguments:
        bool: True if the task is marked as done in avatar status, False otherwise.
    """
    if not ego.gameObject.avatar_status:
        return False
    return ego.gameObject.avatar_status.taskDone


def CheckTrunkNeutral(ego):
    """
    Checks whether the avatar is trunk neutral (i.e. not leaning or tilting).

    Input Arguments:
        1. ego: contains the trunk tilt value of the avatar.

    Output Arguments:
        bool: True if the trunk tilt of the avatar is lower than 10 degrees, representing sitting up straight, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    return True if ego.gameObject.joint_angles.trunkTilt < 10 else False


def CheckOpenPalm(ego, arm):
    """
    Determines whether the palm on the specified arm(s) is fully open.

    Input Arguments:
        1. ego: contains the finger joint angle values of the avatar.
        2. arm (str): Specifies which arm(s) to check. Must be one of:
                   - "Left": Check only the left hand.
                   - "Right": Check only the right hand.
                   - "Both": Check both hands.

    Output Arguments:
        bool: True if all finger joint values meet criteria, representing a complete open plam, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False

    def is_open(side):
        ja = ego.gameObject.joint_angles
        return (
            getattr(ja, f"{side}ThumbIPFlexion") > 160 and
            getattr(ja, f"{side}ThumbCMCFlexion") > 160 and
            getattr(ja, f"{side}IndexMCPFlexion") > 160 and
            getattr(ja, f"{side}IndexPIPFlexion") > 160 and
            getattr(ja, f"{side}IndexDIPFlexion") > 160 and
            getattr(ja, f"{side}MiddleMCPFlexion") > 160 and
            getattr(ja, f"{side}MiddlePIPFlexion") > 160 and
            getattr(ja, f"{side}MiddleDIPFlexion") > 160 and
            getattr(ja, f"{side}RingMCPFlexion") > 160 and
            getattr(ja, f"{side}RingPIPFlexion") > 160 and
            getattr(ja, f"{side}RingDIPFlexion") > 160 and
            getattr(ja, f"{side}PinkyMCPFlexion") > 160 and
            getattr(ja, f"{side}PinkyPIPFlexion") > 160 and
            getattr(ja, f"{side}PinkyDIPFlexion") > 160
        )
    print(is_open("right"))
    if arm == "Both":
        return is_open("left") and is_open("right")
    elif arm == "Left":
        return is_open("left")
    elif arm == "Right":
        return is_open("right")
    else:
        raise ValueError(f"InvaOpenLid arm option: {arm}")

def CheckWristSupination(ego, arm):
    """
    Determines whether the wrist on the specified arm(s) is fully supinated.

    Input Arguments:
        1. ego: contains the wrist supination angle values of the avatar.
        2. arm (str): Specifies which arm(s) to check. Must be one of:
                   - "Left": Check only the left wrist.
                   - "Right": Check only the right wrist.
                   - "Both": Check both wrists.

    Output Arguments:
        bool: True if the wrist supination angle(s) exceed 35 degrees, representing full supination, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    if arm == "Both":
        return ego.gameObject.joint_angles.leftWristSupination > 35 and ego.gameObject.joint_angles.rightWristSupination > 35
    elif arm == "Left":
        return ego.gameObject.joint_angles.leftWristSupination > 35
    elif arm == "Right":
        return ego.gameObject.joint_angles.rightWristSupination > 35
    else:
        raise ValueError(f"Invalid arm option: {arm}")

def CheckWristPronation(ego, arm):
    """
    Determines whether the wrist on the specified arm(s) is fully pronated,
    based on negative wrist supination angles.

    Input Arguments:
        1. ego: contains the wrist supination angle values of the avatar.
        2. arm (str): Specifies which arm(s) to check. Must be one of:
                   - "Left": Check only the left wrist.
                   - "Right": Check only the right wrist.
                   - "Both": Check both wrists.

    Output Arguments:
        bool: True if the wrist supination angle(s) are less than -35 degrees,
              representing full pronation, otherwise False.
    """
    if not ego.gameObject.joint_angles:
        return False
    if arm == "Both":
        return ego.gameObject.joint_angles.leftWristSupination < -35 and ego.gameObject.joint_angles.rightWristSupination < -35
    elif arm == "Left":
        return ego.gameObject.joint_angles.leftWristSupination < -35
    elif arm == "Right":
        return ego.gameObject.joint_angles.rightWristSupination < -35
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def CheckDistanceBetweenTwoObject(obj1, obj2, distance=0.15):
    """
    Checks if the Euclidean distance between two 3D points is less than a given threshold.
    THIS IS A HELPER FUNCTION AND SHOULD NOT BE CALLED IN SCENIC PROGRAM.

    Input Arguments:
        1. obj1, obj2 (Unity object or Vector): Objects or Position Vectors we will use to check distance
        2. distance (float, optional): The threshold distance to compare against. Its default value is set to 0.15

    Output Arguments:
        bool: True if the distance between obj1 and obj2 is less than the given threshold, False otherwise.
    """

    v1, v2 = None, None

    if isinstance(obj1, Vector):
        v1 = obj1
    else:
        v1 = obj1.gameObject.position

    if isinstance(obj2, Vector):
        v2 = obj2
    else:
        v2 = obj2.gameObject.position

    dis = ((v2[0] - v1[0])**2 + (v2[1] - v1[1])**2 + (v2[2] - v1[2])**2) ** 0.5
    return dis < distance


def AssistOneHandWithOther(ego):
    """
    Checks if the left and right palms of the ego are close enough to assist one hand with the other.

    Input Arguments:
        1. ego (Unity object): The ego object, which contains left and right hand positions (`leftPalm`, `rightPalm`).

    Output Arguments:
        bool: True if the distance between the left and right palms is close enough. False otherwise.
    """

    if not ego.gameObject.joint_angles:
        return False

    v1 = ego.gameObject.joint_angles.leftPalm
    v2 = ego.gameObject.joint_angles.rightPalm

    return CheckDistanceBetweenTwoObject(v1, v2)


def CheckDistanceBetweenHandAndObject(ego, obj, arm):
    """
    Checks if the position of the indicated hand ("Left", "Right", or "Both") of ego is close enough to the position of the given object.
    This is useful when the instruction is "Place your right hand on the circle"

    Input Arguments:
        1. ego (Unity object): The ego object, which contains hand positions (`leftPalm`, `rightPalm`).
        2. obj (Unity object): The object that contains its 3D position
        3. arm (str, optional): arm (str): Specifies which hand(s) to check. Must be one of:
                            - "Left": Check only the left hand.
                            - "Right": Check only the right hand.
                            - "Both": Check both hands.

    Output Arguments:
        bool: True if the distance between the hand and the object is close enough. False otherwise.
    """
    if not ego.gameObject.joint_angles or not obj.gameObject.object_state:
        return False

    if arm == "Both":
        return CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.leftPalm, obj) and CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.rightPalm, obj)
    elif arm == "Left":
        return CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.leftPalm, obj)
    elif arm == "Right":
        return CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.rightPalm, obj)
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def CheckBringRealObjectToMouth(ego, arm):
    """
    Checks whether the given hand is close enough to the ego's mouth, indicating that it has been brought to the mouth.

    Input Arguments:
        1. ego (Unity object): The ego entity containing joint angle data, including the mouth's position and right hand position.
        2. arm (str, optional): arm (str): Specifies which arm(s) to check. Must be one of:
                            - "Left": Check only the left hand.
                            - "Right": Check only the right hand.

    Output Arguments:
        bool: True if the hand is within a threshold distance of the ego's mouth. False otherwise.
    """
    if not ego.gameObject.joint_angles:
        return False

    if arm == "Left":
        return CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.leftPalm, ego.gameObject.joint_angles.mouthPos)
    elif arm == "Right":
        return CheckDistanceBetweenTwoObject(ego.gameObject.joint_angles.rightPalm, ego.gameObject.joint_angles.mouthPos)
    else:
        raise ValueError(f"Invalid arm option: {arm}")


def AvatarMoveOrWalkTowardsSomething(ego, object):
    """
    Evaluates whether the ego successfully walks toward the specified target object.

    Input Arguments:
        1. ego (Unity object): The ego entity containing positional data.
        2. target (Unity object): The target object containing positional data and the ego should walk toward.

    Output Arguments:
        bool: True if the ego reaches the target within the specified distance threshold. False otherwise.
    """
    return CheckDistanceBetweenTwoObject(ego, object, distance=1)


def WaitForIntroduction(ego):
    """
    Waits until the introductory speaking actions are completed.

    Useful to delay further instructions or actions until the avatar
    has completed speaking the initial 3 or 4 intro lines.

    Input Arguments:
        ego (Unity object): The Unity object representing the avatar.

    Output Arguments:
        bool: True if fewer than 4 speaking actions have been completed, False otherwise.
    """
    if not ego.gameObject.avatar_status:
        return False
    return ego.gameObject.avatar_status.speakActionCount < 2


def WaitForSpeakAction(ego, speak_count):
    """
    Waits until the introductory speaking actions are completed.

    Input Arguments:
        ego (Unity object): The Unity object representing the avatar.

    Output Arguments:
        bool: True if fewer than speak_count have been completed, False otherwise.
    """
    if not ego.gameObject.avatar_status:
        return False
    return ego.gameObject.avatar_status.speakActionCount < 2 + speak_count


def UpdateLogs(logs, log_idx, action_api, time_taken, completeness):
    """
    Updates the logs dictionary with the current action details.

    Parameters:
        logs (dict): The dictionary to store action execution details.
        action_api (str): The name or identifier of the action API invoked.
        time_taken (float): The time taken to complete the action (in seconds).
        completeness (float): A score or percentage indicating how fully the action was completed.

    Returns:
        None
    """
    if log_idx not in logs:
        print("Unable to find log index")
        return
    logs = logs[log_idx]

    if "ActionAPI" not in logs:
        print("ActionAPI not in the log")
        return
    if "Time_Taken" not in logs:
        print("Time_Taken not in the log")
        return
    if "Completeness" not in logs:
        print("Completeness not in the log")
        return

    logs["ActionAPI"] = action_api
    logs["Time_Taken"] = time_taken
    logs["Completeness"] = completeness


def DetectedPain(ego):
    """
    Checks whether the avatar is currently indicating pain or requesting the program to stop.

    Args:
        ego: The Unity object representing the avatar.

    Returns:
        bool: True if pain is detected or the stop signal is set, False otherwise.
    """
    return ego.gameObject.avatar_status and ego.gameObject.avatar_status.stopProgram
