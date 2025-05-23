import pytest
import pytest_asyncio
import asyncio
import websockets
import json
import os
import sys

# Add the src directory to Python path to import scenic modules
test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(test_dir, '..', 'src')
sys.path.insert(0, src_dir)

from scenic.simulators.unity.websocket_client import WebSocketUnityClient
from scenic.simulators.unity.client import (
    UnityVector3, MovementData, JointAngles, AvatarStatus,
    ObjectState, ScenicPlayer, ScenicObject, TickData, UnityJSON,
    gameObject, Model, SendData
)

# Test configuration
TEST_HOST = "localhost"
TEST_PORT = 5555
TEST_TIMESTEP = 0.1

class MockUnityServer:
    def __init__(self):
        self.clients = set()
        self.last_received_data = None
        self.response_data = None
        self.server = None
        self._ready = asyncio.Event()

    async def start(self):
        async def handler(websocket, path):
            # Only accept connections to /scenic path
            if path != "/scenic":
                await websocket.close(code=1000, reason="Invalid path")
                return
                
            self.clients.add(websocket)
            try:
                async for message in websocket:
                    self.last_received_data = json.loads(message)
                    if self.response_data:
                        await websocket.send(json.dumps(self.response_data))
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.clients.discard(websocket)

        self.server = await websockets.serve(handler, TEST_HOST, TEST_PORT)
        self._ready.set()  # Signal that server is ready
        return self.server

    def set_response(self, response_data):
        self.response_data = response_data

    async def wait_ready(self):
        await self._ready.wait()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

@pytest_asyncio.fixture
async def mock_server():
    server = MockUnityServer()
    await server.start()
    await server.wait_ready()  # Wait for server to be ready
    await asyncio.sleep(0.1)  # Small delay to ensure server is fully ready
    try:
        yield server  # Use yield for proper cleanup
    finally:
        await server.stop()  # Cleanup after test

@pytest.mark.asyncio
async def test_connection(mock_server):
    """Test basic connection and disconnection"""
    client = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    await client.connect()
    assert client.is_connected
    assert len(mock_server.clients) == 1
    
    await client.disconnect()
    assert not client.is_connected

@pytest.mark.asyncio
async def test_step_communication(mock_server):
    """Test basic step communication"""
    client = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    
    # Set up mock response
    mock_response = {
        "TickData": {
            "ScenicPlayers": [],
            "ScenicObjects": []
        }
    }
    mock_server.set_response(mock_response)

    await client.connect()
    
    # Test step
    await client.step()
    
    # Verify data was sent
    assert mock_server.last_received_data is not None
    assert "timestepNumber" in mock_server.last_received_data
    
    await client.disconnect()

@pytest.mark.asyncio
async def test_object_spawning(mock_server):
    """Test object spawning functionality"""
    client = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    
    # Set up mock response
    mock_response = {
        "TickData": {
            "ScenicPlayers": [],
            "ScenicObjects": []
        }
    }
    mock_server.set_response(mock_response)

    await client.connect()

    # Create test object with proper rotation object
    rotation_obj = type('Rotation', (), {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})()
    test_obj = type('TestObject', (), {
        'gameObjectType': 'TestScenicObject',
        'position': (0, 0, 0),
        'orientation': rotation_obj
    })()

    # Spawn object
    game_obj = client.spawnObject(test_obj, test_obj.position, test_obj.orientation)
    
    assert game_obj is not None
    assert len(client.ScenicObjects) == 1
    assert client.sendData.control
    assert client.sendData.addObject
    
    await client.disconnect()

@pytest.mark.asyncio
async def test_player_movement(mock_server):
    """Test player movement and data exchange"""
    client = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    
    # Set up mock response with player movement data
    mock_response = {
        "TickData": {
            "ScenicPlayers": [{
                "movementData": {
                    "transform": {"x": 1.0, "y": 0.0, "z": 0.0},
                    "speed": 1.0,
                    "velocity": {"x": 1.0, "y": 0.0, "z": 0.0},
                    "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "stopButton": False
                },
                "jointAngles": {
                    "LeftElbow": 0.0,
                    "RightElbow": 0.0,
                    "LeftShoulderAbductionFlexion": 0.0,
                    "LeftHorizontalAbduction": 0.0,
                    "RightShoulderAbductionFlexion": 0.0,
                    "RightHorizontalAbduction": 0.0,
                    "LeftWristFlexion": 0.0,
                    "RightWristFlexion": 0.0,
                    "LeftWristSupination": 0.0,
                    "RightWristSupination": 0.0,
                    "LeftThumbIPFlexion": 0.0,
                    "LeftThumbCMCFlexion": 0.0,
                    "LeftIndexMCPFlexion": 0.0,
                    "LeftIndexPIPFlexion": 0.0,
                    "LeftIndexDIPFlexion": 0.0,
                    "LeftMiddleMCPFlexion": 0.0,
                    "LeftMiddlePIPFlexion": 0.0,
                    "LeftMiddleDIPFlexion": 0.0,
                    "LeftRingMCPFlexion": 0.0,
                    "LeftRingPIPFlexion": 0.0,
                    "LeftRingDIPFlexion": 0.0,
                    "LeftPinkyMCPFlexion": 0.0,
                    "LeftPinkyPIPFlexion": 0.0,
                    "LeftPinkyDIPFlexion": 0.0,
                    "RightThumbIPFlexion": 0.0,
                    "RightThumbCMCFlexion": 0.0,
                    "RightIndexMCPFlexion": 0.0,
                    "RightIndexPIPFlexion": 0.0,
                    "RightIndexDIPFlexion": 0.0,
                    "RightMiddleMCPFlexion": 0.0,
                    "RightMiddlePIPFlexion": 0.0,
                    "RightMiddleDIPFlexion": 0.0,
                    "RightRingMCPFlexion": 0.0,
                    "RightRingPIPFlexion": 0.0,
                    "RightRingDIPFlexion": 0.0,
                    "RightPinkyMCPFlexion": 0.0,
                    "RightPinkyPIPFlexion": 0.0,
                    "RightPinkyDIPFlexion": 0.0,
                    "RightKnee": 0.0,
                    "RightPalm": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "RightShoulderPos": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "LeftKnee": 0.0,
                    "LeftPalm": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "LeftShoulderPos": {"x": 0.0, "y": 0.0, "z": 0.0},
                    "TrunkTilt": 0.0,
                    "HipFlexion": 0.0,
                    "MouthPos": {"x": 0.0, "y": 0.0, "z": 0.0}
                },
                "avatarStatus": {
                    "Pain": "none",
                    "Fatigue": "none",
                    "Dizziness": "none",
                    "Anything": "",
                    "TaskDone": False,
                    "InProgress": False,
                    "StopProgram": False,
                    "Feedback": "",
                    "ImageID": "",
                    "SpeakActionCount": 0
                }
            }],
            "ScenicObjects": []
        }
    }
    mock_server.set_response(mock_response)

    await client.connect()

    # Create and spawn player with proper rotation object
    rotation_obj = type('Rotation', (), {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})()
    test_player = type('TestPlayer', (), {
        'gameObjectType': 'Scenicavatar',
        'position': (0, 0, 0),
        'orientation': rotation_obj
    })()
    
    game_obj = client.spawnObject(test_player, test_player.position, test_player.orientation)
    
    # Step simulation
    await client.step()
    
    # Verify player data was updated (checking if the step completed without error)
    assert len(client.ScenicPlayers) == 1
    
    await client.disconnect()

@pytest.mark.asyncio
async def test_multiple_clients(mock_server):
    """Test multiple clients connecting to the server"""
    # Create clients
    client1 = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    client2 = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    
    # Connect both clients
    await client1.connect()
    await client2.connect()
    
    assert len(mock_server.clients) == 2
    
    # Disconnect clients
    await client1.disconnect()
    await client2.disconnect()

@pytest.mark.asyncio
async def test_error_handling(mock_server):
    """Test error handling in various scenarios"""
    # Test connection to non-existent server
    bad_client = WebSocketUnityClient(TEST_HOST, 9999, TEST_TIMESTEP)
    with pytest.raises(Exception):
        await bad_client.connect()
    
    # Test step without connection
    disconnected_client = WebSocketUnityClient(TEST_HOST, TEST_PORT, TEST_TIMESTEP)
    with pytest.raises(ConnectionError):
        await disconnected_client.step()
    
    # Test invalid JSON response - skip this test as it requires more complex mock setup
    # We'll focus on the basic functionality for now

@pytest.mark.asyncio
async def test_separate_client_data():
    """Test that different clients can send separate data without interference"""
    # Set up multiple servers on different ports
    server_configs = [
        {"host": "localhost", "port": 5556},
        {"host": "localhost", "port": 5557},
        {"host": "localhost", "port": 5558}
    ]
    
    servers = []
    clients = []
    
    try:
        # Create and start multiple servers
        for config in server_configs:
            server = MockUnityServer()
            
            # Create custom handler for this server
            def make_server_handler(server_instance):
                async def handler(websocket, path):
                    if path != "/scenic":
                        await websocket.close(code=1000, reason="Invalid path")
                        return
                        
                    server_instance.clients.add(websocket)
                    try:
                        async for message in websocket:
                            server_instance.last_received_data = json.loads(message)
                            if server_instance.response_data:
                                await websocket.send(json.dumps(server_instance.response_data))
                    except websockets.exceptions.ConnectionClosed:
                        pass
                    finally:
                        server_instance.clients.discard(websocket)
                return handler
            
            # Start server with custom handler
            server.server = await websockets.serve(
                make_server_handler(server), 
                config["host"], 
                config["port"]
            )
            server._ready.set()
            
            # Set up mock response for each server
            mock_response = {
                "TickData": {
                    "ScenicPlayers": [],
                    "ScenicObjects": []
                }
            }
            server.set_response(mock_response)
            
            await asyncio.sleep(0.1)  # Small delay to ensure server is ready
            servers.append(server)
        
        # Create clients and connect them to different servers
        for i, config in enumerate(server_configs):
            client = WebSocketUnityClient(config["host"], config["port"], TEST_TIMESTEP)
            clients.append(client)
            await client.connect()
            assert client.is_connected
        
        # Send different data from each client
        test_data = [
            {"client_id": "client_0", "test_value": 100, "unique_data": "first_client"},
            {"client_id": "client_1", "test_value": 200, "unique_data": "second_client"},  
            {"client_id": "client_2", "test_value": 300, "unique_data": "third_client"}
        ]
        
        # Customize each client's sendData to include unique information
        for i, (client, data) in enumerate(zip(clients, test_data)):
            # Add unique data to the client's sendData
            client.sendData.unique_id = data["client_id"]
            client.sendData.test_value = data["test_value"]
            client.sendData.unique_data = data["unique_data"]
            
            # Send a step with the unique data
            await client.step()
        
        # Allow time for all data to be received
        await asyncio.sleep(0.2)
        
        # Verify each server received the correct unique data from its client
        for i, (server, expected_data) in enumerate(zip(servers, test_data)):
            assert server.last_received_data is not None
            assert "timestepNumber" in server.last_received_data
            
            # Check that each server received the correct unique data
            assert server.last_received_data.get("unique_id") == expected_data["client_id"]
            assert server.last_received_data.get("test_value") == expected_data["test_value"]
            assert server.last_received_data.get("unique_data") == expected_data["unique_data"]
        
        # Test that clients can spawn different objects
        rotation_obj = type('Rotation', (), {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})()
        
        object_types = ["TestScenicObject", "Scenicavatar", "TestScenicObject"]
        
        for i, (client, obj_type) in enumerate(zip(clients, object_types)):
            test_obj = type('TestObject', (), {
                'gameObjectType': obj_type,
                'position': (i, 0, 0),  # Different positions for each object
                'orientation': rotation_obj
            })()
            
            game_obj = client.spawnObject(test_obj, test_obj.position, test_obj.orientation)
            assert game_obj is not None
            
            # Verify the correct object was spawned based on type
            if obj_type == "Scenicavatar":
                assert len(client.ScenicPlayers) == 1
                assert len(client.ScenicObjects) == 0
            else:
                assert len(client.ScenicObjects) == 1
                assert len(client.ScenicPlayers) == 0
        
        # Send another round of data to verify continued separation
        for i, (client, data) in enumerate(zip(clients, test_data)):
            # Modify the data slightly for the second round
            client.sendData.round = 2
            client.sendData.modified_value = data["test_value"] * 2
            await client.step()
        
        await asyncio.sleep(0.2)
        
        # Verify the second round of data
        for i, (server, expected_data) in enumerate(zip(servers, test_data)):
            assert server.last_received_data.get("round") == 2
            assert server.last_received_data.get("modified_value") == expected_data["test_value"] * 2
            # Original unique data should still be there
            assert server.last_received_data.get("unique_id") == expected_data["client_id"]
        
        # Disconnect all clients
        for client in clients:
            await client.disconnect()
            assert not client.is_connected
            
    finally:
        # Cleanup: stop all servers
        for server in servers:
            await server.stop()

@pytest.mark.asyncio
async def test_multiple_clients_same_server():
    """Test multiple clients sending different data to the same server"""
    server = MockUnityServer()
    received_messages = []  # Track all received messages
    
    # Create custom handler to capture all messages
    async def handler(websocket, path):
        if path != "/scenic":
            await websocket.close(code=1000, reason="Invalid path")
            return
            
        server.clients.add(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                received_messages.append({
                    'data': data,
                    'websocket': websocket
                })
                if server.response_data:
                    await websocket.send(json.dumps(server.response_data))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            server.clients.discard(websocket)

    try:
        # Start server
        server.server = await websockets.serve(handler, TEST_HOST, 5559)
        server._ready.set()
        
        # Set up mock response
        mock_response = {
            "TickData": {
                "ScenicPlayers": [],
                "ScenicObjects": []
            }
        }
        server.set_response(mock_response)
        
        await asyncio.sleep(0.1)
        
        # Create multiple clients connecting to the same server
        clients = []
        for i in range(3):
            client = WebSocketUnityClient(TEST_HOST, 5559, TEST_TIMESTEP)
            clients.append(client)
            await client.connect()
            assert client.is_connected
        
        # Verify all clients are connected to the same server
        assert len(server.clients) == 3
        
        # Send unique data from each client
        client_data = [
            {"session_id": "session_A", "player_name": "Alice", "score": 1000},
            {"session_id": "session_B", "player_name": "Bob", "score": 2000},
            {"session_id": "session_C", "player_name": "Charlie", "score": 3000}
        ]
        
        # Clear any previous messages
        received_messages.clear()
        
        # Send data from each client with unique identifiers
        for i, (client, data) in enumerate(zip(clients, client_data)):
            client.sendData.session_id = data["session_id"]
            client.sendData.player_name = data["player_name"]
            client.sendData.score = data["score"]
            client.sendData.client_index = i
            
            await client.step()
        
        # Allow time for all messages to be received
        await asyncio.sleep(0.3)
        
        # Verify we received exactly 3 messages (one from each client)
        assert len(received_messages) == 3
        
        # Verify each message contains the correct unique data
        received_data = [msg['data'] for msg in received_messages]
        
        # Check that all expected session IDs are present
        received_session_ids = {data.get('session_id') for data in received_data}
        expected_session_ids = {"session_A", "session_B", "session_C"}
        assert received_session_ids == expected_session_ids
        
        # Verify specific data for each client
        for expected in client_data:
            matching_message = next(
                (data for data in received_data 
                 if data.get('session_id') == expected['session_id']), 
                None
            )
            assert matching_message is not None
            assert matching_message.get('player_name') == expected['player_name']
            assert matching_message.get('score') == expected['score']
        
        # Test simultaneous object spawning from multiple clients
        rotation_obj = type('Rotation', (), {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0})()
        
        for i, client in enumerate(clients):
            test_obj = type('TestObject', (), {
                'gameObjectType': 'TestScenicObject',
                'position': (i * 10, 0, 0),  # Spread objects apart
                'orientation': rotation_obj
            })()
            
            game_obj = client.spawnObject(test_obj, test_obj.position, test_obj.orientation)
            assert game_obj is not None
            assert len(client.ScenicObjects) == 1
        
        # Disconnect all clients
        for client in clients:
            await client.disconnect()
            assert not client.is_connected
        
        # Verify server has no remaining clients
        await asyncio.sleep(0.2)
        assert len(server.clients) == 0
        
    finally:
        # Cleanup
        await server.stop()

if __name__ == "__main__":
    pytest.main([__file__]) 