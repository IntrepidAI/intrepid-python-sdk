from intrepid_python_sdk import Intrepid, Qos, Node, IntrepidType, Type
import socket


# Callback function to execute when inputs are ready
def my_callback_function():

    def closure(bind_host: str, bind_port: int) -> (int, str, str):
        """
        Opens a TCP server to listen for incoming messages, receive data, and send responses.

        Args:
            bind_host (str): The IP address or hostname to bind the server.
            bind_port (int): The port number to listen on.

        Returns:
            status (int): Status code based on the server operations (200 for success, 500 for errors).
            response (str): A response string indicating the result.
        """
        try:
            # Create a TCP server socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((bind_host, bind_port))
                server_socket.listen(5)  # Allow up to 5 queued connections

                print(f"Server listening on {bind_host}:{bind_port}...")

                # Accept a single connection
                conn, addr = server_socket.accept()
                with conn:
                    print(f"Connection established with {addr}")

                    # Receive message from client
                    data = conn.recv(1024)
                    if not data:
                        print("No data received.")
                        return 500, "No data received"

                    message = data.decode('utf-8')
                    print(f"Received message: {message}")

                    # Prepare response
                    response = f"Server received: {message}"
                    conn.sendall(response.encode('utf-8'))  # Send the response back

                    print(f"Sent response: {response}")

                    # Return success status
                    return 200, response, message

        except Exception as e:
            print(f"Server error: {str(e)}")
            return 500, f"Server error: {str(e)}"


    return closure



# Create my node
mynode = Node()
mynode.from_def("./netnode_recv_config.toml")
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
