import asyncio
import json
from clients.sport_client import SportClient 
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from communicator.idl.unitree_api.msg.dds_ import RequestIdentity_, Request_, Response_, ResponseHeader_, ResponseStatus_

class MockServer:
    """
    A mock server to listen to requests and send back a mock response.
    """
    def __init__(self, communicator, request_topic, response_topic):
        self.communicator = communicator
        self.request_topic = request_topic
        self.response_topic = response_topic

    async def listen_for_requests(self):
        async def callback(request_data):
            print("Received request:", request_data)
            # Simulate processing and create a response
            response_data = {
                "continuousGait": {"data": 0},
                "dance": {"data": 0},
                "gait": {"data": "walk"},
                "state": {"data": "balanceStand"},
                "economicGait": {"data": 0}
            }
            data = json.dumps(response_data)
            print("Sending response:", response_data)

            response_id = request_data.header.identity.id
            api_id = request_data.header.identity.api_id
            identity = RequestIdentity_(response_id, api_id)
            status = ResponseStatus_(0)
            header = ResponseHeader_(identity=identity, status=status)
            response = Response_(header=header, data=data, binary=[])

            # Publish the response to the response_topic
            self.communicator.publish(self.response_topic, response, Response_)  # Assume publish is async and takes (topic, data, data_type)

        self.communicator.subscribe(self.request_topic, Request_, callback)  # Ensure Request_ is defined or imported

async def perform_test():
    communicator = DDSCommunicator(interface="wlan0")
    client = SportClient(communicator)

    # Setup the mock server with the same communicator as the client, for demonstration
    # server = MockServer(communicator, "rt/api/sport/request", "rt/api/sport/response")
    # await server.listen_for_requests()  # Use await here if listen_for_requests is an async operation

    # Wait a bit to ensure subscriptions are active
    await asyncio.sleep(1)  # Wait for 1 second, adjust as necessary

    try:
        result = await client.GetState()
        print("Robot state parameters retrieved successfully:")
        for param, value in result.items():
            print(f"{param}: {value}")
    except Exception as e:
        print(f"Failed to retrieve robot state parameters: {e}")

# Usage example
if __name__ == "__main__":
    asyncio.run(perform_test())
