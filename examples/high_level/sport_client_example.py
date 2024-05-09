# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.sport_client import SportClient
import clients.util

async def main():
    # Set up a logger with verbose output enabled. This allows for detailed logging output which can be useful for debugging.
    clients.util.setup_logging(verbose=True)

    # Initialize the SDK with a custom name, which is used to identify the SDK instance and its associated logs.
    sdk = clients.create_standard_sdk('UnitreeGo2SDK')

    # Create a robot instance using the DDS protocol. 
    # `domainId=0` is used as it is currently the standard for all Go2 robots, although a script to change this on the robot is planned.
    # `interface="eth0"` specifies the network interface the DDS should use.
    # Each robot is uniquely identified by a serial number, allowing for multiple robots to be managed by the SDK.
    robot = sdk.create_robot(DDSCommunicator(domainId=45, interface="eth0"), serialNumber='B42D2000NCS8JJ82')

    # Instantiate the SportClient, which is used to send commands related to sport modes and movements.
    # The `ensure_client` method checks if the client exists and creates it if not, ensuring that the robot can use this client.
    robot_sport_client : SportClient = robot.ensure_client(SportClient.default_service_name)

    # Execute a dance sequence asynchronously and wait for an acknowledgment.
    # `ack=True` ensures that the function will wait for the robot to confirm that it has started the sequence.
    await robot_sport_client.WiggleHips(ack=True)

    return

    # Execute a front pounce sequence without waiting for a response from the robot.
    # `ack=False` is used here to send the command without blocking the code execution to wait for a response.
    await robot_sport_client.FrontPounce(ack=False)

    # Change the robot's gait to idle mode, not waiting for a response. 
    # The gait IDs are predefined (0: idle, 1: trot, 2: trot running, 3: forward climbing, 4: reverse climbing).
    await robot_sport_client.SwitchGait(0)

    # Set the Euler angles for the robot. This configuration adjusts the robot's orientation.
    # `roll`, `pitch`, and `yaw` are the rotation angles around the x, y, and z axes respectively.
    args = {
        "roll": -0.75,  # Roll: -0.75 radians (rotation around the x-axis)
        "pitch": 0.75,  # Pitch: 0.75 radians (rotation around the y-axis)
        "yaw": 0  # Yaw: 0 radians (no rotation around the z-axis)
    }
    await robot_sport_client.Euler(args=args, ack=True)

    # Command the robot to move using linear and angular velocities. This command should continiously been executes
    # for the robot to move, otherwise just moves for ~1 sec
    args = {
        "x": 5,  # Linear velocity in the x direction (m/s). Value range: [-2.5, 5].
        "y": 0,  # No movement along the y-axis [-2.5, 5].
        "z": 0  # Angular velocity around the z-axis (rad/s). Set to 0, meaning no rotation [-4, 4].
    }
    await robot_sport_client.Move(args=args, ack=True)

    # Retrieve some states. It's unclear why UNITREE hasn't added these variables to /rt/sportstate, 
    # but some of these variables seem unique and can only be retrieved with this command.      
    try:
        parameters = ["state", "gait", "dance", "continuousGait", "economicGait"]
        result = await robot_sport_client.GetState(parameters)
        if result:
            robot.logger.info("Parameters retrieved successfully:")
            for param, value in result.items():
                print(f"{param}: {value}")
    except Exception as e:
             robot.logger.info(f"Failed to retrieve parameters: {e}")

    ### TODO add more examples here


# Usage example
if __name__ == "__main__":
    asyncio.run(main())