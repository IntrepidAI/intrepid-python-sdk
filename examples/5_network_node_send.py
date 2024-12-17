from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type
import socket


# Callback function to execute when inputs are ready
def my_callback_function():

    def closure(dest_host: str, dest_port: int, header: str, message: str) -> (int, str):

        try:
            # Establish a TCP socket connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Set a 5-second timeout for operations

                print(f"Connecting to {dest_host}:{dest_port}...")
                s.connect((dest_host, dest_port))

                # Prepare and send the message
                payload = f"{header}\n{message}"
                s.sendall(payload.encode('utf-8'))  # Send header and message encoded

                # Receive response
                data = s.recv(1024)  # Adjust buffer size as needed
                response = data.decode('utf-8')  # Decode the received bytes

                print(f"Received response: {response}")

                # Return a successful status and the received response
                status = 200
                return status, response

        except (socket.timeout, ConnectionError) as e:
            print(f"Error: {str(e)}")
            status = 500  # Return an error status
            return status, f"Error: {str(e)}"

    return closure



# Create my node
mynode = Node()
mynode.from_def("./netnode_send_config.toml")
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
