import asyncio
from clients.sport_client import SportClient
from communicator.constants import ROBOT_CMD
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from communicator.idl.unitree_api.msg.dds_ import RequestIdentity_, Request_, Response_, ResponseHeader_, ResponseStatus_

class MockServer:
    """
    A mock server to listen to requests and send back acknowledgments.
    """
    def __init__(self, communicator, request_topic, response_topic):
        self.communicator = communicator
        self.request_topic = request_topic
        self.response_topic = response_topic

    async def listen_for_requests(self):
        async def callback(request_data):
            print("Received request:", request_data)
            # Check if the request is a Damp command
            if request_data.header.identity.api_id == ROBOT_CMD["Damp"]:
                print("Received Damp command, sending acknowledgment.")
                
                # Prepare acknowledgment response
                response_id = request_data.header.identity.id
                api_id = request_data.header.identity.api_id
                identity = RequestIdentity_(response_id, api_id)
                status = ResponseStatus_(0)  # Assuming 0 means success/acknowledgment
                header = ResponseHeader_(identity=identity, status=status)
                response = Response_(header=header, data='ack', binary=[])
                
                # Publish the acknowledgment to the response_topic
                self.communicator.publish(self.response_topic, response, Response_)

        # Subscribe to the request topic
        self.communicator.subscribe(self.request_topic, Request_, callback)

async def perform_test():
    communicator = DDSCommunicator(interface="wlan0")
    client = SportClient(communicator)
    # Setup the mock server with the same communicator as the client, for demonstration
    # server = MockServer(communicator, "rt/api/sport/request", "rt/api/sport/response")
    # await server.listen_for_requests()

    # Wait a bit to ensure subscriptions are active
    await asyncio.sleep(1)

    # Send a Damp command
    await client.Hello(ack=False)

# Usage example
if __name__ == "__main__":
    asyncio.run(perform_test())
