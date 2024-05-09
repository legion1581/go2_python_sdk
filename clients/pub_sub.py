import asyncio
import logging
from .util import PeriodicTask 

class Subscriber:
    """
    Helper Subscriber class
    """

    def __init__(self, communicator, topic_name, data_class, frequency=None, callback=None, logger=None, start_listening=True, ):

        self.communicator = communicator
        self.topic_name = topic_name
        self.topic = self.get_topic_name(frequency)
        self.data_class = data_class
        self.start_listening = start_listening
        self.callbacks = set()
        self.listening = False

        # Initialize or use an existing logger dynamically with the class name
        self.logger = logger.getChild(self.__class__.__name__) if logger else logging.getLogger(__name__)

        if callback:
            self.add_callback(callback)

        if self.start_listening and not self.listening:
            asyncio.create_task(self._start_listening())

    def add_callback(self, callback):
        self.callbacks.add(callback)
        if not self.listening:
            asyncio.create_task(self._start_listening())

    def remove_callback(self, callback):
        self.callbacks.discard(callback)
        if not self.callbacks and self.listening:
            asyncio.create_task(self._stop_listening())
        
    def get_topic_name(self, frequency):
        if frequency is None:
            return self.communicator.get_topic_by_name(f"{self.topic_name}")
        
        # Validate that frequency is one of the expected values
        valid_frequencies = ['MF', 'HF', 'LF']
        frequency = frequency.upper()  # Normalize input to uppercase to ensure case insensitivity
        if frequency not in valid_frequencies:
            raise ValueError(f"Invalid frequency '{frequency}'. Expected one of {valid_frequencies}")

        # Apply conditional logic for topic name suffix
        if frequency == 'HF':
            suffix = ''  # No suffix for 'HF'
        elif frequency == 'LF':
            suffix = '_LF'
        elif frequency == 'MF':
            suffix = '_MF'

        # Construct and return the topic name with the appropriate suffix
        return self.communicator.get_topic_by_name(f"{self.topic_name}{suffix}")

    async def _process_data(self, data):
        """Process incoming data using callbacks. To be overridden or handled via callbacks."""
        await asyncio.gather(*(callback(data) for callback in self.callbacks))

    async def _start_listening(self):
        if not self.listening:
            self.communicator.subscribe(self.topic, self.data_class, self._process_data)
            self.listening = True

    async def _stop_listening(self):
        if self.listening:
            self.communicator.unsubscribe(self.topic)
            self.listening = False
            self.logger.info(f"Unsubscribed from {self.topic}")


class Publisher:
    def __init__(self, communicator, topic_name, data_class, logger=None):
        self.communicator = communicator
        self.topic_name = topic_name
        self.data_class = data_class
        self.topic = self.communicator.get_topic_by_name(self.topic_name)
        # Initialize or use an existing logger dynamically with the class name
        self.logger = logger.getChild(self.__class__.__name__) if logger else logging.getLogger(__name__)
        self.periodic_task = PeriodicTask(self.logger)

    async def start_publishing(self, frequency, data):
        await self.periodic_task.start(1 / frequency, self.write, data)

    async def stop_publishing(self):
        if self.publish_task and not self.publish_task.done():
            await self.periodic_task.stop()

    def write(self, data):
        self.communicator.publish(self.topic, data, self.data_class)
        self.logger.debug(f"Data published to {self.topic}")

    
class PublishRequest:
    def __init__(self, communicator, topic_name, logger=None):
        self.communicator = communicator
        self.topic_name = topic_name
        self.topic = self.communicator.get_topic_by_name(self.topic_name)

        # Initialize or use an existing logger dynamically with the class name
        self.logger = logger.getChild(self.__class__.__name__) if logger else logging.getLogger(__name__)
        self.periodic_task = PeriodicTask(self.logger)

    async def doRequest(self, api_id, parameter=None, priority=0, noreply=True):

        requestData = {
        'api_id': api_id,
        'parameter': parameter,
        'priority': priority,
        'noreply' : noreply
        }

        # Send the request and wait for a response if noreply is False
        response = await self.communicator.publishReq(self.topic, requestData, timeout=2)

        # If noreply is True, just indicate that the request was sent
        if noreply:
            self.logger.info("Request sent with no reply expected.")
            return True

        # For reply-expected requests, directly return the response which is either None or contains the response data
        return response


