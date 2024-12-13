from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type
import math
import pymap3d as pm


# Callback function to execute when inputs are ready
def my_callback_function():
    counter = 0  # Waypoint counter (cannot reset this)
    LAT_0 = 50.84703102
    LON_0 = 4.352496080
    ALT_0 = 0  # in meters
    MAX_SPEED = 1.0  # Maximum drone speed (units per second)
    SAFE_DISTANCE = 10.0  # Example safe distance from waypoints

    def closure(agent_id: int, drone_position: list, trajectory: list, something: list) -> (float, float, float, float, float):
        # Extract components
        drone_x, drone_y, drone_z = drone_position["x"], drone_position["y"], drone_position["z"]
        vx, vy, vz = 0.0, 0.0, 0.0  # Initialize velocities to zero

        nonlocal counter

        while counter < len(trajectory):
            active_waypoint = trajectory[counter]
            # Convert trajectory to local coords
            local_waypoint = pm.geodetic2enu(active_waypoint["x"],
                                            active_waypoint["y"],
                                            active_waypoint["z"],
                                            LAT_0,
                                            LON_0,
                                            ALT_0)
            print("Active WP:", counter)
            print("Global coords ", active_waypoint)

            active_waypoint = {}
            active_waypoint["x"] = float(local_waypoint[0])
            active_waypoint["y"] = float(local_waypoint[1])
            active_waypoint["z"] = float(local_waypoint[2])
            print("Local coords (x, y, z):", active_waypoint)

            # Calculate distance from drone to current waypoint
            dx = active_waypoint["x"] - drone_x
            dy = active_waypoint["y"] - drone_y
            dz = active_waypoint["z"] - drone_z
            distance_to_waypoint = math.sqrt(dx**2 + dy**2 + dz**2)
            print(f"Distance to WP {counter}: {distance_to_waypoint:.2f} meters")

            if distance_to_waypoint < SAFE_DISTANCE:
                print(f"Waypoint {counter} reached.")
                counter += 1  # Move to the next waypoint
                continue  # Check the next waypoint

            print()
            # Calculate velocity vector towards the waypoint
            velocity_factor = min(MAX_SPEED / distance_to_waypoint, 1.0)
            vx = dx * velocity_factor
            vy = dy * velocity_factor
            vz = dz * velocity_factor
            break  # Exit loop temporarily to update velocity and position

        # Maintain current altitude if all waypoints are reached
        altitude = drone_z if counter >= len(trajectory) else trajectory[counter]["z"]

        yaw = 0  # Placeholder yaw computation
        return altitude, yaw, vx, vy, vz

    return closure



# Create my node
mynode = Node()
mynode.from_def("./tutorial_2_config.toml")
inputs = mynode.get_inputs()

# Write to Graph
service_handler = Intrepid()
service_handler.register_node(mynode)

# Create QoS policy for function node
qos = Qos(reliability="BestEffort", durability="TransientLocal")
qos.set_history("KeepLast")
qos.set_deadline(100)  # Deadline expressed in milliseconds
service_handler.create_qos(qos)

# Register callback with node input. Callback and node inputs must have the same signature (same number/name/type)
service_handler.register_callback(my_callback_function)

# Start server and node execution
service_handler.start()
