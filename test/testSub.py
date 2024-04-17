import asyncio
import logging
from clients.sport_client import SportState
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from communicator.idl.unitree_go.msg.dds_ import SportModeState_, IMUState_, PathPoint_, TimeSpec_

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def custom_callback(data):
    """
    Custom callback function to process the received data.
    """
    logger.info(f"Got the imu data: {data.imu_state.accelerometer}")

async def publish_sport_mode_state(communicator, topic):
    while True:
        sport_mode_state = SportModeState_(
            stamp=TimeSpec_(sec=1711603666, nanosec=233088524),
            error_code=0,
            imu_state=IMUState_(
                quaternion=[0.9761399626731873, 0.009133945219218731, -0.00014730705879628658, 0.2169501632452011],
                gyroscope=[0.008522114716470242, -0.019174758344888687, -0.02237055078148842],
                accelerometer=[0.10773907601833344, 0.09217676520347595, 9.53849983215332],
                rpy=[0.01776919700205326, -0.0042508188635110855, 0.4373590648174286],
                temperature=79
            ),
            mode=1,
            progress=0.0,
            gait_type=1,
            foot_raise_height=0.09000000357627869,
            position=[-5.45238733291626, -0.0790208950638771, 0.31081774830818176],
            body_height=0.3199999928474426,
            velocity=[0.004781864583492279, -0.0007157432846724987, -0.021893171593546867],
            yaw_speed=-0.02237055078148842,
            range_obstacle=[2.0, 2.0, 2.0, 2.0],
            foot_force=[136, 133, 117, 112],
            foot_position_body=[
                0.1886584609746933, -0.11758740246295929, -0.31161776185035706, 0.17782104015350342,
                0.10546503961086273, -0.31300225853919983, -0.19986705482006073, -0.12721499800682068,
                -0.30945026874542236, -0.1934507042169571, 0.12067098915576935, -0.3106277287006378
            ],
            foot_speed_body=[
                0.006779681891202927, 0.013316601514816284, -0.003435283899307251, -0.010066003538668156,
                0.03395499661564827, 0.006311581935733557, 0.013018809258937836, -0.015360712073743343,
                -0.0007106108241714537, -0.008062327280640602, -0.01218421384692192, -0.004974719136953354
            ],
            path_point=[PathPoint_(t_from_start=0.0, x=0.0, y=0.0, yaw=0.0, vx=0.0, vy=0.0, vyaw=0.0) for _ in range(10)]
        )

        communicator.publish(topic, sport_mode_state, SportModeState_)

        logger.debug(f"Published SportModeState to {topic}")
        await asyncio.sleep(3)

async def perform_test():

    communicator = DDSCommunicator(interface="eth0")
    # Create a SportState instance and start listening
    sport_state = await SportState.create_and_listen(communicator, frequency="lf")
     # Add custom callback for processing data
    sport_state.add_custom_callback(custom_callback)

    topic = sport_state.topic  # Using the topic from SportState

    # Start publishing test data
    await publish_sport_mode_state(communicator, topic)

    # Optionally, stop listening if needed (not demonstrated here)
    # await sport_state_listener.stop_listening()

if __name__ == "__main__":
    asyncio.run(perform_test())