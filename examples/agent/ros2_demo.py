from intrepid_python_sdk import Intrepid
from intrepid_python_sdk.intrepid_types import Context

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

rclpy.init()

class PersistentPublisher(Node):
    def __init__(self, topic_name):

        super().__init__('persistent_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10)

    def publish_message(self, message) -> bool:
        msg = String()
        msg.data = message
        try:
            self.publisher_.publish(msg)
        except:
            return False

        self.get_logger().info(f'Publishing: "{message}"')
        return True


def publish_to_ros(ctx: Context[PersistentPublisher], topic_name: str, message: str) -> bool:
    """ Publish message to ROS2 topic_name """

    if ctx.state is None:
        ctx.state = PersistentPublisher(topic_name)

    return ctx.state.publish_message(message)



if __name__ == "__main__":
    runtime = Intrepid()

    # Create a node (called ROS2 Publisher) implementing publish_to_ros
    runtime.register_node(publish_to_ros,
                     label="ROS2 Publisher",
                     description="Publish message to a ROS2 topic")
    runtime.start("0.0.0.0", 8765)
