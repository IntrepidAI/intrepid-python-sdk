# cargo run --release

import asyncio
from intrepid_python_sdk.simulator import Simulator, ObstacleType, Position, Rotation
import random

GRID_SIZE = 8  # 4x4 blocks, so 5x5 intersections
BLOCK_LENGTH = 70
TREE_PROBABILITY = 0.3  # 30% chance to spawn a tree near the road
BUILDING1_PROBABILITY = 0.5
BUILDING2_PROBABILITY = 0.3


async def main():
    sim = Simulator()
    await sim.connect()

    # Create a grid of intersections and roads (horizontal + vertical)
    # for row in range(GRID_SIZE + 1):  # +1 to include the far edge
    #     for col in range(GRID_SIZE + 1):
    #         x = col * BLOCK_LENGTH
    #         y = row * BLOCK_LENGTH
    #         pos = Position(x, y, 0)
    #         # Optionally: spawn intersection marker/entity
    #         # await sim.spawn_entity(ObstacleType.INTERSECTION, pos, Rotation(0,0,0))
    #         # UGV at some intersections
    #         if row < GRID_SIZE and col < GRID_SIZE:
    #             ugv_pos = Position(x + 2, y + 2, 0)
    #             ugv = await sim.spawn_ugv(row * GRID_SIZE + col, ugv_pos, Rotation(0,0,0))
    #             print(ugv)

    # Horizontal roads
    for row in range(GRID_SIZE + 1):
        for col in range(GRID_SIZE):
            x1 = col * BLOCK_LENGTH
            x2 = (col + 1) * BLOCK_LENGTH
            y = row * BLOCK_LENGTH
            pos1 = Position(x1, y, 0)
            pos2 = Position(x2, y, 0)
            await sim.spawn_road(pos1, pos2)

            # Maybe add trees along the road
            for dx in range(10, BLOCK_LENGTH, 5):
                tx = x1 + dx
                ty = y + 25 + random.uniform(-1, 1)  # small offset from road
                chance = random.random()
                if chance > 0.1 and chance < BUILDING2_PROBABILITY:
                    await sim.spawn_entity(ObstacleType.BUILDING2, Position(tx, ty, 0), Rotation(0,0,0))
                # elif chance > BUILDING2_PROBABILITY and chance < BUILDING1_PROBABILITY:
                #     await sim.spawn_entity(ObstacleType.BUILDING1, Position(tx, ty, 0), Rotation(0,0,0))

    # Vertical roads
    for col in range(GRID_SIZE + 1):
        for row in range(GRID_SIZE):
            y1 = row * BLOCK_LENGTH
            y2 = (row + 1) * BLOCK_LENGTH
            x = col * BLOCK_LENGTH
            pos1 = Position(x, y1, 0)
            pos2 = Position(x, y2, 0)
            await sim.spawn_road(pos1, pos2)

            # Maybe add trees along the road
            for dy in range(5, BLOCK_LENGTH, 5):
                if random.random() < TREE_PROBABILITY:
                    ty = y1 + dy
                    tx = x + 3 + random.uniform(-1, 1)
                    await sim.spawn_entity(ObstacleType.TREE1, Position(tx, ty, 0), Rotation(0,0,0))




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
