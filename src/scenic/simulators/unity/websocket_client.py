import asyncio
import websockets
import json
import logging
from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, cast, Callable
from scenic.core.vectors import Vector
from numpy.linalg import norm
from scipy.spatial.transform import Rotation

# Reuse existing data classes from client.py
from .client import (
    UnityVector3, MovementData, JointAngles, AvatarStatus, 
    ObjectState, ScenicPlayer, ScenicObject, TickData, UnityJSON,
    gameObject, Model, SendData
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketUnityClient:
    def __init__(self, ip: str, port: int, timestep: float, timeout: int = 10):
        self.ip = ip
        self.port = port
        self.timestep = timestep
        self.timeout = timeout
        self.timestepNumber = 0
        self.sendData = SendData()
        self.ScenicPlayers = []
        self.ScenicObjects = []
        self.websocket = None
        self.is_connected = False
        self.loop = None

    async def connect(self):
        """Connect to the Unity WebSocket server"""
        uri = f"ws://{self.ip}:{self.port}/scenic"
        try:
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            logger.info(f"Connected to Unity WebSocket server at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Unity WebSocket server: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the Unity WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from Unity WebSocket server")

    async def step(self):
        """Perform a simulation step"""
        if not self.is_connected:
            raise ConnectionError("Not connected to Unity WebSocket server")

        try:
            # Send data to Unity
            out_data = self.json_constructor()
            await self.websocket.send(out_data)
            self.timestepNumber += 1

            # Receive data from Unity
            response = await asyncio.wait_for(self.websocket.recv(), timeout=self.timeout)
            incoming_data = self.json_deconstructor(response)
            self.extractReceivedData(incoming_data)

        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed")
            self.is_connected = False
            raise
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for Unity response")
            raise
        except Exception as e:
            logger.error(f"Error during step: {e}")
            raise

    def json_deconstructor(self, data):
        """Convert JSON string to UnityJSON object"""
        try:
            a = json.loads(data)
            if isinstance(a, dict):
                return UnityJSON.from_dict(a)
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            return ""

    def json_constructor(self):
        """Convert SendData to JSON string"""
        self.sendData.timestepNumber = self.timestepNumber
        data = self.to_json(self.sendData)
        self.sendData.clearControl()
        return data

    def to_json(self, obj):
        """Convert object to JSON string"""
        def defaultMap(x):
            if isinstance(x, Vector):
                return x.coordinates
            elif isinstance(x, list):
                return tuple(x)
            elif hasattr(x, '__dict__'):
                return x.__dict__
            return x
        return json.dumps(obj, default=defaultMap)

    def extractReceivedData(self, data):
        """Process received data from Unity"""
        if isinstance(data, UnityJSON):
            scenic_players = data.tick_data.scenic_player
            scenic_objects = data.tick_data.scenic_object
            destroy_everything = False

            if len(scenic_objects) == len(self.ScenicObjects):
                for i, unity_object in enumerate(scenic_objects):
                    obj = self.ScenicObjects[i]
                    obj.ConvertFromJsonObject(unity_object)

            if len(scenic_players) == len(self.ScenicPlayers):
                for i, unity_player in enumerate(scenic_players):
                    player = self.ScenicPlayers[i]
                    if unity_player.movement_data.stopButton:
                        destroy_everything = True
                    player.ConvertFromJsonPlayer(unity_player)

            if destroy_everything:
                logger.info("Destroying all objects")
                self.destroy_all()

    def spawnObject(self, obj, position, rotation):
        """Spawn an object in Unity"""
        defaultSpawnObjectTypes = [
            "TestScenicObject", "Scenicavatar", "Tennisball",
            # ... (rest of the object types from original client.py)
        ]

        scenicPlayerList = ["Scenicavatar"]

        if obj.gameObjectType in defaultSpawnObjectTypes:
            game_object = gameObject(position, rotation)
            obj.gameObject = game_object
            obj.gameObject.model = Model(1, 1, 1, (255, 255, 0, 1), obj.gameObjectType.capitalize())
            self.sendData.addToQueue(obj.gameObject)
            self.sendData.control, self.sendData.addObject = True, True

            if obj.gameObjectType in scenicPlayerList:
                self.ScenicPlayers.append(game_object)
                game_object.tag = len(self.ScenicPlayers) - 1
            else:
                self.ScenicObjects.append(game_object)
                game_object.tag = len(self.ScenicObjects) - 1

            return game_object

    def destroy_all(self):
        """Destroy all objects in Unity"""
        for p in self.ScenicPlayers:
            if p:
                p.destroyObj()
        for o in self.ScenicObjects:
            if o:
                o.destroyObj()

        self.ScenicPlayers = []
        self.ScenicObjects = []
        self.sendData.clearObjects()
        asyncio.create_task(self.step())
        self.sendData.clearControl()
        asyncio.create_task(self.step())

    def getProperties(self, obj, properties):
        """Get properties of an object from Unity"""
        # Implementation depends on what properties you need to get
        pass

def StartMessageServer(ip, port, timestep):
    """Factory function to create a WebSocketUnityClient instance"""
    return WebSocketUnityClient(ip, port, timestep) 