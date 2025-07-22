import asyncio
import math
import random
from typing import List
from functools import partial

# from centrifuge import Client, PublicationContext, SubscriptionEventHandler
# from pseudo_glam.vec3 import Vec3
# from pseudo_glam.quat import Quat
from intrepid_python_sdk.simulator import Simulator, \
    WorldEntity, Position, \
    Rotation, Vehicle, Entity, Camera, ObstacleType

from intrepid_python_sdk.pseudo_glam.vec3 import Vec3
from intrepid_python_sdk.pseudo_glam.quat import Quat


TIMESTEP_MS = 100
SHIELD_RADIUS = 10
TERMINAL_PHASE_THR = 3
NUM_DEFENDERS = 4
NUM_ATTACKERS = 1
DEFENDER_SPREAD = 5
ATTACKER_ID = 99


class WorldControllerBase:
    def __init__(self):
        client = Client('ws://localhost:9120/connection/websocket')

        class EventHandler(SubscriptionEventHandler):
            async def on_publication(_, ctx: PublicationContext) -> None:
                print(f"tick {ctx.pub.data}")
                self._last_tick_received = ctx.pub.data
                self._process_tick(ctx.pub.data)

        sync = client.new_subscription('sync', EventHandler())
        asyncio.ensure_future(sync.subscribe())

        self.client = client
        self._dt_ms = TIMESTEP_MS
        self._last_tick_received = -1
        self._user_task = None

        fut = asyncio.ensure_future(client.connect())
        fut.add_done_callback(lambda _: asyncio.ensure_future(self.on_start()))

    async def on_start(self):
        # implemented by the user
        pass

    async def on_tick(self, _tick):
        # implemented by the user
        pass

    async def rpc(self, method: str, args = None):
        result = await self.client.rpc(method, args)
        return result.data

    def _process_tick(self, tick):
        if self._user_task and self._last_tick_received > 0:
            return # busy

        # send sync
        next_tick = tick + self._dt_ms * 1_000
        sync = self.client.get_subscription('sync')
        asyncio.ensure_future(sync.publish(next_tick))
        # print(f"send sync {next_tick}")

        def on_task_done(_):
            self._user_task = None
            if self._last_tick_received >= next_tick:
                self._process_tick(next_tick)

        self._user_task = asyncio.ensure_future(self.on_tick(tick))
        self._user_task.add_done_callback(on_task_done)

class WorldController(WorldControllerBase):
    async def on_start(self):
        self._robots = []
        self._last_idx = 0
        await self.rpc('session.restart')

        commands = []

        attacker = AttackerVehicleController(ATTACKER_ID)
        self._robots.append(attacker)
        await attacker.spawn(self)

        # hvt_entity = await self.rpc('map.spawn_goal', {
        #     'position': Vec3(0, 0, 10).to_dict(),
        # })

        hvt_entity = await self.rpc('map.spawn_gltf', {
            'mesh': 'https://ams1.vultrobjects.com/assets-sim/assets_v1/military/96L6.glb',
            'position': Vec3(20, 0, 0).to_dict(),
            'rotation': {'xy': math.pi / 6},
        })


        await self.create_defender(attacker.entity, hvt_entity, 0, 0)

        for i in range(NUM_DEFENDERS):
            await self.create_defender(attacker.entity,
                                       hvt_entity,
                                       DEFENDER_SPREAD,
                                       i * 2 * math.pi / NUM_DEFENDERS)

        # for i in range(18):
        #     await self.create_defender(attacker.entity, hvt_entity, 3, i * 2 * math.pi / 18)

        commands.append(self.rpc('session.run'))
        await asyncio.gather(*commands)

    async def create_defender(
        self,
        attacker_entity,
        hvt_entity,
        formation_distance,
        formation_angle,
    ):
        idx = self._last_idx + 1
        self._last_idx = idx
        robot = DefenderVehicleController(
            idx,
            attacker_entity,
            hvt_entity,
            formation_distance,
            formation_angle,
        )
        self._robots.append(robot)
        await robot.spawn(self)

    async def on_tick(self, _tick):
        commands = []
        for robot in self._robots:
            commands.append(robot.control(self))
        await asyncio.gather(*commands)

        for robot in self._robots:
            if robot.error is not None:
                await robot.despawn(self)
                self._robots.remove(robot)

class AttackerVehicleController:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.entity = None
        self.error = None

    async def spawn(self, world):
        self.entity = await world.rpc('map.spawn_drone', {
            'model': 'f450_pid',
            'robot_id': self.robot_id,
            'position': Vec3(-20, 0, 0).to_dict(),
        })

    async def despawn(self, world):
        if self.entity is not None:
            try:
                await world.rpc(f'object_{self.entity}.despawn')
            except:
                pass
        self.entity = None

    async def control(self, world):
        pass

class DefenderVehicleController:
    def __init__(
        self,
        robot_id,
        attacker_entity,
        hvt_entity,
        formation_distance,
        formation_angle,
    ):
        self.takeoff = True
        self.robot_id = robot_id
        self.entity = None
        self.error = None
        self.gizmos = []
        self.attacker_entity = attacker_entity
        self.hvt_entity = hvt_entity
        self.formation_distance = formation_distance
        self.formation_angle = formation_angle

    async def spawn(self, world):
        self.entity = await world.rpc('map.spawn_drone', {
            'model': 'f450_simplified',
            'robot_id': self.robot_id,
            'position': Vec3(
                self.formation_distance * math.cos(self.formation_angle),
                self.formation_distance * math.sin(self.formation_angle),
                0,
            ).to_dict(),
        })

    async def despawn(self, world):
        commands = [
            self.remove_gizmos(world),
        ]

        if self.entity is not None:
            commands.append(world.rpc(f'object_{self.entity}.despawn'))

        self.entity = None

        try:
            await asyncio.gather(*commands)
        except:
            pass

    async def remove_gizmos(self, world):
        commands = []
        for gizmo in self.gizmos:
            commands.append(world.rpc(f'object_{gizmo}.despawn'))
        self.gizmos = []
        try:
            await asyncio.gather(*commands)
        except:
            pass

    async def draw_line(self, world, src, dst, color):
        gizmo = await world.rpc(f'gizmos.draw_line', {
            'src': src.to_dict(),
            'dst': dst.to_dict(),
            'color': color,
        })
        self.gizmos.append(gizmo)

    async def control(self, world):
        if self.entity is None:
            return

        try:
            [position, hvt_position, attacker_position, attacker_velocity] = await asyncio.gather(
                world.rpc(f'object_{self.entity}.position'),
                world.rpc(f'object_{self.hvt_entity}.position'),
                world.rpc(f'object_{self.attacker_entity}.position'),
                world.rpc(f'object_{self.attacker_entity}.linear_velocity'),
            )
            position = Vec3.from_dict(position)
            hvt_position = Vec3.from_dict(hvt_position)
            attacker_position = Vec3.from_dict(attacker_position)
            attacker_velocity = Vec3.from_dict(attacker_velocity)

            # if (hvt_position - attacker_position).length() < SHIELD_RADIUS + TERMINAL_PHASE_THR:
            #     intercept_position = attacker_position
            # else:
            #     # intercept_position = hvt_position - (hvt_position - attacker_position).normalize() * SHIELD_RADIUS
            #     intercept_position = hvt_position.copy()
            #     intercept_position -= attacker_direction_from_hvt * Vec3(SHIELD_RADIUS, 0, 0)
            #     intercept_position += attacker_direction_from_hvt * Vec3(
            #         0.,
            #         self.formation_distance * math.cos(self.formation_angle),
            #         self.formation_distance * math.sin(self.formation_angle),
            #     )

            future_attacker_position = attacker_position + attacker_velocity * (TIMESTEP_MS / 1000.0) * 2
            attacker_direction_from_hvt = Quat.from_rotation_arc(Vec3.X, (hvt_position - future_attacker_position).normalize_or_zero())

            if (hvt_position - future_attacker_position).length() < SHIELD_RADIUS + TERMINAL_PHASE_THR:
                intercept_position = future_attacker_position
            else:
                # intercept_position = hvt_position - (hvt_position - attacker_position).normalize() * SHIELD_RADIUS
                intercept_position = hvt_position.copy()
                intercept_position -= attacker_direction_from_hvt * Vec3(SHIELD_RADIUS, 0, 0)
                intercept_position.z = max(intercept_position.z, 4)
                intercept_position += attacker_direction_from_hvt * Vec3(
                    0.,
                    self.formation_distance * math.cos(self.formation_angle),
                    self.formation_distance * math.sin(self.formation_angle),
                )
                intercept_position.z = max(intercept_position.z, 0.5)


            commands = [
                self.remove_gizmos(world),
                self.draw_line(world, attacker_position, future_attacker_position, '#ff0000'),
                self.draw_line(world, future_attacker_position, hvt_position, '#ff0000'),
                self.draw_line(world, position, intercept_position, '#00ff00'),
                world.rpc(f'object_{self.entity}.position_control', {
                    'x': intercept_position.x,
                    'y': intercept_position.y,
                    'z': intercept_position.z,
                    'xy': 0,
                })
            ]

            await asyncio.gather(*commands)

        except Exception as e:
            import traceback
            self.error = e
            print(f"vehicle {self.robot_id} error: {e}")
            traceback.print_exc()

# WorldController()
# asyncio.get_event_loop().run_forever()



class Defender:
    def __init__(self,
                 id: int,
                 formation_distance,
                 formation_angle,
                 vehicle: Vehicle,
                 hvt: Entity):
        self.id = id
        self.formation_distance = formation_distance
        self.formation_angle = formation_angle
        self.vehicle = vehicle
        self.hvt = hvt


async def single_defender_logic(defender: Defender, sim: Simulator):
    try:
        attacker_vehicle = await sim.get_vehicle(ATTACKER_ID)
    except Exception as e:
        print("error: ", e)
        return

    # defender_position = await defender.vehicle.local_position()

    # import pdb;
    # pdb.set_trace()


    hvt_position = await defender.hvt.local_position()

    # print(attacker_vehicle)
    attacker_velocity = await attacker_vehicle.linear_velocity()
    attacker_position = await attacker_vehicle.local_position()
    print("attacker vel: ", attacker_velocity)
    print("attacker pos: ", attacker_position)
    future_attacker_position =  attacker_position.to_vec() + attacker_velocity * (TIMESTEP_MS / 1000.0) * 2
    attacker_direction_from_hvt = Quat.from_rotation_arc(Vec3.X, (hvt_position - future_attacker_position).normalize_or_zero())

    if (hvt_position - future_attacker_position).length() < SHIELD_RADIUS + TERMINAL_PHASE_THR:
            intercept_position = future_attacker_position
    else:
        # intercept_position = hvt_position - (hvt_position - attacker_position).normalize() * SHIELD_RADIUS
        intercept_position = hvt_position.copy()
        intercept_position -= attacker_direction_from_hvt * Vec3(SHIELD_RADIUS, 0, 0)
        intercept_position.z = max(intercept_position.z, 4)
        intercept_position += attacker_direction_from_hvt * Vec3(
            0.,
            defender.formation_distance * math.cos(defender.formation_angle),
            defender.formation_distance * math.sin(defender.formation_angle),
        )
        intercept_position.z = max(intercept_position.z, 0.5)

    # Control vehicle by position
    print("Controlling vehicle ", defender.vehicle)
    print("intercept_position: ", intercept_position)

    await defender.vehicle.position_control(
        Position(intercept_position.x,
                    intercept_position.y,
                    intercept_position.z), 0)


async def defender_control_logic(defenders: List[Defender], sim: Simulator):
    commands = []
    for defender in defenders:
        commands.append(single_defender_logic(defender, sim))
    await asyncio.gather(*commands)


async def main():
    sim = Simulator()
    await sim.connect()
    await sim.reset()

    # Spawn high value target
    hvt = await sim.spawn_entity(ObstacleType.HVT1, Position(20, 0, 0), Rotation(math.pi/6))

    # Spawn defenders
    defenders = []
    for i in range(NUM_DEFENDERS):
        formation_angle = i * 2 * math.pi / NUM_DEFENDERS
        formation_distance = DEFENDER_SPREAD

        position = Position(
                formation_distance * math.cos(formation_angle),
                formation_distance * math.sin(formation_angle),
                0,
            )
        defender_vehicle = await sim.spawn_vehicle(vehicle_id=i,
                                position=position,
                                rotation=Rotation(0,0,0),
                                vehicle_model = "f450_simplified")
        defender = Defender(i, formation_angle, formation_distance, defender_vehicle, hvt)
        defenders.append(defender)

    # Spawn attacker
    _attacker_vehicle = await sim.spawn_vehicle(vehicle_id=ATTACKER_ID,
                                  position=Position(-20,0,0),
                                  rotation=Rotation(0,0,0),
                                  vehicle_model = "f450_pid")
    # defenders.append(attacker_vehicle)
    sim.set_step_duration(TIMESTEP_MS)
    sim.sync(partial(defender_control_logic, defenders))


if __name__ ==  '__main__':
    asyncio.ensure_future(main())
    loop = asyncio.get_event_loop()
    loop.run_forever()

