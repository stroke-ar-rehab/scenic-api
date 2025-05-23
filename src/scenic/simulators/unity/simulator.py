from scenic.core.simulators import SimulationCreationError, Simulator, Simulation
from scenic.syntax.veneer import verbosePrint
from scenic.simulators.unity import websocket_client
import json
import asyncio
# print('Connecting to Unity Server...')
# msgClient = client.StartMessageServer('127.0.0.1', 5555, 1)10.0.0.113
# while(True):
#     msgClient.step()

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

class UnitySimulator(Simulator):
    def __init__(self, ip=current_ip, port=5555, timeout=10, render=True, timestep=0.1):
        super().__init__()
        verbosePrint('Connecting to Unity Server...')
        self.messageClient = websocket_client.StartMessageServer(ip, port, timestep)
        self.scenario_number = 0
        self.timestep = timestep
        self.simulation = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.messageClient.connect())
    
    def createSimulation(self, scene, *, timestep, **kwargs):
        self.scenario_number += 1
        self.simulation = UnitySimulation(scene, self.messageClient, timestep=self.timestep, **kwargs)
        return self.simulation

    def destroy(self):
        print("Destroying Simulator")
        super().destroy()
        self.loop.run_until_complete(self.messageClient.disconnect())
        self.loop.close()

class UnitySimulation(Simulation):
    def __init__(self, scene, client, *, timestep, **kwargs):
        self.client = client
        super().__init__(scene, timestep=timestep, **kwargs)
        
    def step(self):
        asyncio.get_event_loop().run_until_complete(self.client.step())
        
    def executeActions(self, allActions):
        '''
        Buffers allActions before sending. Sending happens in step:
        getProperties -> Information from unity is parsed / action is picked 
        -> executeActions -> step()
        '''
        super().executeActions(allActions)

    def createObjectInSimulator(self, obj):
        print(f"\t{obj.gameObjectType} spawned at {obj.position}")
        gameObject = self.client.spawnObject(obj, obj.position, obj.orientation)
        obj.gameObject = gameObject
        return gameObject

    def getProperties(self, obj, properties):
        values = self.client.getProperties(obj, properties)
        return values

    def updateObjects(self):
        super().updateObjects()

    def destroy(self):
        print("Destroying Simulation")
        self.forceQuit = True
        self.client.destroy_all()
        self.objects = []
        super().destroy()