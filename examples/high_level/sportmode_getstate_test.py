# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.sport_client import SportClient 

logging.basicConfig(level=logging.WARNING)  # Set the desired level

async def main():
    communicator = DDSCommunicator(interface="eth0")
    client = SportClient(communicator)
        
    while True:
        try:
            parameters = ["state", "gait", "dance", "continuousGait", "economicGait"]
            result = await client.GetState(parameters)
            if result:
                print("Robot state parameters retrieved successfully:")
                for param, value in result.items():
                    print(f"{param}: {value}")
        except Exception as e:
            print(f"Failed to retrieve robot state parameters: {e}")
        
        await asyncio.sleep(1)


# Usage example
if __name__ == "__main__":
    asyncio.run(main())
