"""We need to define things here like positions, players, etc.
This is how scenic actually grabs information.
"""



from scenic.simulators.unity.simulator import UnitySimulator
from scenic.simulators.unity.behaviors import *
from scenic.simulators.unity.client import gameObject
from scenic.core.vectors import Orientation
param unity_map = None

def get_ip_from_json(filepath):
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            ip = data.get("ip", "localhost")  # Default to localhost if not found
            return ip
    except FileNotFoundError:
        print(f"File {filepath} not found, using localhost")
        return "localhost"
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}, using localhost")
        return "localhost"

current_ip = get_ip_from_json("Scenic-main/Scenic/src/scenic/simulators/unity/req.json")

param address = current_ip
param port = 5555
param timeout = 10
param timestep = .1

simulator UnitySimulator(
    ip=globalParameters.address,
    port=int(globalParameters.port),
    timeout=int(globalParameters.timeout),
    render=True,
    timestep=float(globalParameters.timestep)
)
class UnityObject:
    position : (0,0,0)
    isUnityObject : True
    gameObjectType : ""
    yaw : 0 deg
    pitch : 0 deg
    roll : 0 deg
    gameObject : gameObject((0,0,0), Orientation.fromEuler(0,0,0))
    width : 0.0
    length : 0.0
    height : 0.0
    allowCollisions: True


class Scenicavatar(UnityObject):
    gameObjectType: "Scenicavatar"
    width : 0.1
    length : 0.1
    height : 0.1


class Arrow(UnityObject):
    gameObjectType: "a_arrow"
    width : 0.1
    length : 0.1
    height : 0.1

class Circle(UnityObject):
    gameObjectType: "a_circle"
    width : 0.1
    length : 0.1
    height : 0.1

class Square(UnityObject):
    gameObjectType: "a_square"
    width : 0.1
    length : 0.1
    height : 0.1

class Star(UnityObject):
    gameObjectType: "a_star"
    width : 0.1
    length : 0.1
    height : 0.1

class Triangle(UnityObject):
    gameObjectType: "a_triangle"
    width : 0.1
    length : 0.1
    height : 0.1

class X(UnityObject):
    gameObjectType: "a_x"
    width : 0.1
    length : 0.1
    height : 0.1

