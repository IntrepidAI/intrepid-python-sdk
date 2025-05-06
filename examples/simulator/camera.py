import asyncio
from intrepid_python_sdk.simulator import Simulator, Camera, AbstractSensor
import base64
import numpy as np
import cv2
import time
from base64 import b64decode



# with open("image.png", "wb") as f:
#     f.write(data)


class MySensor:
    pass

# base64 to OpenCV
def base64_cv2(base64_str):
  imgString = base64.b64decode(base64_str)
  nparr = np.fromstring(imgString, np.uint8)
  cv2_img= cv2.imdecode(nparr, cv2.IMREAD_COLOR)
  return cv2_img


async def main():
    sim = Simulator()
    await sim.connect()

    # Get vehicle from agent_id
    vehicle = await sim.get_vehicle(vehicle_id=1)

    camera = await vehicle.spawn_camera(position=[0,0,0],
                                        rotation=[0,0,0],
                                        size=[320, 240],
                                        fov_degrees=120)
    _ = await camera.capture()

    for i in range(30):
        imgbuf = await camera.capture()
        header, encoded = imgbuf.split("base64,", 1)
        data = b64decode(encoded)
        with open(f"image{i}.png", "wb") as f:
            f.write(data)

        im = cv2.imread(f"image{i}.png", cv2.IMREAD_UNCHANGED)
        cv2.imshow("Camera Footage", im)
        time.sleep(0.1)

    # im = cv2.imread("image20.png", cv2.IMREAD_UNCHANGED)
    # cv2.imshow("Camera Footage", im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # img = base64_cv2(imgbuf)
    # cv2.imshow(img)

    # print(sensor.capture())


    # print(f"vehicle: {vehicle}")
    # pos = await vehicle.position()
    # print(f"pos: {pos}")

    # # Get partial state
    # rot = await vehicle.rotation()
    # print(f"rot: {rot}")
    # acc = await vehicle.acceleration()
    # print(f"acc: {acc}")
    # av = await vehicle.angular_velocity()
    # print(f"av: {av}")
    # lv = await vehicle.linear_velocity()
    # print(f"lv: {lv}")

    # # Get full state
    # full_state = await vehicle.state()
    # print(f"state: {full_state}")

    # # Get non-existing vehicle
    # non_existing_vehicle = await sim.get_vehicle(vehicle_id=999)
    # print(f"non_existing_vehicle: {non_existing_vehicle}")




if __name__ ==  '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
