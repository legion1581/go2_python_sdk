# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.robot_state_client import RobotStateClient
import clients.util


async def main():
    # Set up a logger for detailed output, useful for debugging and tracking operational logs.
    clients.util.setup_logging(verbose=True)

    # Initialize the SDK with a unique name for easier identification in logs and management.
    sdk = clients.create_standard_sdk('UnitreeGo2SDK')

    # Create a robot instance with a specified domain ID and network interface, essential for communications.
    robot = sdk.create_robot(DDSCommunicator(domainId=45, interface="eth0"), serialNumber='B42D2000NCS8JJ82')

    # Ensure the RobotStateClient is instantiated and ready to use.
    robot_state_client: RobotStateClient = robot.ensure_client(RobotStateClient.default_service_name)
        
    # Set the frequency of service reports to every second for 10 seconds.
    await robot_state_client.SetReportFreq(1, 10)
    
    vui_service_status = await robot_state_client.fetch_service_status("vui_service", 5)
    
    if vui_service_status is not None:
    # Toggle the 'vui_service' based on its current status after exiting the loop.
        await robot_state_client.ServiceSwitch("vui_service", not vui_service_status)

# Usage example
if __name__ == "__main__":
    asyncio.run(main())