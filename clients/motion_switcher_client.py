import json
import logging
from communicator.constants import SPORT_MODE_SWITCH_API_ID

logger = logging.getLogger(__name__)

class MotionSwitcher:
    """
    SportModeSwitcher: This class manages switching the high-level operational mode between normal and advanced.
    Certain maneuvers like Handstand, CrossStep, OnesidedStep, and Bound are only supported in the advanced mode,
    which requires firmware version 1.0.23 or later.
    """
    def __init__(self, communicator):
        self.communicator = communicator  
        self.sport_topic = self.communicator.get_topic_by_name("SPORT_MODE_SWITCHER")  

    async def doRequest(self, api_id, parameter=None, priority=0, noreply=False):
        requestData = {
            'api_id': api_id,
            'parameter': parameter,
            'priority': priority,
            'noreply': noreply
        }

        # Send the request and wait for a response if noreply is False
        response = await self.communicator.publishReq(self.sport_topic, requestData, timeout=2)

        # If noreply is True, just indicate that the request was sent
        if noreply:
            logger.info("Request sent with no reply expected.")
            return True

        # For reply-expected requests, directly return the response which is either None or contains the response data
        return response

    async def getSportMode(self):
        """
        Retrieve the current sport mode from the device and parse the mode details.
        """
        action_id = SPORT_MODE_SWITCH_API_ID["GetMode"] 
        response = await self.doRequest(action_id, noreply=False)
        parsed_parameters = {}

        if response:
            try:
                # Parse the JSON string within the 'data' attribute of the response
                response_data = json.loads(response.data)

                # Extract the 'form' and 'name' parameters
                parsed_parameters['form'] = response_data.get('form')
                parsed_parameters['name'] = response_data.get('name')

                logger.info(f"Successfully retrieved sport mode: {parsed_parameters}")
                return parsed_parameters
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response data: {e}")
                raise Exception(f"Failed to parse response data: {e}")
        else:
            logger.error("Failed to retrieve state or no response received.")
            return None
    
    async def setSportMode(self, mode):
        """
        Sends a request to set the sport mode of the device.
        Args:
            mode (str): The desired sport mode (e.g., 'normal', 'advanced').
        Returns:
            bool: True if the command was successful, False otherwise.
        """
        # Retrieve the API ID for setting the sport mode
        action_id = SPORT_MODE_SWITCH_API_ID["SetMode"]
        
        # Prepare the parameter to be sent; specify the mode name
        para = {"name": mode}
        
        # Send the request to the device and await the response
        response = await self.doRequest(action_id, parameter=para, noreply=False)
        
        # Check if the response was successful
        if response:
            # Log success with the action ID and mode set
            logger.info(f"Command to set mode to '{mode}' with api_id: {action_id} succeeded.")
            return True
        else:
            # Log failure with the action ID
            logger.error(f"Command with api_id: {action_id} failed or no response received.")
            return False
    
    async def releaseSportMode(self, flag=False, ack=False):
        """
        Disables both services: advanced_sport and sport_mode, If True then dumps imediatly, otherwise does a soft StandDown movement and proceed
        """

        # Convert the boolean flag to an integer to match the expected data format
        flag_int = 1 if flag else 0

        # Prepare the parameter for the control message
        para = {'sample': flag_int}

        action_id = SPORT_MODE_SWITCH_API_ID["ReleaseMode"]
      
        # Send the request to the device and await the response
        response = await self.doRequest(action_id, parameter=para, noreply=False)
        # Check if the response was successful
        if response:
            # Log success with the action ID and mode set
            logger.info(f"Command with api_id: {action_id} succeeded.")
            return True
        else:
            # Log failure with the action ID
            logger.error(f"Command with api_id: {action_id} failed or no response received.")
            return False

    async def setSilent(self, flag, ack=False):
        """
        Sets the silent mode. If true after the boot up none of the sport services would be launched. Perfect for developing stage

        Args:
            flag (bool): True to enable silent mode, False to disable it.
            ack (bool): If True, waits for an acknowledgment from the server.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        # Convert the boolean flag to an integer to match the expected data format
        flag_int = 1 if flag else 0

        # Prepare the parameter for the control message
        para = {'silent': flag_int}

        # Retrieve the action ID for the 'SetSilent' command from the API dictionary
        action_id = SPORT_MODE_SWITCH_API_ID["SetSilent"]

        # Send the request and check for an acknowledgment if required
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Log success with the action ID
            logger.info(f"Silent mode set command with api_id: {action_id} succeeded")
            return True
        else:
            # Log failure with the action ID
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False

    async def getSilent(self):
        """
        Retrieves the current state of the silent mode from the device. Have no clue what the silent mode is
        """
        action_id = SPORT_MODE_SWITCH_API_ID["GetSilent"]
        response = await self.doRequest(action_id, noreply=False)
        parsed_parameters = {}

        if response:
            try:
                # Parse the JSON string within the 'data' attribute of the response
                response_data = json.loads(response.data)

                parsed_parameters['silent'] = response_data.get("silent")

                logger.info(f"Successfully retrieved silent mode state: {parsed_parameters}")
                return parsed_parameters

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response data: {e}")
                raise Exception(f"Failed to parse response data: {e}")
        else:
            logger.error("Failed to retrieve silent state or no response received.")
            return False