# Add clients and communicator directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.sport_client import SportClient 

logging.basicConfig(level=logging.INFO)  # Set the desired level

async def main():
    communicator = DDSCommunicator(interface="eth0")
    client = SportClient(communicator)
        
    #awaiting for response     
    await client.Dance1(ack=True)

    #not awaiting for response
    await client.FrontPounce(ack=False)

    # change Gait, no response 
    await client.SwitchGait(0) # 0 is idle, 1 is trot, 2 is trot running, 3 is forward climbing mode, and 4 is reverse climbing mode.

    ### TODO add more examples here


# Usage example
if __name__ == "__main__":
    asyncio.run(main())