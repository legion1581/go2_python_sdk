import os
import time
import random
import asyncio
import json
import logging
from communicator.constants import DDS_TOPICS, DDS_ERROR_DESCRIPTIONS
from cyclonedds.domain import DomainParticipant, Domain
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.topic import Topic
from cyclonedds.core import Listener
from communicator.communicatorWrapper import CommunicatorWrapper
import xml.etree.ElementTree as ET

from communicator.idl.unitree_api.msg.dds_ import RequestIdentity_, RequestLease_, RequestPolicy_, RequestHeader_, Request_, Response_

logging.basicConfig(level=logging.DEBUG)  # Set the desired level
logger = logging.getLogger(__name__)

class DDSCommunicator(CommunicatorWrapper):
    # Class variable to hold the DomainParticipant instance
    _participant = None

    def __init__(self, interface="eth0"):
        self.name = "DDS"
        self._set_network(interface)

        # If a DomainParticipant has not been created, do so with the updated configuration
        if DDSCommunicator._participant is None:
            # Directly use the path to the XML configuration file when creating the Domain
            DDSCommunicator._participant = DomainParticipant()

        self.participant = DDSCommunicator._participant
        self.subscriber = Subscriber(self.participant)
        self.publisher = Publisher(self.participant)
        self.readers = {} # Use a dictionary to manage readers by topic name
        self.topics = {}  # Cache topics to avoid recreating them
        self.writers = {}  # Cache for DataWriter instances
        self.main_loop = asyncio.get_event_loop()
    
    def _create_topic(self, name, data_type):
        if name not in self.topics:
            self.topics[name] = Topic(self.participant, name, data_type)
        return self.topics[name]

    def publish(self, topic, data, data_type):
        # Ensure the topic exists
        topic_instance = self._create_topic(topic, data_type)

        # Check if a writer for this topic already exists, if not, create it
        if topic not in self.writers:
            self.writers[topic] = DataWriter(self.publisher, topic_instance)

        writer = self.writers[topic]
        logger.debug(f"Data to publish: {data}")
        writer.write(data)

    def subscribe(self, topic, data_type, callback):
        if topic in self.readers:
            logger.warning(f"Already subscribed to {topic}. Consider unsubscribing before resubscribing.")
            return

        topic_instance = self._create_topic(topic, data_type)

        # Capture the current event loop at the time of subscription.
        # This assumes subscriptions are made from the main thread with the running event loop.
        current_loop = asyncio.get_event_loop()
        
        class CustomListener(Listener):
            def on_data_available(self, reader):
                samples = reader.take()
                for sample in samples:
                    logger.debug(f"Data recieved from subscribe: {sample}")
                    if sample.sample_info.valid_data:
                        try:
                            # Schedule the callback in the captured event loop
                            asyncio.run_coroutine_threadsafe(callback(sample), current_loop)
                        except RuntimeError as e:
                            logger.error(f"Failed to schedule callback: {e}")
        
        reader = DataReader(self.subscriber, topic_instance, listener=CustomListener())
        self.readers[topic] = reader
        logger.info(f"Subscribed to {topic}")

    def unsubscribe(self, topic):
        if topic not in self.readers:
            logger.warning(f"Not subscribed to {topic}, cannot unsubscribe.")
            return
        
        # Assuming a way to cleanly tear down the reader if necessary

        del self.readers[topic]
        logger.info(f"Unsubscribed from {topic}")
    
    async def publishReq (self, topic, requestData, timeout=5):
        if not topic.endswith("/request"):
            logger.error("The request should end with /request")
            return
        
        # Prepare the request message
        request_id = requestData.get('request_id', int(time.time()) % 2147483648 + random.randint(0, 1000))
        identity = RequestIdentity_(request_id, requestData.get('api_id', 0))
        lease = RequestLease_(requestData.get('lease', 0))
        policy = RequestPolicy_(priority=requestData.get('priority', 0), noreply=requestData.get('noreply', False))
        header = RequestHeader_(identity=identity, lease=lease, policy=policy)
        parameter = json.dumps(requestData.get('parameter'), ensure_ascii=False) if requestData.get('parameter') is not None else ''
        request = Request_(header=header, parameter=parameter, binary=[])
        
        # Send the request
        self.publish(topic, request, Request_)
        logger.info(f"Request sent to {topic}")

        # No need to proceed further for no-reply requests
        if requestData.get('noreply', False):
            return None
        
        response_topic_name = topic.replace("/request", "/response")

        # Listen for the response
        future = asyncio.get_event_loop().create_future()
        
        async def response_callback(response_data):
            if response_data.header.identity.id == request_id:
                if not future.done():
                    future.set_result(response_data)
                    self.unsubscribe(response_topic_name)

        self.subscribe(response_topic_name, Response_, response_callback)

        try:
            response = await asyncio.wait_for(future, timeout)
            # Check if response is not None
            if response:
                # Now check the status code of the response
                if response.header.status.code == 0:
                    logger.info("Request successful with status code 0.")
                    return response  # Return the whole response object if successful
                else:
                    # Handle error status codes
                    error_description = DDS_ERROR_DESCRIPTIONS.get(response.header.status.code, "Unknown error code")
                    logger.error(f"Request failed with status code {response.header.status.code}: {error_description}")
                    return None  # Consider returning None or error details on failure
            else:
                logger.error("No response received.")
                return None
        except asyncio.TimeoutError:
            logger.error(f"Response from {response_topic_name} timed out")
            return None
    
    def get_topic_by_name(self, name):
        return DDS_TOPICS[name]
    
    def _set_network(self, interface):

        current_path = os.path.dirname(os.path.abspath(__file__))
        cyclonedds_config_path = os.path.join(current_path, "cyclonedds.xml")
        tree = ET.parse(cyclonedds_config_path)
        root = tree.getroot()

        # Find the NetworkInterface element and change its name attribute
        for network_interface in root.findall(".//NetworkInterface"):
            network_interface.set("name", interface)  # Change the interface name

        # Save the modified XML back to the file
        tree.write(cyclonedds_config_path)

         # Set the CYCLONEDDS_URI environment variable to point to the updated config file
        os.environ['CYCLONEDDS_URI'] = cyclonedds_config_path
        logger.info(f"CYCLONEDDS_URI set to: {cyclonedds_config_path}")

        logger.info(f"DDS Domain configured with network interface {interface}")



