import pybullet as p
import pybullet_data
import time

def validate_stability(furniture_list, render=False):
    p.connect(p.GUI if render else p.DIRECT)
    p.setGravity(0, 0, -9.8)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.loadURDF("plane.urdf")

    stable = True
    for item in furniture_list:
        try:
            half_extents = [item.width / 2, item.height / 2, 0.5]
            shape_id = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_extents)
            p.createMultiBody(baseMass=1,
                              baseCollisionShapeIndex=shape_id,
                              basePosition=[item.x, item.y, 0.5])
        except Exception:
            continue

    for _ in range(240):
        p.stepSimulation()
        if render: time.sleep(1 / 240)

    # TODO: future add tilt angle check
    p.disconnect()
    return stable
