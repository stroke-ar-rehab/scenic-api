from dataclasses import dataclass
import time
from types import MappingProxyType
import zmq
import json
from scenic.core.vectors import Vector
from scenic.core.vectors import Orientation
from numpy.linalg import norm
from typing import Optional, Any, List, TypeVar, Type, cast, Callable
from scipy.spatial.transform import Rotation
import sys
# Language: Python 3
# Holds client information for Scenic Unity communication
# See class gameObject below for adding actions


def StartMessageServer(ip, port, timestep):
    return UnityMessageServer(ip, port, timestep)


class UnityMessageServer:
    def __init__(self, ip, port, timestep, timeout=10):
        self.ip = ip
        self.port = port
        self.timestep = timestep
        self.timeout = timeout
        self.timestepNumber = 0
        self.sendData = SendData()
        self.isClient = True
        self.socket_address = ""
        # TODO: initialize all scenic objects that need to be communicated between Unity and Scenic
        self.ScenicPlayers = []
        self.ScenicObjects = []
        # ----
        self.start()

    def start(self):
        self.context = zmq.Context()
        self.socket_address = "tcp://" + str(self.ip) + ":" + str(self.port)
        if self.isClient:
            self.socket = self.context.socket(zmq.REQ)
            # self.socket.setsockopt(zmq.RCVTIMEO, self.timeout * 100)
            self.socket.setsockopt(zmq.HANDSHAKE_IVL, 0)
            self.socket.connect(self.socket_address)
        else:
            self.socket = self.context.socket(zmq.REP)
            self.socket.setsockopt(zmq.RCVTIMEO, self.timeout * 100)
            self.socket.setsockopt(zmq.HANDSHAKE_IVL, 0)
            self.socket.bind(self.socket_address)
        print("Started Unity messenging client @ " + self.socket_address
              + " at a timestep of " + str(self.timestep))

    def json_deconstructor(self, data):
        a = json.loads(data)
        if type(a) == dict:
            a = unity_json_from_dict(a)
        else:
            a = ""
        return a

    def json_constructor(self):
        self.sendData.timestepNumber = self.timestepNumber
        data = self.to_json(self.sendData)
        self.sendData.clearControl()
        return data

    def to_json(self, obj):
        def defaultMap(x):
            if isinstance(x, Vector):
                return x.coordinates
            elif isinstance(x, list):
                return tuple(x)
            elif isinstance(x, MappingProxyType):
                pass
            else:
                return x.__dict__
        return json.dumps(obj, default=defaultMap)

    def step(self):
        # send this data, then sleep then receive .
        if not self.socket or self.socket.closed:
            print("Error: Attempted to send on a closed or invalid socket.")
            return
        if self.isClient:
            out_data = self.json_constructor()

            try:
                self.socket.send_json(out_data)

            except Exception as e:
                return
            self.timestepNumber += 1
            received = False
            inData = None
            while not received:
                try:
                    inData = self.socket.recv(flags=zmq.NOBLOCK)
                    # print(inData, '\n')
                except zmq.ZMQError:
                    received = False
                else:
                    received = True
            incoming_data = self.json_deconstructor(str(inData, 'utf-8'))
            self.extractReceivedData(incoming_data)
        else:
            # should never enter here in our case
            # since our scenic side is always client and never server
            incoming_data = self.json_deconstructor(
                str(self.socket.recv(), 'utf-8'))
            self.extractReceivedData(incoming_data)
            time.sleep(self.timestep)
            out_data = self.json_constructor()
            self.socket.send_json(out_data)
            self.timestepNumber += 1
        # time.sleep(self.timestep)

    def terminate(self):
        if self.timestepNumber < 2:
            # If we did not find another server and scenic barely simulated
            return
        try:
            # Ensure socket closes immediately
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.disconnect(self.socket_address)
            self.socket.close()  # Explicitly close the socket
            self.context.term()  # Terminate the context
            self.resetData()  # Reset Existing data
            print("Successfully disconnected")
        except zmq.ZMQError as e:
            print(f"Error during socket termination: {e}")

    def destroy_all(self):
        for p in self.ScenicPlayers:
            if p:
                p.destroyObj()
        for o in self.ScenicObjects:
            if o:
                o.destroyObj()

        self.ScenicPlayers = []
        self.ScenicObjects = []
        self.sendData.clearObjects()
        self.step()
        self.sendData.clearControl()
        self.step()
        self.terminate()

    def resetData(self):
        self.timestepNumber = 0
        self.sendData = SendData()

    def reset(self):
        # set control true and reset match
        raise NotImplementedError

    def spawnObject(self, obj, position, rotation):
        defaultSpawnObjectTypes = [
            "TestScenicObject",
            "Scenicavatar",
            "Tennisball",
            "Init_hand_l",
            "Init_hand_r",
            "Init_object_pos",
            "Target_point",
            "Box",
            "Sponge",
            "Toothbrush",
            "Toothpaste",
            "Shelf",
            "Fork",
            "Cup",
            "real_obj_placeholder",
            "semi_tandem_stance_foot_marker",
            "tandem_stance_foot_marker",
            "Dog",
            "Bowl",
            "Kettle",
            "Spoon",
            "Pitcher",
            "Cerealbox",
            "Milkcarton",
            "Teabag",
            "Kibblebox",
            "Scoop",
            "Cabinet",
            "Lotion",
            "Pill",
            "Pill_bottle",
            "Sink",
            "Dish",
            "Dishsoap",
            "Dishrack",
            "a_arrow",
            "a_circle",
            "a_square",
            "a_star",
            "a_triangle",
            "a_x"
        ]

        # Added to Scenic player list
        scenicPlayerList = ["Scenicavatar"]

        if obj.gameObjectType in defaultSpawnObjectTypes:

            game_object = gameObject(position, rotation)
            obj.gameObject = game_object
            obj.gameObject.model = Model(
                1, 1, 1, (255, 255, 0, 1), obj.gameObjectType.capitalize())
            self.sendData.addToQueue(obj.gameObject)
            self.sendData.control, self.sendData.addObject = True, True

            # Adding to Scenic player list of the name is Scenicavatar, else scenic objects
            if obj.gameObjectType in scenicPlayerList:
                self.ScenicPlayers.append(game_object)
                game_object.tag = len(self.ScenicPlayers) - 1
            else:
                self.ScenicObjects.append(game_object)
                game_object.tag = len(self.ScenicObjects) - 1

            return game_object

    def extractReceivedData(self, data):
        if isinstance(data, UnityJSON):
            # TODO: extract the recieved data and convert if needed
            scenic_players = data.tick_data.scenic_player
            scenic_objects = data.tick_data.scenic_object
            destroy_everything = False
            if len(scenic_objects) == len(self.ScenicObjects):
                for i, unity_object in enumerate(scenic_objects):
                    object = self.ScenicObjects[i]
                    object.ConvertFromJsonObject(unity_object)

            if len(scenic_players) == len(self.ScenicPlayers):
                for i, unity_player in enumerate(scenic_players):
                    player = self.ScenicPlayers[i]
                    if unity_player.movement_data.stopButton:
                        destroy_everything = True
                    player.ConvertFromJsonPlayer(unity_player)

            if destroy_everything:
                print("DESTROY")
                # self.destroy_all()

    def setupBasicProperties(self, gameObject, obj, player=False):
        position = gameObject.position
        rotation = gameObject.rotation
        velocity = gameObject.velocity
        angularVelocity = gameObject.angularVelocity
        speed = gameObject.speed
        if rotation[3] == 0:
            yaw, pitch, roll = 0, 0, 0
        else:
            r = Rotation.from_quat(
                [rotation[0], rotation[1], rotation[2], rotation[3]])
            simOrientation = Orientation(r)
            simYaw, simPitch, simRoll = simOrientation.eulerAngles   # global Euler angles
            yaw, pitch, roll = obj.parentOrientation.globalToLocalAngles(
                simYaw, simPitch, simRoll)   # local Euler angles

        if player:
            # print(gameObject.joint_angles.rightPalm,
            #     gameObject.joint_angles.leftPalm)
            values = dict(
                position=position,
                velocity=velocity,
                speed=speed,
                angularSpeed=speed,
                angularVelocity=angularVelocity,
                pitch=pitch,
                roll=roll,
                yaw=yaw,
            )
            return values
        else:
            # print(obj.gameObjectType)
            values = dict(
                position=position,
                velocity=velocity,
                speed=speed,
                angularSpeed=speed,
                angularVelocity=angularVelocity,
                pitch=pitch,
                roll=roll,
                yaw=yaw,
            )
            return values

    def getProperties(self, obj, properties):
        defaultSpawnObjectTypes = [
            "TestScenicObject",
            "Scenicavatar",
            "Tennisball",
        ]

        if len(self.ScenicPlayers) == 0:
            self.terminate()
            sys.exit(1)
            return -1

        scenicPlayerList = ["Scenicavatar"]
        if obj.gameObjectType in scenicPlayerList:
            player = self.ScenicPlayers[int(obj.gameObject.tag)]
            return self.setupBasicProperties(player, obj, player=True)
        else:
            object = self.ScenicObjects[int(obj.gameObject.tag)]
            return self.setupBasicProperties(object, obj, player=False)


class actionParameters:
    intVals: list
    floatVals: list
    stringVals: list
    tupleVals: list
    boolVals: list

    def __init__(self):
        self.intVals = []
        self.floatVals = []
        self.stringVals = []
        self.tupleVals = []
        self.boolVals = []

    def addParameter(self, intVal: int = None, floatVal: float = None, stringVal: str = None, tupleVal: tuple = None, boolVal: bool = None):
        tmpList = []
        tmpList.extend([intVal, floatVal, stringVal, tupleVal, boolVal])
        parameter = [x for x in tmpList if x is not None][0]
        if type(parameter) is int:
            self.intVals.append(parameter)
        elif type(parameter) is float:
            self.floatVals.append(parameter)
        elif type(parameter) is str:
            self.stringVals.append(parameter)
        elif type(parameter) is tuple:
            self.tupleVals.append(parameter)
        elif type(parameter) is bool:
            self.boolVals.append(parameter)

# gameObject class holds information Unity needs to generate all gameObject


class gameObject:
    position: Vector
    rotation: tuple
    stopButton: bool
    # tag is to keep track of the scenic objects spawned
    tag: str
    velocity: Vector
    angularVelocity: Vector
    speed: float
    actionDict: dict
    joint_angles: dict
    object_state: dict
    avatar_status: dict

    def __init__(self, position, rotation):
        self.position = position
        self.rotation = (rotation.x, rotation.y, rotation.z, rotation.w)
        self.velocity = Vector(0, 0, 0)
        self.angularVelocity = Vector(0, 0, 0)
        self.speed = 0.0
        self.tag = ""
        self.actionDict = {}
        self.model = Model()
        self.joint_angles = ()
        self.object_state = {}
        self.avatar_status = {}
        self.stopButton = False

    # fills out the action dict of the gameObject with
    # the action it is currently taking/should take at the current timestep
    def DoAction(self, actionName: str, *args):
        if (actionName == "Idle"):
            # clear action dict
            self.actionDict = {}
        else:
            self.actionDict = {}
            params = actionParameters()
            for i in list(args):
                params.addParameter(i)
            self.actionDict[actionName] = params

    def StopAction(self):
        self.actionDict = {}

    def DoneAction(self):
        self.actionDict = {}

    def DisposeQueriesAction(self):
        self.actionDict = {}
        params = actionParameters()
        self.actionDict["DisposeQueries"] = params
        
    def RecordVideoAndEvaluateAction(self, instruction):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(instruction)
        self.actionDict["RecordVideoAndEvaluate"] = params

    def ShowAction(self, objectName):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(objectName)
        self.actionDict["Show"] = params

    def HideAction(self, objectName):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(objectName)
        self.actionDict["Hide"] = params

    def SendImageAndTextRequestAction(self, instruciton):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(instruciton)
        self.actionDict["SendImageAndTextRequest"] = params

    def TakeSnapshot(self, image_id):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(image_id)
        self.actionDict["TakeSnapshot"] = params

    def ActivateShineAction(self, objectName):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(objectName)
        self.actionDict["ActivateShine"] = params

    def AskQuestionAction(self, question):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(question)
        self.actionDict["AskQuestion"] = params

    def StartRecordingAction(self):
        self.actionDict = {}
        params = actionParameters()
        self.actionDict["StartRecording"] = params

    def StopRecordingAction(self):
        self.actionDict = {}
        params = actionParameters()
        self.actionDict["StopRecording"] = params

    def DeactivateShineAction(self, objectName):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(objectName)
        self.actionDict["DeactivateShine"] = params

    def SpeakAction(self, sentence):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(sentence)
        self.actionDict["Speak"] = params
        print("SPEAK", sentence)

    def PlayVideoAction(self, fn):
        self.actionDict = {}
        params = actionParameters()
        params.addParameter(fn)
        self.actionDict["PlayVideo"] = params
        print(f"Play Video file: {fn}")

    def destroyObj(self):
        print("Destroying object")
        self.destroy = True

    # Utility/Helper Functions
    def toVector3(self, unity_v3):
        return Vector(unity_v3.x, unity_v3.y, unity_v3.z)

    def toQuaternion(self, unity_q):
        return (unity_q.x, unity_q.y, unity_q.z, unity_q.w)

    def ConvertFromJsonPlayer(self, data):

        self.position = self.toVector3(data.movement_data.transform)
        self.velocity = self.toVector3(data.movement_data.velocity)
        self.speed = data.movement_data.speed
        self.rotation = self.toQuaternion(data.movement_data.rotation)
        self.joint_angles = data.joint_angles
        self.stopButton = data.movement_data.stopButton
        self.avatar_status = data.avatar_status

    def ConvertFromJsonObject(self, data):
        self.position = self.toVector3(data.movement_data.transform)
        self.velocity = self.toVector3(data.movement_data.velocity)
        self.speed = data.movement_data.speed
        self.rotation = self.toQuaternion(data.movement_data.rotation)
        self.object_state = data.object_state


# Class Model
class Model:
    length: float
    width: float
    height: float
    color: tuple
    type: str

    def __init__(self, length=0, width=0, height=0, color=(0, 0, 0, 1), type=""):
        self.length = length
        self.width = width
        self.height = height
        self.color = color
        self.type = type


# This are the classes that the json will be inserted into
# We might want to put this into another .py file, or make its definition static

class SendData:
    control: bool
    timestepNumber: int
    objects: list
    spawnQueue: list
    addObject: bool
    destroy: bool

    def __init__(self):
        self.control = False
        self.addObject = False
        self.timestepNumber = 0
        self.destroy = False
        self.objects = []
        self.spawnQueue = []

    def addToQueue(self, player: gameObject):
        self.objects.append(player)
        self.spawnQueue.append(player)

    def clearQueue(self):
        self.spawnQueue = []

    def clearControl(self):
        if self.control:
            self.clearQueue()
            self.control = False
            self.destroy = False
            # self.addToQueue = False

    def clearObjects(self):
        self.control = True
        self.destroy = True
        self.objects = []


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    if x is None or x == "NaN":
        return 0.0

    # print(x, type(x))
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def to_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_int(x: Any) -> int:
    assert isinstance(x, int)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def to_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


@dataclass
class UnityVector3:
    x: float
    y: float
    z: float
    w: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any) -> 'UnityVector3':
        assert isinstance(obj, dict)
        x = from_float(obj.get("x"))
        y = from_float(obj.get("y"))
        z = from_float(obj.get("z"))
        w = from_union([from_float, from_none], obj.get("w"))
        return UnityVector3(x, y, z, w)

    def to_dict(self) -> dict:
        result: dict = {}
        result["x"] = to_float(self.x)
        result["y"] = to_float(self.y)
        result["z"] = to_float(self.z)
        result["w"] = from_union([from_int, from_none], self.w)
        return result


@dataclass
class MovementData:
    # TODO: declare all information of an object in the scene returned to us from Unity
    transform: UnityVector3
    speed: float
    velocity: UnityVector3
    rotation: UnityVector3
    stopButton: bool

    @staticmethod
    def from_dict(obj: Any) -> 'MovementData':
        assert isinstance(obj, dict)
        # TODO: Convert info
        transform = UnityVector3.from_dict(obj.get("transform"))
        speed = from_float(obj.get("speed"))
        velocity = UnityVector3.from_dict(obj.get("velocity"))
        rotation = UnityVector3.from_dict(obj.get("rotation"))
        stopButton = from_bool(obj.get("stopButton"))
        return MovementData(transform, speed, velocity, rotation, stopButton)

    def to_dict(self) -> dict:
        result: dict = {}
        # TODO: Convert info
        result["transform"] = to_class(UnityVector3, self.transform)
        result["speed"] = to_float(self.speed)
        result["velocity"] = to_class(UnityVector3, self.velocity)
        result["rotation"] = to_class(UnityVector3, self.rotation)
        result["stopButton"] = to_bool(self.stopButton)
        return result


def toVector3(unity_v3):
    return Vector(unity_v3.x, unity_v3.y, unity_v3.z)


@dataclass
class JointAngles:
    leftShoulderAbductionFlexion: float
    leftHorizontalAbduction: float

    rightShoulderAbductionFlexion: float
    rightHorizontalAbduction: float

    leftWristFlexion: float
    rightWristFlexion: float

    leftWristSupination: float
    rightWristSupination: float

    leftThumbIPFlexion: float
    leftThumbCMCFlexion: float
    leftIndexMCPFlexion: float
    leftIndexPIPFlexion: float
    leftIndexDIPFlexion: float
    leftMiddleMCPFlexion: float
    leftMiddlePIPFlexion: float
    leftMiddleDIPFlexion: float
    leftRingMCPFlexion: float
    leftRingPIPFlexion: float
    leftRingDIPFlexion: float
    leftPinkyMCPFlexion: float
    leftPinkyPIPFlexion: float
    leftPinkyDIPFlexion: float

    rightThumbIPFlexion: float
    rightThumbCMCFlexion: float
    rightIndexMCPFlexion: float
    rightIndexPIPFlexion: float
    rightIndexDIPFlexion: float
    rightMiddleMCPFlexion: float
    rightMiddlePIPFlexion: float
    rightMiddleDIPFlexion: float
    rightRingMCPFlexion: float
    rightRingPIPFlexion: float
    rightRingDIPFlexion: float
    rightPinkyMCPFlexion: float
    rightPinkyPIPFlexion: float
    rightPinkyDIPFlexion: float

    rightElbow: float
    rightKnee: float
    rightPalm: Vector
    rightShoulderPos: Vector

    leftElbow: float
    leftKnee: float
    leftPalm: Vector
    leftShoulderPos: Vector

    trunkTilt: float

    hipFlexion: float

    mouthPos: Vector

    @staticmethod
    def from_dict(obj: Any) -> 'JointAngles':
        assert isinstance(obj, dict)

        return JointAngles(
            leftElbow=from_float(obj.get("LeftElbow")),
            rightElbow=from_float(obj.get("RightElbow")),

            leftShoulderAbductionFlexion=from_float(
                obj.get("LeftShoulderAbductionFlexion")),
            leftHorizontalAbduction=from_float(
                obj.get("LeftHorizontalAbduction")),

            rightShoulderAbductionFlexion=from_float(
                obj.get("RightShoulderAbductionFlexion")),
            rightHorizontalAbduction=from_float(
                obj.get("RightHorizontalAbduction")),

            leftWristFlexion=from_float(obj.get("LeftWristFlexion")),
            rightWristFlexion=from_float(obj.get("RightWristFlexion")),

            leftWristSupination=from_float(obj.get("LeftWristSupination")),
            rightWristSupination=from_float(obj.get("RightWristSupination")),

            leftThumbIPFlexion=from_float(obj.get("LeftThumbIPFlexion")),
            leftThumbCMCFlexion=from_float(obj.get("LeftThumbCMCFlexion")),
            leftIndexMCPFlexion=from_float(obj.get("LeftIndexMCPFlexion")),
            leftIndexPIPFlexion=from_float(obj.get("LeftIndexPIPFlexion")),
            leftIndexDIPFlexion=from_float(obj.get("LeftIndexDIPFlexion")),
            leftMiddleMCPFlexion=from_float(obj.get("LeftMiddleMCPFlexion")),
            leftMiddlePIPFlexion=from_float(obj.get("LeftMiddlePIPFlexion")),
            leftMiddleDIPFlexion=from_float(obj.get("LeftMiddleDIPFlexion")),
            leftRingMCPFlexion=from_float(obj.get("LeftRingMCPFlexion")),
            leftRingPIPFlexion=from_float(obj.get("LeftRingPIPFlexion")),
            leftRingDIPFlexion=from_float(obj.get("LeftRingDIPFlexion")),
            leftPinkyMCPFlexion=from_float(obj.get("LeftPinkyMCPFlexion")),
            leftPinkyPIPFlexion=from_float(obj.get("LeftPinkyPIPFlexion")),
            leftPinkyDIPFlexion=from_float(obj.get("LeftPinkyDIPFlexion")),

            rightThumbIPFlexion=from_float(obj.get("RightThumbIPFlexion")),
            rightThumbCMCFlexion=from_float(obj.get("RightThumbCMCFlexion")),
            rightIndexMCPFlexion=from_float(obj.get("RightIndexMCPFlexion")),
            rightIndexPIPFlexion=from_float(obj.get("RightIndexPIPFlexion")),
            rightIndexDIPFlexion=from_float(obj.get("RightIndexDIPFlexion")),
            rightMiddleMCPFlexion=from_float(obj.get("RightMiddleMCPFlexion")),
            rightMiddlePIPFlexion=from_float(obj.get("RightMiddlePIPFlexion")),
            rightMiddleDIPFlexion=from_float(obj.get("RightMiddleDIPFlexion")),
            rightRingMCPFlexion=from_float(obj.get("RightRingMCPFlexion")),
            rightRingPIPFlexion=from_float(obj.get("RightRingPIPFlexion")),
            rightRingDIPFlexion=from_float(obj.get("RightRingDIPFlexion")),
            rightPinkyMCPFlexion=from_float(obj.get("RightPinkyMCPFlexion")),
            rightPinkyPIPFlexion=from_float(obj.get("RightPinkyPIPFlexion")),
            rightPinkyDIPFlexion=from_float(obj.get("RightPinkyDIPFlexion")),

            rightKnee=from_float(obj.get("RightKnee")),
            rightPalm=toVector3(UnityVector3.from_dict(obj.get("RightPalm"))),
            rightShoulderPos=toVector3(
                UnityVector3.from_dict(obj.get("RightShoulderPos"))),

            leftKnee=from_float(obj.get("LeftKnee")),
            leftPalm=toVector3(UnityVector3.from_dict(obj.get("LeftPalm"))),
            leftShoulderPos=toVector3(
                UnityVector3.from_dict(obj.get("LeftShoulderPos"))),

            trunkTilt=from_float(obj.get("TrunkTilt")),

            hipFlexion=from_float(obj.get("HipFlexion")),

            mouthPos=toVector3(UnityVector3.from_dict(obj.get("MouthPos")))
        )

    def to_dict(self) -> dict:
        result = {
            "leftElbow": to_float(self.leftElbow),
            "rightElbow": to_float(self.rightElbow),

            "leftShoulderAbductionFlexion": to_float(self.leftShoulderAbductionFlexion),
            "leftHorizontalAbduction": to_float(self.leftHorizontalAbduction),

            "rightShoulderAbductionFlexion": to_float(self.rightShoulderAbductionFlexion),
            "rightHorizontalAbduction": to_float(self.rightHorizontalAbduction),

            "leftWristFlexion": to_float(self.leftWristFlexion),
            "rightWristFlexion": to_float(self.rightWristFlexion),

            "leftWristSupination": to_float(self.leftWristSupination),
            "rightWristSupination": to_float(self.rightWristSupination),

            "leftThumbIPFlexion": to_float(self.leftThumbIPFlexion),
            "leftThumbCMCFlexion": to_float(self.leftThumbCMCFlexion),
            "leftIndexMCPFlexion": to_float(self.leftIndexMCPFlexion),
            "leftIndexPIPFlexion": to_float(self.leftIndexPIPFlexion),
            "leftIndexDIPFlexion": to_float(self.leftIndexDIPFlexion),
            "leftMiddleMCPFlexion": to_float(self.leftMiddleMCPFlexion),
            "leftMiddlePIPFlexion": to_float(self.leftMiddlePIPFlexion),
            "leftMiddleDIPFlexion": to_float(self.leftMiddleDIPFlexion),
            "leftRingMCPFlexion": to_float(self.leftRingMCPFlexion),
            "leftRingPIPFlexion": to_float(self.leftRingPIPFlexion),
            "leftRingDIPFlexion": to_float(self.leftRingDIPFlexion),
            "leftPinkyMCPFlexion": to_float(self.leftPinkyMCPFlexion),
            "leftPinkyPIPFlexion": to_float(self.leftPinkyPIPFlexion),
            "leftPinkyDIPFlexion": to_float(self.leftPinkyDIPFlexion),

            "rightThumbIPFlexion": to_float(self.rightThumbIPFlexion),
            "rightThumbCMCFlexion": to_float(self.rightThumbCMCFlexion),
            "rightIndexMCPFlexion": to_float(self.rightIndexMCPFlexion),
            "rightIndexPIPFlexion": to_float(self.rightIndexPIPFlexion),
            "rightIndexDIPFlexion": to_float(self.rightIndexDIPFlexion),
            "rightMiddleMCPFlexion": to_float(self.rightMiddleMCPFlexion),
            "rightMiddlePIPFlexion": to_float(self.rightMiddlePIPFlexion),
            "rightMiddleDIPFlexion": to_float(self.rightMiddleDIPFlexion),
            "rightRingMCPFlexion": to_float(self.rightRingMCPFlexion),
            "rightRingPIPFlexion": to_float(self.rightRingPIPFlexion),
            "rightRingDIPFlexion": to_float(self.rightRingDIPFlexion),
            "rightPinkyMCPFlexion": to_float(self.rightPinkyMCPFlexion),
            "rightPinkyPIPFlexion": to_float(self.rightPinkyPIPFlexion),
            "rightPinkyDIPFlexion": to_float(self.rightPinkyDIPFlexion),

            "rightKnee": to_float(self.rightKnee),
            "rightPalm": to_class(UnityVector3, self.rightPalm),
            "rightShoulderPos": to_class(UnityVector3, self.rightShoulderPos),

            "leftKnee": to_float(self.leftKnee),
            "leftPalm": to_class(UnityVector3, self.leftPalm),
            "leftShoulderPos": to_class(UnityVector3, self.leftShoulderPos),

            "trunkTilt": to_float(self.trunkTilt),

            "hipFlexion": to_float(self.hipFlexion),

            "mouthPos": to_class(UnityVector3, self.mouthPos)
        }
        return result


@dataclass
class AvatarStatus:
    pain: str
    fatigue: str
    dizziness: str
    anything: str
    taskDone: bool
    inProgress: bool
    stopProgram: bool
    feedback: str
    image_id: str
    speakActionCount: int

    @staticmethod
    def from_dict(obj: Any) -> 'AvatarStatus':
        assert isinstance(obj, dict)
        pain = from_str(obj.get("Pain"))
        speakActionCount = from_int(obj.get("SpeakActionCount"))
        fatigue = from_str(obj.get("Fatigue"))
        dizziness = from_str(obj.get("Dizziness"))
        anything = from_str(obj.get("Anything"))
        taskDone = from_bool(obj.get("TaskDone"))
        inProgress = from_bool(obj.get("InProgress"))
        stopProgram = from_bool(obj.get("StopProgram"))
        feedback = from_str(obj.get("Feedback"))
        image_id = from_str(obj.get("ImageID"))

        return AvatarStatus(
            pain=pain,
            speakActionCount=speakActionCount,
            fatigue=fatigue,
            dizziness=dizziness,
            anything=anything,
            taskDone=taskDone,
            inProgress=inProgress,
            stopProgram=stopProgram,
            feedback=feedback,
            image_id=image_id
        )

    def to_dict(self) -> dict:
        result = {
            "pain": to_str(self.pain),
            "speakActionCount": to_int(self.speakActionCount),
            "fatigue": to_str(self.fatigue),
            "dizziness": to_str(self.dizziness),
            "anything": to_str(self.anything),
            "taskDone": to_bool(self.taskDone),
            "inProgress": to_bool(self.inProgress),
            "stopProgram": to_bool(self.stopProgram),
            "feedback": to_str(self.feedback),
            "image_id": to_str(self.feedback)
        }
        return result


'''
Scenic player class
    To add a new class, add following
        1) add attribute
        2) add a line for initialization in from_dict and to_dict
'''


@dataclass
class ScenicPlayer:
    movement_data: MovementData
    joint_angles: JointAngles
    avatar_status: AvatarStatus

    @staticmethod
    def from_dict(obj: Any) -> 'ScenicPlayer':
        assert isinstance(obj, dict)
        movement_data = MovementData.from_dict(obj.get("movementData"))
        joint_angles = JointAngles.from_dict(obj.get("jointAngles"))
        avatar_status = AvatarStatus.from_dict(obj.get("avatarStatus"))
        return ScenicPlayer(movement_data, joint_angles, avatar_status)

    def to_dict(self) -> dict:
        result: dict = {}
        result["movementData"] = to_class(MovementData, self.movement_data)
        result["jointAngles"] = to_class(JointAngles, self.joint_angles)
        result["avatarStatus"] = to_class(AvatarStatus, self.avatar_status)

        return result


@dataclass
class ObjectState:
    grabbed: bool

    @staticmethod
    def from_dict(obj: Any) -> 'ObjectState':
        assert isinstance(obj, dict)
        grabbed = from_bool(obj.get("Grabbed"))
        return ObjectState(
            grabbed=grabbed
        )

    def to_dict(self) -> dict:
        result = {
            "grabbed": to_bool(self.grabbed)
        }
        return result


# Scenic Object status
@dataclass
class ScenicObject:
    movement_data: MovementData
    object_state: ObjectState

    @staticmethod
    def from_dict(obj: Any) -> 'ScenicObject':
        assert isinstance(obj, dict)
        movement_data = MovementData.from_dict(obj.get("movementData"))
        object_state = ObjectState.from_dict(obj.get("objectState"))
        return ScenicObject(movement_data, object_state)

    def to_dict(self) -> dict:
        result: dict = {}
        result["movementData"] = to_class(MovementData, self.movement_data)
        result["objectStatus"] = to_class(ObjectState, self.object_status)
        return result


@dataclass
class TickData:
    scenic_player: List[ScenicPlayer]
    scenic_object: List[ScenicObject]

    @staticmethod
    def from_dict(obj: Any) -> 'TickData':
        assert isinstance(obj, dict)
        scenic_player = from_list(
            ScenicPlayer.from_dict, obj.get("ScenicPlayers"))
        scenic_object = from_list(
            ScenicObject.from_dict, obj.get("ScenicObjects"))
        return TickData(scenic_player, scenic_object)

    def to_dict(self) -> dict:
        result: dict = {}
        # TODO: Convert objects/object lists
        result["ScenicObjects"] = from_list(
            lambda x: to_class(ScenicPlayer, x), self.scenic_player)
        return result


@dataclass
class UnityJSON:
    tick_data: TickData

    @staticmethod
    def from_dict(obj: Any) -> 'UnityJSON':
        assert isinstance(obj, dict)
        tick_data = TickData.from_dict(obj.get("TickData"))
        return UnityJSON(tick_data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["TickData"] = to_class(TickData, self.tick_data)
        return result


def unity_json_from_dict(s: Any) -> UnityJSON:
    return UnityJSON.from_dict(s)


def unity_json_to_dict(x: UnityJSON) -> Any:
    return to_class(UnityJSON, x)
