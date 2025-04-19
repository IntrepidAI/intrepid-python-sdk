import asyncio
from centrifuge import Client, SubscriptionEventHandler, PublicationContext
import numpy as np
import logging
import signal
import sys
import time
import math
from typing import List
from enum import Enum

from functools import partial
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorldEntity(Enum):
    OBSTACLE=1,
    VEHICLE=2,
    GOAL=3,
    TERRAIN=4,
    SENSOR=5,

    def to_string(self):
        return self.name.lower()

    def __str__(self):
            return self.to_string()

    def __repr__(self):
        return self.__str__()

class ObstacleType(Enum):
    TREE1=1,
    TREE2=2,
    BUILDING1=3,
    BUILDING2=4,
    BUILDING3=5,
    BUILDING4=6,
    BENCH1=7,
    BENCH2=8,

    def to_string(self):
        return self.name.lower()




class SimClient:
    def __init__(self, host="localhost", port=9120):
        # Instantiate sim client
        self.__host = host
        self.__port = port
        # self.__step_duration = step_duration  # simulation step in microseconds
        self.__client = Client(f"ws://{self.__host}:{self.__port}/connection/websocket")
        logger.info(f"Connected to Intrepid Sim on {self.__host}:{self.__port}")
        # asyncio.ensure_future(self.__client.connect())
        self.__is_connected = False

    def is_connected(self):
        return self.__is_connected

    async def connect(self):
        await self.__client.connect()
        self.__is_connected = True
        logger.info("Connected to simulator")

    async def disconnect(self):
        await self.__client.disconnect()
        self.__is_connected = False
        logger.info("Disconnected to simulator")

    def client(self):
        return self.__client

    async def reset(self):
        await self.__client.rpc(f"session.restart", None)

    async def pause(self):
        await self.__client.rpc(f"session.pause", None)

    async def stop(self):
        await self.__client.rpc(f"session.exit", { "code": 0 })

    async def speedup(self, speed_factor: float):
        await self.__client.rpc(f"session.run", { "speed": speed_factor })

    async def get_vehicles(self):
        response = await self.__client.rpc('script.eval', {
            "code": """
                -- Return all vehicles with vehicle ids attached to them
                function find_vehicles()
                    local result = {}
                    local found = sim.map.find_all({
                        groups = { "vehicle" },
                    })
                    for idx = 1, #found do
                        local vehicle_id = sim.object.get_robot_id(found[idx].entity)
                        table.insert(result, {
                            id = vehicle_id,
                            entity = found[idx].entity,
                        })
                    end
                    return result
                end

                return find_vehicles()
            """
        })
        return [(v["id"], v["entity"]) for v in response.data ]
        # return [ Vehicle(self, v["id"], v["entity"]) for v in response.data ]

    async def get_entities(self):
        response = await self.__client.rpc('script.eval', {
            "code": """
                -- Return all vehicles with vehicle ids attached to them
                function find_vehicles()
                    return sim.map.find_all({
                        groups = { "obstacle", "terrain", "goal" },
                    })
                end

                return find_vehicles()
            """
        })

        return [ (e["entity"], e["group"]) for e in response.data ]

    async def get_vehicle_state(self, vehicle) -> dict:
        state = await self.__client.rpc(f"object_{vehicle}.state", None)
        position = state.data["position"]
        rotation = state.data["rotation"]
        velocity = state.data["lin_vel"]
        res = {}
        res["position"] = position
        res["rotation"] = rotation
        res["velocity"] = velocity
        return res

    async def spawn_uav(self, vehicle_id, position, rotation):
        vehicle = await self.__client.rpc(f"map.spawn_uav", {
                "robot_id": vehicle_id,
                "position": {"x": position[0], "y": position[1], "z": position[2]},
                "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]}
            })
        logger.debug(f"Spawned vehicle (UAV) {vehicle_id} at pos:{position} rot: {rotation}")
        return vehicle_id, vehicle.data

    async def spawn_ugv(self, vehicle_id, position, rotation):
        vehicle = await self.__client.rpc(f"map.spawn_ugv", {
                "robot_id": vehicle_id,
                "position": {"x": position[0], "y": position[1], "z": position[2]},
                "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]}
            })
        logger.debug(f"Spawned vehicle (UGV) {vehicle_id} at pos:{position} rot: {rotation}")
        return vehicle_id, vehicle.data

    async def spawn_road(self, src, dest):
        try:
            await self.__client.rpc(f"map.spawn_road", {
                    "src": {"x": src[0], "y": src[1]},
                    "dst": {"x": dest[0], "y": dest[1]},
                })
        except Exception as e:
            logger.error(f"[spawn_road] RPC call failed: {e}")

    async def spawn_camera(self, position, rotation, size, parent):
        pass
        # camera = await self.__client.rpc(f"map.spawn_camera", {
        #         "robot_id": vehicle_id,
        #         "position": {"x": position[0], "y": position[1], "z": position[2]},
        #         "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]}
        #     })
        # logger.debug(f"Spawned vehicle (UGV) {vehicle_id} at pos:{position} rot: {rotation}")
        # return vehicle_id, vehicle.data

        # let camera_rgb = await client.rpc('map.spawn_camera', {
        #     position: { x: 0, y: 0, z: 0 },
        #     rotation: { yz: 0, zx: 0, xy: 0 },
        #     size: { w: 768, h: 576 },
        #     parent: 'HAAAAAEAAAA=',
        #     fov: Math.PI / 4,
        #     format: 'image/png',
        # })


    # TODO
    async def spawn_entity(self, entity_type: ObstacleType, position, rotation):
        if entity_type == ObstacleType.TREE1:
            tree = await self.__client.rpc(f"map.spawn", {
                "mesh": "trees/tree_a.glb",
                "position": {"x": position[0], "y": position[1]},
                "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]},
                })
            logger.debug(f"Spawned tree block {tree} at pos: {position} rot: {rotation}")
            return tree.data

        elif entity_type == ObstacleType.TREE2:
            tree = await self.__client.rpc(f"map.spawn", {
                "mesh": "trees/tree_b.glb",
                "position": {"x": position[0], "y": position[1]},
                "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]},
                })
            logger.debug(f"Spawned tree block {tree} at pos: {position} rot: {rotation}")
            return tree.data



        # TODO other entities
        else:
            return None

    """
    Return goal entity id
    """
    async def set_goal(self, position: list) -> str:
        goal = await self.__client.rpc(f"map.spawn_goal", {"position": {
                                                "x": position[0],
                                                "y": position[1],
                                                "z": position[2]
                                                }})
        return goal.data



class Entity:
    def __init__(self, client: SimClient, entity: str, group: str):
        assert client.is_connected() == True, "Client is not connected."
        self._entity = entity
        self._group = group
        self._client = client

        if group == "terrain":
            self._entity_type = WorldEntity.TERRAIN
        elif group == "tree":
            self._entity_type = WorldEntity.OBSTACLE
        elif group == "obstacle":
            self._entity_type = WorldEntity.OBSTACLE
        elif group == "vehicle":
            self._entity_type = WorldEntity.VEHICLE
        elif group == "goal":
            self._entity_type = WorldEntity.GOAL
        elif group == "sensor":
            self._entity_type = WorldEntity.SENSOR

    def __repr__(self):
        return f"<Entity entity='{self._entity}' group={self._group}>"

    async def _state(self) -> dict:
        state = await self._client.client().rpc('script.eval', {
            "code": """
                local_position = sim.object.position(ARGS)
                global_position = sim.object.gps_position(ARGS)
                rotation = sim.object.rotation_angles(ARGS)
                lin_vel = sim.object.linear_velocity(ARGS)
                ang_vel = sim.object.angular_velocity(ARGS)
                accel = sim.object.acceleration(ARGS)
                state = {
                    global_position=global_position,
                    local_position=local_position,
                    rotation=rotation,
                    lin_vel=lin_vel,
                    ang_vel=ang_vel,
                    accel=accel,
                }
                return state
            """,
            "args": self._entity
        })

        return state.data

    def entity_type(self) -> WorldEntity:
        return self._entity_type

    async def state(self):
        return await self._state()

    async def local_position(self):
        state = await self._state()
        return state.get("local_position", None)

    async def global_position(self):
        state = await self._state()
        return state.get("global_position", None)

    async def rotation(self):
        state = await self._state()
        return state.get("rotation", None)

    async def set_position(self, x: float, y: float, z: float):
        try:
            await self._client.client().rpc("object_{self._entity}.set_position",
            {
                "x": x,
                "y": y,
                "z": z,
            })
        except:
            print("Cannot set position because TODO")

    async def set_rotation(self, yz: float, zx: float, xy: float):
        try:
            await self._client.client().rpc("object_{self._entity}.set_rotation_angles",
            {
                "yz": yz,
                "zx": zx,
                "xy": xy,
            })
        except:
            print("Cannot set rotation because TODO")

    async def despawn(self):
        try:
            self._client.client().rpc('object_{self._entity}.despawn')
        except:
            print(f"Error despawning entity {self._entity}")

    async def spawn_camera(self, position, rotation, size, fov_degrees=80.0, format="image/tiff", camera_type="rgb") -> "Camera":
        # from intrepid_python_sdk.simulator import Camera

        depth_camera = camera_type == "rgbd"
        camera = await self._client.client().rpc("map.spawn_camera", {
            "position": {"x": position[0], "y": position[1], "z": position[2] },
            "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2] },
            "size": {"w": size[0], "h": size[1]},
            "parent": self._entity,
            "fov": fov_degrees * math.pi / 180,
            "format": format,
            "depth_camera": depth_camera
        })
        return Camera(self._client, camera.data)

    def spawn_abstract_sensor(self, radius: 1.0, groups=None) -> "AbstractSensor":
        return AbstractSensor(self._client, radius, groups)


class AbstractSensor:
    def __init__(self, client: SimClient, radius, groups):
        self._client = client
        self._groups = groups
        self._radius = radius
        self._data = None

    def __repr__(self):
        return f"<AbstractSensor groups={self._groups} radius={self._radius}>"

    def groups(self):
        return self._groups

    def radius(self):
        return self._radius

    def set_data(self, data):
        self._data = data

    async def capture(self) -> List[Entity]:
        surrounding = await self._client.client().rpc("map.intersection_with_sphere", {
                    "center": {"x": 0, "y": 0, "z": 0.0 },
                    "radius": self._radius,
                    "groups": self._groups
        })
        # sensor = AbstractSensor(self._client, self._radius, groups)
        self._data = surrounding.data
        return [Entity(self._client, e["entity"], e["group"]) for e in self._data]


"""
Secondary sensors class (eg. lidar, camera, depth/termal camera, ultrasonic, IR, etc.)
"""
class Sensor(Entity):
    def __init__(self, client: SimClient, entity: str):
        assert client.is_connected() == True, "Cannot instantiate Sensor. Client is not connected"
        super().__init__(client, entity, WorldEntity.SENSOR.to_string())

    def __repr__(self):
        return f"<Sensor id={self._id}, entity='{self._entity}'>"

    def id(self):
        return self._id

    def entity(self):
        return self._entity

    async def state(self):
        return await super().state()

    async def position(self):
        logger.info(f"[Sensor] Getting position for entity {self._entity}")
        return await super().position()

    async def rotation(self):
        logger.info(f"[Sensor] Getting rotation for entity {self._entity}")
        return await super().rotation()

    async def set_position(self, x, y, z):
        return await super().set_position(x, y, z)

    async def set_rotation(self, yz, zx, xy):
        return await super().set_rotation(yz, zx, xy)

class Camera(Sensor):
    def __init__(self, client: SimClient, entity: str):
        super().__init__(client, entity)
        self._resolution_x = 640
        self._resolution_y = 480

    def __repr__(self):
        return f"<Camera entity='{self._entity}', resolution={self._resolution_x}x{self._resolution_y}>"

    def resolution(self):
        return self._resolution_x, self._resolution_y

    async def capture(self):
        image = await self._client.client().rpc(f"object_{self._entity}.request_image", None)
        return image.data

    async def set_position(self, x, y, z):
        return await super().set_position(x, y, z)

    async def set_rotation(self, yz, zx, xy):
        return await super().set_rotation(yz, zx, xy)

class Vehicle(Entity):
    def __init__(self, client: SimClient, id: int, entity: str):
        assert client.is_connected() == True, "Cannot instantiate vehicle. Client is not connected"

        super().__init__(client, entity, None)
        self._id = id

    def __repr__(self):
        return f"<Vehicle id={self._id}, entity='{self._entity}'>"

    def id(self):
        return self._id

    def entity(self):
        return self._entity

    async def state(self):
        return await super().state()

    """
    Get local/global position of vehicle
    """
    async def local_position(self):
        logger.info(f"[Vehicle] Getting local position for entity {self._entity}")
        return await super().local_position()

    async def global_position(self):
            logger.info(f"[Vehicle] Getting global position for entity {self._entity}")
            return await super().global_position()

    async def rotation(self):
        logger.info(f"[Vehicle] Getting position for entity {self._entity}")
        return await super().rotation()

    async def linear_velocity(self):
        state = await self._state()
        return state.get("lin_vel", None)

    async def angular_velocity(self):
        state = await self._state()
        return state.get("ang_vel", None)

    async def acceleration(self):
        state = await self._state()
        return state.get("accel", None)

class Simulator:
    def __init__(self, host="localhost", port=9120, step_duration=1_000):
        # Instantiate sim client
        self.__sim_client = SimClient(host, port)
        self._last_tick_received = -1
        self._user_task = None
        self._dt_ms = step_duration
        self._sim_vehicles = {}  # { int: list }

        class EventHandler(SubscriptionEventHandler):
            async def on_publication(_, ctx: PublicationContext) -> None:
                self._last_tick_received = ctx.pub.data
                self._process_tick(ctx.pub.data)

        sub = self.__sim_client.client().new_subscription('sync', EventHandler())
        logger.debug(f"sub: {sub}")
        asyncio.ensure_future(sub.subscribe())

    async def connect(self):
        await asyncio.wait_for(self.__sim_client.connect(), timeout=10)

    async def disconnect(self):
        await asyncio.wait_for(self.__sim_client.disconnect(), timeout=10)

    def client(self):
        return self.__sim_client

    def set_step_duration(self, duration: int):
        self._dt_ms = duration

    """
    Connect to simulator websocket server
    """
    # async def connect(self):
    #     await self.__client.connect()

    """
    Reset simulator instance
    """
    async def reset(self):
        await self.__sim_client.reset()

    """
    Pause simulator instance
    """
    async def pause(self):
        await self.__sim_client.pause()

    """
    Stop simulator instance
    """
    async def stop(self):
        await self.__sim_client.stop()

    async def speedup(self, speed_factor: float):
        assert speed_factor > 0, "Speed factor must be greater than 0"
        await self.__sim_client.speedup(speed_factor)

    """
    Perform a simulation step for duration (microseconds)
    """
    async def step(self, duration):
        pass

    """
    Subscribe to simulator and receive
    """
    def sync(self, control_func):
        self.on_tick = control_func

    """
    Get all vehicles in simulation instance
    """
    async def get_vehicles(self) -> List[Vehicle]:
        vehicles = await self.__sim_client.get_vehicles()
        return [ Vehicle(self.client(), v_id, v_entity) for (v_id, v_entity) in vehicles ]

    """
    Get single vehicle
    """
    async def get_vehicle(self, vehicle_id: int) -> Vehicle:
        vehicles = await self.get_vehicles()
        for v in vehicles:
            if v.id() == vehicle_id:
                return v
        return None


    async def get_entities(self):
        entities = await self.__sim_client.get_entities()
        return [ Entity(self.client(), e[0], e[1]) for e in entities ]

    """
    Set goal at position
    Position: [x, y, z] in local coordinates
    """
    async def set_goal(self, position: list):
        goal = await self.__sim_client.set_goal(position)
        return Entity(self.client(), goal, "goal")

    """
    Spawn UAV vehicle with id, position and rotation
    Position: [x,y,z]
    Rotation: [yz, zx, xy]
    """
    async def spawn_uav(self, vehicle_id, position, rotation):
        (vehicle_id, vehicle_entity) = await self.__sim_client.spawn_uav(vehicle_id, position, rotation)
        return Vehicle(self.__sim_client, vehicle_id, vehicle_entity)

    """
    Spawn UGV vehicle with id, position and rotation
    Position: [x,y,z]
    Rotation: [yz, zx, xy]
    """
    async def spawn_ugv(self, vehicle_id, position, rotation):
        (vehicle_id, vehicle_entity) = await self.__sim_client.spawn_ugv(vehicle_id, position, rotation)
        return Vehicle(self.__sim_client, vehicle_id, vehicle_entity)

    async def spawn_road(self, src, dest):
        await self.__sim_client.spawn_road(src, dest)

    async def spawn_entity(self, entity_type: ObstacleType, position, rotation):
        entity = await self.__sim_client.spawn_entity(entity_type, position, rotation)
        return Entity(self.__sim_client, entity[0], entity_type.to_string())

    async def spawn_camera(self, position, rotation, size, fov_degrees=80.0, format="image/tiff", camera_type="rgb"):
        depth_camera = camera_type == "rgbd"
        camera = await self._client.client().rpc("map.spawn_camera", {
            "position": {"x": position[0], "y": position[1], "z": position[2] },
            "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2] },
            "size": {"w": size[0], "h": size[1]},
            "parent": None,
            "fov": fov_degrees * math.pi / 180,
            "format": format,
            "depth_camera": depth_camera
        })
        return Camera(self._client.client(), camera.data)

    """
    Callback to be implemented by user within sim sync context
    """
    async def on_tick(self, _tick):
        pass

    def _process_tick(self, tick):
        if self._user_task and self._last_tick_received > 0:
            return # busy

        # send sync
        next_tick = tick + self._dt_ms * 1_000
        sync = self.__sim_client.client().get_subscription('sync')
        asyncio.ensure_future(sync.publish(next_tick))

        def on_task_done(_):
            self._user_task = None
            if self._last_tick_received >= next_tick:
                self._process_tick(next_tick)

        self._user_task = asyncio.ensure_future(self.on_tick(self.__sim_client.client()))
        self._user_task.add_done_callback(on_task_done)

