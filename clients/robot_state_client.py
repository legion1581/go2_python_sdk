import json
import logging
import asyncio

from dataclasses import dataclass
from .api import ROBOT_STATE_API_ID
from .pub_sub import Subscriber, PublishRequest


@dataclass
class RobotStateService_:
    name: str
    protect: bool
    status: bool
    version: str


class RobotStateClient():
    '''
    RobotStateClient acts as a client interface to the device state service. This client facilitates
    the control of internal services of the Go2 robot, and enables the retrieval of service and device statuses.
    '''
    default_service_name = 'robot_state_client'
    def __init__(self, communicator):
        # Instantiate communication interface (either DDS or WebRTC)    
        self.communicator = communicator       
        self.logger = logging.getLogger(__class__.__name__)  

        self.String_ = self.communicator.get_data_class('String_')

        # Initialize PublishRequest for sending specific requests
        self.robot_state_publisher = PublishRequest(
            communicator=self.communicator,
            topic_name='ROBOT_STATE_REQ',
            logger=self.logger
        )

        self.robot_state = []
        self.robot_state_subscriber = Subscriber(
            communicator=self.communicator,
            topic_name='SERVICE_STATE',
            callback = self.process_robot_state_update,
            data_class=self.String_,
            start_listening=True,
            logger=self.logger
        )

    def update_from(self, other):
        self.logger = other.logger.getChild(self.__class__.__name__)

    async def ServiceSwitch(self, name: str, switch: bool, ack: bool = True):
        """
        Toggle a specific service on or off based on the provided name and switch state.

        Args:
            name (str): The name of the service to be toggled.
            switch (bool): The desired state of the service (True for on, False for off).
            ack (bool): If True, waits for and checks the acknowledgment of the request.

        Returns:
            bool: True if the command was acknowledged as successful, False otherwise.
        """

        # Convert the boolean flag to an integer to match the expected data format
        switch_int = 1 if switch else 0

        # Parameters for the request
        para = {
            'name': name,
            'switch': switch_int
        }

        # Retrieve the API ID for toggling the service switch
        action_id = ROBOT_STATE_API_ID["ServiceSwitch"]
        # Send the request and process the response based on the acknowledgment flag
        response = await self.robot_state_publisher.doRequest(action_id, priority=1, parameter=para, noreply=not ack)
        if response:
            self.logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            self.logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False

    async def SetReportFreq(self, interval: int, duration: int, ack: bool = True):
        """
        Set the frequency and duration for reporting service status to rt/servicestate.

        Args:
            interval (int): The interval in seconds at which the service state should be published.
            duration (int): The total duration in seconds for which the state reports should be sent.
            ack (bool): If True, waits for and checks the acknowledgment of the request.

        Returns:
            bool: True if the command was acknowledged as successful, False otherwise.
        """

        # Parameters for setting the report frequency
        para = {
            'interval': interval,
            'duration': duration
        }

        # Retrieve the API ID for setting report frequency
        action_id = ROBOT_STATE_API_ID["SetReportFreq"]
        # Send the request and process the response based on the acknowledgment flag
        response = await self.robot_state_publisher.doRequest(action_id, priority=1, parameter=para, noreply=not ack)
        if response:
            self.logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            self.logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
        

    async def GetServiceList(self, ack: bool = True):
        """
        Not used. Abandoded. !!!Test it out!!!
        """
        # Retrieve the API ID for setting report frequency
        action_id = ROBOT_STATE_API_ID["GetServiceList"]
        # Send the request and process the response based on the acknowledgment flag
        response = await self.robot_state_publisher.doRequest(action_id, priority=1, noreply=not ack)
        if response:
            self.logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            self.logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False

    async def process_robot_state_update(self, data):
        """ Process incoming data and update robot state. """
        try:
            # Parse the JSON string from the data attribute of the incoming message
            services_data = json.loads(data.data)
            # Convert dictionaries to RobotStateService_ dataclass instances with inverted status
            self.robot_state = [
                RobotStateService_(
                    name=service['name'],
                    protect=bool(service['protect']),  # Convert to bool 
                    status=not bool(service['status']),  # Invert the status, idn why we get it inverted
                    version=service['version']
                ) for service in services_data
            ]
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON data.")
        except TypeError:
            self.logger.error("Incorrect data format for service creation.")


    async def fetch_service_status(self, service_name):
        """
        Retrieve the status of a service by its name.

        Args:
            service_name (str): The name of the service to look up.

        Returns:
            bool: The status of the service if found, otherwise None.
        """
        for service in self.robot_state:
            if service.name == service_name and service.status is not None:
                return service.status
        return None  # Return None if the service is not found

    async def fetch_service_status_with_timeout(self, service_name, timeout):
        """
        Retrieve the status of a service by its name, waiting until the status is non-None or timeout occurs.

        Args:
            service_name (str): The name of the service to look up.
            timeout (float): The maximum time in seconds to wait for a non-None status.

        Returns:
            bool: The status of the service if found and non-None, otherwise None after timeout.
        """
        end_time = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < end_time:
            for service in self.robot_state:
                if service.name == service_name and service.status is not None:
                    return service.status
        return None  # Timeout reached, return None


        



    


