import os
import time
import random
import asyncio
import json
import logging
from communicator.constants import DDS_TOPICS, DDS_ERROR_DESCRIPTIONS
from cyclonedds.domain import DomainParticipant
from cyclonedds.sub import DataReader
from cyclonedds.pub import DataWriter
from cyclonedds.topic import Topic
from cyclonedds.core import Listener, Qos, Policy, Entity
from cyclonedds.util import duration
from communicator.communicatorWrapper import CommunicatorWrapper
import xml.etree.ElementTree as ET

from communicator.idl.unitree_api.msg.dds_ import RequestIdentity_, RequestLease_, RequestPolicy_, RequestHeader_, Request_, Response_
from communicator.idl.std_msgs.msg.dds_ import String_

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
            DDSCommunicator._participant = DomainParticipant(domain_id=0)

        self.participant = DDSCommunicator._participant
        self.current_id = random.randint(0, 2147483647)
        self.readers = {} # Use a dictionary to manage readers by topic name
        self.topics = {}  # Cache topics to avoid recreating them
        self.writers = {}  # Cache for DataWriter instances
        self.callbacks = {} # Cache for callback instances
        self.deferred_unsubscriptions = {}  # Manage deferred unsubscriptions
        self.main_loop = asyncio.get_event_loop()
    
    def _create_topic(self, topic, data_type):  

        if topic not in self.topics:
            self.topics[topic] = Topic(self.participant, topic, data_type) 
            # time.sleep(2)
        return self.topics[topic]

    def publish(self, topic, data, data_type):

        topic_instance = self._create_topic(topic, data_type)

        # Check if a writer for this topic already exists, if not, create it
        if topic not in self.writers:
            self.writers[topic] = DataWriter(self.participant, topic_instance)
            time.sleep(0.5) #Wait a bit after topic creation

        writer = self.writers[topic]

        logger.debug(f"Data to publish: {data}")
        writer.write(data)

    def subscribe(self, topic, data_type, callback=None):
        # Initialize callback list for the topic if it does not exist
        if topic not in self.callbacks:
            self.callbacks[topic] = []

        # Add the callback to the list of callbacks for this topic if it's not already present
        if callback not in self.callbacks[topic]:
            self.callbacks[topic].append(callback)
            logger.debug(f"Added new callback for {topic}")

        if topic not in self.readers:
            topic_instance = self._create_topic(topic, data_type)
            current_loop = asyncio.get_running_loop()

            class CustomListener(Listener):
                def __init__(self, callbacks, topic, current_loop):
                    super().__init__()
                    self.callbacks = callbacks
                    self.topic = topic
                    self.current_loop = current_loop

                def on_data_available(self, reader):
                    samples = reader.take(N=100)
                    for sample in samples:
                        if sample.sample_info.valid_data:
                            for cb in self.callbacks.get(self.topic, []):
                                asyncio.run_coroutine_threadsafe(cb(sample), self.current_loop)
                        else:
                            logger.error("Received invalid data.")

            # Create the listener and data reader
            listener = CustomListener(self.callbacks, topic, current_loop)
            reader = DataReader(self.participant, topic_instance, listener=listener)
            self.readers[topic] = reader
            logger.info(f"Subscribed to {topic}")

    def unsubscribe(self, topic, callback=None):
        """Unsubscribe from a topic immediately without deferred actions."""
        if topic not in self.readers:
            logger.warning(f"Not subscribed to {topic}, cannot unsubscribe")
            return

        # Remove callback if specified, or all callbacks if not
        if callback:
            if callback in self.callbacks.get(topic, []):
                self.callbacks[topic].remove(callback)
                logger.info(f"Callback removed from {topic}, callback: {callback}")
            else:
                logger.warning(f"Callback not found for {topic}")
        
        # If no callbacks remain, or no specific callback was specified, clean up immediately
        if not callback or not self.callbacks[topic]:
            """Clean up reader and callback resources for a topic."""
            if topic in self.readers:
                del self.readers[topic]  # Clean up the data reader
            if topic in self.callbacks:
                del self.callbacks[topic]  # Remove all callbacks associated with the topic
            logger.info(f"Unsubscribed from {topic}")

    
    async def publishReq(self, topic, requestData, timeout=5):
        if not topic.endswith("/request"):
            logger.error("The request should end with '/request'")
            return
        
        # Prepare the request message
        self.current_id += 1
        request_id = requestData.get('request_id', self.current_id)
        identity = RequestIdentity_(request_id, requestData.get('api_id', 0))
        lease = RequestLease_(requestData.get('lease', 0))
        policy = RequestPolicy_(priority=requestData.get('priority', 0), noreply=requestData.get('noreply', False))
        header = RequestHeader_(identity=identity, lease=lease, policy=policy)
        parameter = json.dumps(requestData.get('parameter'), ensure_ascii=False) if requestData.get('parameter') is not None else ''
        request = Request_(header=header, parameter=parameter, binary=[])

        if not requestData.get('noreply', False):
            response_topic_name = topic.replace("/request", "/response")
            # Make sure the topic and reader are ready
            topic_instance = self._create_topic(response_topic_name, Response_)
            if response_topic_name not in self.readers:
                self.readers[response_topic_name] = DataReader(self.participant, topic_instance)

            # Send the request
            self.publish(topic, request, Request_)
            logger.info(f"Request sent to {topic} with id: {request_id}")

            # Polling for response
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                samples = self.readers[response_topic_name].take(N=1)
                for sample in samples:
                    if sample.sample_info.valid_data and sample.header.identity.id == request_id:
                        if sample.header.status.code == 0:
                            logger.info("Request successful with status code 0.")
                            return sample  # Return the whole response object if successful
                        else:
                            error_description = DDS_ERROR_DESCRIPTIONS.get(sample.header.status.code, "Unknown error code")
                            logger.error(f"Request failed with status code {sample.header.status.code}: {error_description}")
                            return None
                        
            logger.error(f"Response from {response_topic_name} timed out")
        else:
            # Send the request without expecting a response
            self.publish(topic, request, Request_)
            logger.info(f"Request sent with no reply expected to {topic} with id: {request_id}")
            return None

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



