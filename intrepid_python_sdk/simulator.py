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
    VEHICLE=4,
    GROUND=5,




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

    async def connect(self):
        await self.__client.connect()
        self.__is_connected = True

    def client(self):
        return self.__client

    async def reset(self):
        await self.__client.rpc(f"session.restart", None)

    async def pause(self):
        pass

    async def stop(self):
        pass

    async def get_vehicles(self)-> list:
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

        return response.data


        # response = await self.__client.rpc('map.find_all',
        #                                    {
        #                                     "groups": ["vehicle"]
        #                                     })
        # vehicles = response.data
        # return vehicles

    async def get_objects(self):
        all_objects = await self.__client.rpc('map.list_objects', None)
        res = {}
        for obj in all_objects.data:
            obj_position = await self.__client.rpc(f"object_{obj}.position", None)
            print(obj_position)
            res["obj_id"] = obj_position
        return res

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

    async def set_goal(self, position: list):
        goal = await self.__client.rpc(f"map.spawn_goal", {"position": {
                                                "x": position[0],
                                                "y": position[1],
                                                "z": position[2]
                                                }})
        return goal



class Entity:
    def __init__(self):
        pass

    async def position(self):
        pass

    async def rotation(self):
        pass

    async def velocity(self):
        pass

    async def set_position(self):
        pass

    async def set_rotation(self):
        pass

    async def despawn(self):
        pass


class Vehicle(Entity):
    def __init__(self, client: SimClient, id: int, entity: str):
        self._id = id
        self._entity = entity
        self._client = client
        assert self._client.__is_connected == True

    async def _state(self) -> dict:
        state = await self.__client.rpc('script.eval', {
            "code": """
                position = sim.object.position(ARGS),
                rotation = sim.object.rotation_angles(ARGS),
                lin_vel = sim.object.linear_velocity(ARGS),
                ang_vel = sim.object.angular_velocity(ARGS),
                accel = sim.object.acceleration(ARGS),
                state = {
                    position=position,
                    rotation=rotation,
                    lin_vel=lin_vel,
                    ang_vel=ang_vel,
                    accel=accel
                }

                return state
            """,
            "args": self._id
        })

        return state.data


    async def position(self):
        state = await self._state()
        return state.get("position", None)

    async def rotation(self):
        state = await self._state()
        return state.get("rotation", None)

    async def linear_velocity(self):
        state = await self._state()
        return state.get("lin_vel", None)

    async def angular_velocity(self):
        state = await self._state()
        return state.get("ang_vel", None)

    async def despawn(self):
        pass
        # Entity.despawn()


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
        print(f"sub: {sub}")
        asyncio.ensure_future(sub.subscribe())

    async def connect(self):
        await self.__sim_client.connect()

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
    def sync(self, control_func):
        self.on_tick = control_func

    async def get_vehicle(self, vehicle_id):
        vehicle = await self.__sim_client.get_vehicles()
        # [v for v in all_vehicles ]
        return vehicle
    """
    Get vehicle infos: id, type, sensors, specs
    """
    async def get_vehicle_info(self, vehicle):
        pass

    """
    Get vehicle position, velocity, rotation
    """
    async def get_vehicle_state(self, vehicle) -> dict:
        res = await self.__sim_client.get_vehicle_state(vehicle)
        return res

    async def get_objects(self):
        res = await self.__sim_client.get_objects()
        return res

    """
    Set goal at position
    Position: [x, y, z] in local coordinates
    """
    async def set_goal(self, position: list):
        goal = await self.__sim_client.set_goal(position)
        return goal

    """
    Spawn vehicle with id, position and rotation
    Position: [x,y,z]
    Rotation: [yz, zx, xy]
    """
    async def spawn_vehicle(self, vehicle_id, position, rotation):
        vehicle = await self.__sim_client.spawn_vehicle(vehicle_id, position, rotation)
        # vehicle = await self.__client.rpc(f"map.spawn_uav", {
        #         "robot_id": vehicle_id,
        #         "position": {"x": position[0], "y": position[1], "z": position[2]},
        #         "rotation": {"yz": rotation[0], "zx": rotation[1], "xy": rotation[2]}
        #     })
        # logger.info(f"Spawned vehicle {vehicle_id} at pos:{position} rot: {rotation}")
        return vehicle

    async def spawn_road(self, src, dest):
        road_block = await self.__sim_client.spawn_road(src, dest)
        return road_block

    async def spawn_entity(self, entity_type: WorldEntity, position, rotation):
        entity = await self.spawn_entity(entity_type, position, rotation)
        return entity

    async def on_tick(self, _tick):
        # implemented by the user
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

