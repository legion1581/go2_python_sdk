# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.motion_switcher_client import MotionSwitcher 

logging.basicConfig(level=logging.INFO)  # Set the desired level

async def main():
    communicator = DDSCommunicator(interface="eth0")
    client = MotionSwitcher(communicator)
        
    # Read the current sport mode (normal or advanced)
    response =  await client.getSportMode()
    if response:
        print(response)
    
    # Switch the sport mode to advanced
    await client.setSportMode("advanced")

    #Switch the sport mode to normal
    await client.setSportMode("normal")


# Usage example
if __name__ == "__main__":
    asyncio.run(main())