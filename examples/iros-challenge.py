from intrepid import Intrepid, Qos, Node, DataType
import time
import math

is_takeoff = True  # Global variable to track takeoff state
last_checkpoint_x = 0.
last_checkpoint_y = 0.
last_checkpoint_z = 0.
counter = 0


# Callback function to execute when inputs are ready
def my_callback_function(drone_position: list,
                         checkpoint_position: list,
                         obstacle_position: list) -> (float, float, float, float):
    global is_takeoff
    global checkpoint_x
    global checkpoint_y
    global checkpoint_z
    global counter

    counter += 1

    if drone_position["z"] >= 2.5:
        is_takeoff = False
        print("Takeoff ended")

    if is_takeoff:
        print("Takeoff started")
        altitude = 10.5
        yaw = 0
        x,y = drone_position["x"], drone_position["y"]
        return altitude, yaw, x, y


    # Extract components
    drone_x, drone_y, drone_z = drone_position["x"], drone_position["y"], drone_position["z"]
    if counter % 59:
        checkpoint_x, checkpoint_y, checkpoint_z = checkpoint_position["x"], checkpoint_position["y"], checkpoint_position["z"]
        last_checkpoint_x, last_checkpoint_y, last_checkpoint_z =

        
    obstacle_x, obstacle_y, obstacle_z = obstacle_position["x"], obstacle_position["y"], obstacle_position["z"]

    # print(drone_position, type(drone_position))

    # Calculate distance from drone to checkpoint
    dx = checkpoint_x - drone_x
    dy = checkpoint_y - drone_y
    dz = checkpoint_z - drone_z

    # Calculate Yaw (angle in the x-y plane between the drone and the checkpoint)
    # yaw = math.atan2(dy, dx)
    yaw = 0.0

    # Calculate new position to move towards checkpoint, avoiding obstacles
    # You can implement a simple obstacle avoidance logic by adjusting x, y positions
    safe_distance = 5.0  # Example safe distance from obstacles
    distance_to_obstacle = math.sqrt((obstacle_x - drone_x) ** 2 + (obstacle_y - drone_y) ** 2)

    if distance_to_obstacle < safe_distance:
        # Move away from obstacle by adjusting x and y
        move_away_factor = safe_distance / (distance_to_obstacle + 0.1)
        x = drone_x - (obstacle_x - drone_x) * move_away_factor
        y = drone_y - (obstacle_y - drone_y) * move_away_factor
    else:
        # Move towards checkpoint
        x = checkpoint_x
        y = checkpoint_y

    # Set altitude to a safe height above both the obstacle and the checkpoint
    altitude = max(checkpoint_z, obstacle_z + 10.0)  # Add a 1.0 meter buffer over obstacle

    return altitude, yaw, x, y




# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds


# Create my node
node_type = "node/sdk/iros-challenge-sol-1"
mynode = Node(node_type)
mynode.add_input("flow", DataType.FLOW)
mynode.add_input("drone_position", DataType.VEC3)
mynode.add_input("checkpoint_position", DataType.VEC3)
mynode.add_input("obstacle_position", DataType.VEC3)

mynode.add_output("flow", DataType.FLOW)
mynode.add_output("altitude", DataType.FLOAT)
mynode.add_output("yaw", DataType.FLOAT)
mynode.add_output("x", DataType.FLOAT)
mynode.add_output("y", DataType.FLOAT)

print("Created node ", mynode.get_type())

# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)

# Attach Qos policy to this node
service_handler.create_qos(qos)
print("Attached QoS policy to node")

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(my_callback_function)
print("Callback registered to node")

# Start server and node execution
service_handler.start()