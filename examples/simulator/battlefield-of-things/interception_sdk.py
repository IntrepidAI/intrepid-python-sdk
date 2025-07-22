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

    [hvt_position, attacker_velocity, attacker_position] = await asyncio.gather(
        defender.hvt.local_position(),
        attacker_vehicle.linear_velocity(),
        attacker_vehicle.local_position()
    )

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

