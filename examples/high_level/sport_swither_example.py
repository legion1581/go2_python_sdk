# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.sport_switcher_client import SportSwitcherClient
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
    robot = sdk.create_robot(DDSCommunicator(domainId=0, interface="wlan0"), serialNumber='B42D2000NCS8JJ82')

    # Instantiate the SportSwitcherClient
    # The `ensure_client` method checks if the client exists and creates it if not, ensuring that the robot can use this client.
    sport_switcher_client : SportSwitcherClient = robot.ensure_client(SportSwitcherClient.default_service_name)
        
    # Read the current sport mode (normal or advanced)
    response =  await sport_switcher_client.getSportMode()
    if response:
        print(response)
    
    # Switch the sport mode to advanced
    await sport_switcher_client.setSportMode("advanced")

    #Switch the sport mode to normal
    await sport_switcher_client.setSportMode("normal")


# Usage example
if __name__ == "__main__":
    asyncio.run(main())