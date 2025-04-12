import asyncio
from centrifuge import Client, SubscriptionEventHandler, PublicationContext
import numpy as np
import logging
import signal
import sys
import time
from functools import partial
import logging
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorldEntity(Enum):
    TREE=1,
    BUILDING=2,
    BENCH=3,




class Simulator:
    def __init__(self, host="localhost", port=9120, step_duration=1_000_000):
        # Instantiate sim client
        self.__host = host
        self.__port = port
        self.__step_duration = step_duration  # simulation step in microseconds
        self.__client = Client(f"ws://{self.__host}:{self.__port}/connection/websocket")
        logger.info(f"Connected to Intrepid Sim on {self.__host}:{self.__port}")

    def client(self):
        return self.__client

    def set_step_duration(self, duration: int):
        self.__step_duration = duration

    """
    Connect to simulator websocket server
    """
    async def connect(self):
        await self.__client.connect()

    """
    Reset simulator instance
    """
    async def reset(self):
        await self.__client.rpc(f"session.restart", None)

    async def pause(self):
        pass

    async def stop(self):
        pass

    """
    Perform a simulation step for duration (microseconds)
    """
    async def step(self, duration):
        pass

    """
    Subscribe to simulator and receive
    """
    async def sync(self, control_func, *args, **kwargs):
        self.__event_handler = Simulator.__EventHandler(control_func, *args, **kwargs)
        print("setup event handler")

        sub = self.__client.new_subscription('sync', self.__event_handler)
        print(f"sub: {sub}")
        await sub.subscribe()


    async def get_vehicle(self, agent_id):
        response = await self.__client.rpc('map.list_vehicles', None)
        vehicles = response.data
        vehicle = next((v for v in vehicles if vehicles[v]['robot_id'] == agent_id), None)
        if not vehicle:
            logger.error("No vehicle found. Are you sure agent_id exists?")
            return None
        return vehicle

    """
    Get vehicle infos: id, type, sensors, specs
    """
    async def get_vehicle_info(self, vehicle):
        pass

    """
    Get vehicle position and velocity
    """
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

    async def get_objects(self):
        all_objects = await self.__client.rpc('map.list_objects', None)
        res = {}
        # print(all_buildings)
        for obj in all_objects.data:
            obj_position = await self.__client.rpc(f"object_{obj}.position", None)
            print(obj_position)
            res["obj_id"] = obj_position
        return res

    """
    Set goal at position
    Position: [x, y, z] in local coordinates
    """
    async def set_goal(self, position: list):
        goal = await self.__client.rpc(f"map.spawn_goal", {"position": {
                                                "x": position[0],
                                                "y": position[1],
                                                "z": position[2]
                                                }})
        return goal

    """
    Spawn vehicle with id, position and rotation
    Position: [x,y,z]
    Rotation: [yz, zx, xy]
    """
    async def spawn_vehicle(self, vehicle_id, position, rotation):
        vehicle = await self.__client.rpc(f"map.spawn_uav", {
                "robot_id": vehicle_id,
                "position": {"x": position[0], "y": position[1], "z": position[2]},
                "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]}
            })
        logger.info(f"Spawned vehicle {vehicle_id} at pos:{position} rot: {rotation}")
        return vehicle

    async def spawn_road(self, src, dest):
        road_block = await self.__client.rpc(f"map.spawn_road", {
                "src": {"x": src[0], "y": src[1]},
                "dst": {"x": dest[0], "y": dest[1]},
            })
        logger.info(f"Spawned road block {road_block} from {src} to {dest}")
        return road_block

    async def spawn_entity(self, entity_type: WorldEntity, position, rotation):
        if entity_type == WorldEntity.TREE:
            tree = await self.__client.rpc(f"map.spawn", {
                "mesh": "trees/tree_a.glb",
                "position": {"x": position[0], "y": position[1]},
                "rotation": {"yx": rotation[0], "zx": rotation[1], "xy": rotation[2]},
                })
            logger.info(f"Spawned tree block {tree} at pos: {position} rot: {rotation}")
            return tree
        # TODO other entities
        else:
            return None

    class __EventHandler(SubscriptionEventHandler):
        def __init__(self, control_func, *args, **kwargs):
            self.user_func = control_func
            self.args = args
            self.kwargs = kwargs

        async def on_publication(self, ctx: PublicationContext) -> None:
            ts = ctx.pub.data
            print(f"on_publication: ts {ts}")
            args = list(self.args)
            args.insert(1, ts)  # Assuming the user_func expects: client, ts, every_microsec
            print(f"args: {args}")
            # task = partial(self.user_func, *args, **self.kwargs)
            # task = self.user_func(*self.args, **self.kwargs)
            # Pass `ts` or other dynamic args by adding them here
            # task = partial(self.user_func, ts=ts, *self.args, **self.kwargs)
            # asyncio.ensure_future(task())
            asyncio.ensure_future(self.user_func(*self.args, **self.kwargs))
