# import rclpy
# from geometry_msgs.msg import PoseStamped
# from sensor_msgs.msg import Image
# from intrepid.actions import ActionHandle, ActionResult, ActionStatus, ActionFeedback
# from intrepid.adapter import AdapterBase, action, sensor

# class ROS2Adapter(AdapterBase):
#     def __init__(self):
#         rclpy.init()
#         self.node = rclpy.create_node("intrepid_adapter")

#     @action("Takeoff")
#     async def takeoff(self):
#         self.node.create_client(Takeoff, "/px4/takeoff").call_async(Takeoff.Request())
#         return "ok"

#     @action("MoveTo")
#     async def go_to(self, pos):
#         msg = PoseStamped()
#         msg.pose.position.x = pos.x
#         msg.pose.position.y = pos.y
#         msg.pose.position.z = pos.z
#         self.navigator_pub.publish(msg)
#         return "ok"

#     @action("DetectPerson")
#     async def detect_person(self):
#         img = await self._latest_camera_frame()
#         return run_detector(img)  # your vision m# intrepid/examples/adapters/ros2_adapter.py


import rclpy
from rclpy.node import Node
from intrepid.adapter import AdapterBase, action, sensor
from intrepid.world import Pose3D, PersonDetection
from intrepid.actions import ActionHandle, ActionResult, ActionStatus, ActionFeedback
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import asyncio

class ROS2RuntimeClientWrapper:
    def __init__(self, runtime):
        self.runtime = runtime
    def update_world_robot_pose(self, robot_id, pose: Pose3D):
        self.runtime.world.update_robot_pose(robot_id, pose)
    # add more helper methods...

class ROS2Adapter(AdapterBase, Node):
    def __init__(self, runtime, robot_id='ros2-robot-01'):
        Node.__init__(self, 'intrepid_ros2_adapter')
        AdapterBase.__init__(self, runtime_client=ROS2RuntimeClientWrapper(runtime))
        self.robot_id = robot_id
        # nav2 action client
        self._nav_client = rclpy.action.ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.create_subscription(PoseStamped, '/pose', self._pose_cb, 10)

    def _pose_cb(self, msg: PoseStamped):
        pose = Pose3D(x=msg.pose.position.x, y=msg.pose.position.y, z=msg.pose.position.z,
                      qx=msg.pose.orientation.x, qy=msg.pose.orientation.y,
                      qz=msg.pose.orientation.z, qw=msg.pose.orientation.w,
                      frame_id=msg.header.frame_id)
        self.runtime.update_world_robot_pose(self.robot_id, pose)

    @action("MoveTo")
    async def move_to(self, params):
        # translate Intrepid Pose3D param into nav2 NavigateToPose
        goal_pose = params["goal"]  # expect dict of pose fields
        goal_msg = NavigateToPose.Goal()
        # fill goal_msg.pose
        # ... create handle
        handle = ActionHandle()
        # run nav2 send_goal asynchronously
        # for sketch: we'll just set succeeded after sleep
        async def run():
            handle._status = ActionStatus.RUNNING
            await self._send_nav2_goal(goal_msg, handle)
        asyncio.create_task(run())
        return handle

    async def _send_nav2_goal(self, goal_msg, handle: ActionHandle):
        # actual Nav2 action client code should be here
        # simulate progress:
        for p in [0.1,0.5,0.9]:
            await handle.send_feedback(ActionFeedback(progress=p, message="moving"))
            await asyncio.sleep(0.5)
        handle.set_result(ActionResult(status=ActionStatus.SUCCEEDED, result={"arrived": True}))

    @sensor("PersonDetection")
    def person_detection_cb(self, detection_msg):
        # convert detection to PersonDetection and update runtime
        det = PersonDetection(id="p1", bbox=None, position=None, confidence=0.9)
        self.runtime.world.add_person_detection(self.robot_id, det)
