import time
import random
import asyncio
import json
import logging
from communicator.topics_and_errors import STATUS_CODE_ERROR_DESCRIPTIONS
from cyclonedds.domain import DomainParticipant
from cyclonedds.sub import DataReader
from cyclonedds.pub import DataWriter
from cyclonedds.topic import Topic
from cyclonedds.core import Listener
from communicator.common import CommunicatorBase
from communicator.cyclonedds.util import DataClassManager, cyclondds_xml_set, get_topic_by_name

from communicator.cyclonedds.idl.idl_dataclass_map import idl_dataclass_map

class DDSCommunicator(CommunicatorBase):

    def __init__(self, domainId=0, interface=None):
        self.name = 'DDS'

        if interface:
            cyclondds_xml_set(interface)

        self.logger = logging.getLogger(self.name)
        self.domain_id = domainId
        self.participant = DomainParticipant(self.domain_id)
        self.current_id = random.randint(0, 2147483647)
        self.readers = {} # Use a dictionary to manage readers by topic name
        self.topics = {}  # Cache topics to avoid recreating them
        self.writers = {}  # Cache for DataWriter instances
        self.callbacks = {} # Cache for callback instances
        self.deferred_unsubscriptions = {}  # Manage deferred unsubscriptions
        self.main_loop = asyncio.get_event_loop()

        self.data_class_manager = DataClassManager()

    
    def _create_topic(self, topic, data_type):  

        if topic not in self.topics:
            self.topics[topic] = Topic(self.participant, topic, data_type) 
            # time.sleep(2)
        return self.topics[topic]

    def update_from(self, other):
        self.logger = other.logger.getChild(self.name or __class__.__name__)

    def get_topic_by_name(self, name):
        return get_topic_by_name(name)
    
    def get_data_class(self, class_name):
        return self.data_class_manager.get_data_class(class_name)

    def publish(self, topic, data, data_type):

        topic_instance = self._create_topic(topic, data_type)

        # Check if a writer for this topic already exists, if not, create it
        if topic not in self.writers:
            self.writers[topic] = DataWriter(self.participant, topic_instance)
            time.sleep(0.5) #Wait a bit after topic creation

        writer = self.writers[topic]

        self.logger.debug(f"Data to publish: {data}")
        writer.write(data)

    def subscribe(self, topic, data_type, callback=None):
        # Initialize callback list for the topic if it does not exist
        if topic not in self.callbacks:
            self.callbacks[topic] = []

        # Add the callback to the list of callbacks for this topic if it's not already present
        if callback not in self.callbacks[topic]:
            self.callbacks[topic].append(callback)
            self.logger.debug(f"Added new callback for {topic}")

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
                            self.logger.error("Received invalid data.")

            # Create the listener and data reader
            listener = CustomListener(self.callbacks, topic, current_loop)
            reader = DataReader(self.participant, topic_instance, listener=listener)
            self.readers[topic] = reader
            self.logger.info(f"Subscribed to {topic}")

    def unsubscribe(self, topic, callback=None):
        """Unsubscribe from a topic immediately without deferred actions."""
        if topic not in self.readers:
            self.logger.warning(f"Not subscribed to {topic}, cannot unsubscribe")
            return

        # Remove callback if specified, or all callbacks if not
        if callback:
            if callback in self.callbacks.get(topic, []):
                self.callbacks[topic].remove(callback)
                self.logger.info(f"Callback removed from {topic}, callback: {callback}")
            else:
                self.logger.warning(f"Callback not found for {topic}")
        
        # If no callbacks remain, or no specific callback was specified, clean up immediately
        if not callback or not self.callbacks[topic]:
            """Clean up reader and callback resources for a topic."""
            if topic in self.readers:
                del self.readers[topic]  # Clean up the data reader
            if topic in self.callbacks:
                del self.callbacks[topic]  # Remove all callbacks associated with the topic
            self.logger.info(f"Unsubscribed from {topic}")

    
    async def publishReq(self, topic, requestData, timeout=5):
        if not topic.endswith("/request"):
            self.logger.error("The request should end with '/request'")
            return
        
        # Prepare the request message
        self.current_id += 1
        request_id = requestData.get('request_id', self.current_id)
        identity = self.get_data_class('RequestIdentity_')(request_id, requestData.get('api_id', 0))
        lease = self.get_data_class('RequestLease_')(requestData.get('lease', 0))
        policy = self.get_data_class('RequestPolicy_')(priority=requestData.get('priority', 0), noreply=requestData.get('noreply', False))
        header = self.get_data_class('RequestHeader_')(identity=identity, lease=lease, policy=policy)
        parameter = json.dumps(requestData.get('parameter'), ensure_ascii=False) if requestData.get('parameter') is not None else ''
        request = self.get_data_class('Request_')(header=header, parameter=parameter, binary=[])

        if not requestData.get('noreply', False):
            response_topic_name = topic.replace("/request", "/response")
            # Make sure the topic and reader are ready
            topic_instance = self._create_topic(response_topic_name, self.get_data_class('Response_'))
            if response_topic_name not in self.readers:
                self.readers[response_topic_name] = DataReader(self.participant, topic_instance)

            # Send the request
            self.publish(topic, request, self.get_data_class('Request_'))
            self.logger.info(f"Request sent to {topic} with id: {request_id}")

            # Polling for response
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                samples = self.readers[response_topic_name].take(N=1)
                for sample in samples:
                    if sample.sample_info.valid_data and sample.header.identity.id == request_id:
                        if sample.header.status.code == 0:
                            self.logger.info("Request successful with status code 0.")
                            return sample  # Return the whole response object if successful
                        else:
                            error_description = STATUS_CODE_ERROR_DESCRIPTIONS.get(sample.header.status.code, "Unknown error code")
                            self.logger.error(f"Request failed with status code {sample.header.status.code}: {error_description}")
                            return None
                        
            self.logger.error(f"Response from {response_topic_name} timed out")
        else:
            # Send the request without expecting a response
            self.publish(topic, request, self.get_data_class('Request_'))
            self.logger.info(f"Request sent with no reply expected to {topic} with id: {request_id}")
            return None

        return None
    



