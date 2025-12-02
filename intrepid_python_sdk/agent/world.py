# world.py
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import time
import json

@dataclass
class Pose3D:
    x: float
    y: float
    z: float
    qx: float = 0.0
    qy: float = 0.0
    qz: float = 0.0
    qw: float = 1.0
    frame_id: str = "map"
    timestamp: float = field(default_factory=time.time)

@dataclass
class PersonDetection:
    id: Optional[str]
    bbox: Optional[Dict]    # {x,y,w,h} in pixels (if available)
    position: Optional[Pose3D]  # estimated 3D position in world frame (if available)
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class RobotState:
    robot_id: str
    pose: Pose3D
    battery_pct: Optional[float] = None
    status: Optional[str] = None
    capabilities: Optional[Dict] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class WorldState:
    robots: Dict[str, RobotState] = field(default_factory=dict)
    detections: Dict[str, List] = field(default_factory=lambda: {"persons": []})
    metadata: Dict = field(default_factory=dict)

    # ----------------
    # Update helpers
    # ----------------
    def update_robot_pose(self, robot_id: str, pose: Pose3D):
        if robot_id not in self.robots:
            self.robots[robot_id] = RobotState(robot_id=robot_id, pose=pose)
        else:
            self.robots[robot_id].pose = pose
            self.robots[robot_id].timestamp = pose.timestamp

    def update_robot_battery(self, robot_id: str, pct: float):
        if robot_id not in self.robots:
            self.robots[robot_id] = RobotState(robot_id=robot_id, pose=Pose3D(0,0,0))
        self.robots[robot_id].battery_pct = pct

    def add_person_detection(self, robot_id: str, det: PersonDetection):
        self.detections.setdefault("persons", [])
        # optionally annotate with source robot_id
        self.detections["persons"].append({"robot_id": robot_id, **asdict(det)})

    # ----------------
    # Serialization
    # ----------------
    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: asdict(o), indent=None)

    @staticmethod
    def from_json(js: str) -> "WorldState":
        data = json.loads(js)
        # Simple loader for MVP; production: full validation
        ws = WorldState()
        if "robots" in data:
            for rid, rdata in data["robots"].items():
                pose = Pose3D(**rdata.get("pose", {}))
                ws.robots[rid] = RobotState(robot_id=rid, pose=pose,
                                            battery_pct=rdata.get("battery_pct"),
                                            status=rdata.get("status"),
                                            capabilities=rdata.get("capabilities"))
        if "detections" in data:
            ws.detections = data["detections"]
        ws.metadata = data.get("metadata", {})
        return ws
