import logging
from .robot import Robot
from .sport_client import SportClient
from .basic_client import BasicClient
from .robot_state_client import RobotStateClient
from .sport_switcher_client import SportSwitcherClient

__LOGGER = logging.getLogger(__name__)

_DEFAULT_SERVICE_CLIENTS = [
    SportClient, 
    SportSwitcherClient, 
    BasicClient, 
    # ObstacleAvoidanceClient,
    RobotStateClient, 
    # BashRunnerClient, 
    # VuiClient, 
    # HandheldRemoteControllerClient,
    # UWBClient, 
    # LidarClient, 
    # FaultClient, 
    # ConfigClient, 
    # WebRTCClient, 
    # SLAMClient,
    # ArmClient, 
    # ChatGPTClient, 
    # AudioClient, 
    # ImageClient, 
    # NetworkClient
]

def create_standard_sdk(client_name_prefix, service_clients=None):
    __LOGGER.debug("Creating standard SDK")
    sdk = Sdk(name=client_name_prefix)

    all_service_clients = list(_DEFAULT_SERVICE_CLIENTS)
    if service_clients:
        all_service_clients.extend(service_clients)
    for client_class in all_service_clients:
        sdk.register_service_client(client_class)
    return sdk

class Sdk:
    """
    Repository for settings typically common to a single developer and/or robot fleet.
    """
    def __init__(self, name=None, logger=None):
        self.logger = logger or logging.getLogger(name or __class__.__name__)
        self.client_name = name
        self.service_client_factories_by_name={}
        self.robots = {}

    def create_robot(self, communicator, serialNumber=None, name=None):
        # Placeholder for implementation to create a robot instance
        self.logger.debug(f"Creating robot {serialNumber}")
        if not serialNumber:
            raise ValueError("Robot serial cannot be None")

        if serialNumber in self.robots:
            return self.robots[serialNumber]
        
        robot = Robot(communicator, serialNumber, name)

        robot.update_from(self)
        self.robots[serialNumber] = robot

        return robot
        
    
    def delete_robot(self, name):
        """
        Deletes a robot instance from the SDK by its name.

        Args:
            name (str): The name of the robot to be deleted.

        Raises:
            ValueError: If the name is None or empty.
            KeyError: If no robot with the given name exists in the registry.
        """
        self.logger.debug(f"Attempting to delete robot {name}")
        if not name:
            raise ValueError("Robot name cannot be None or empty")  # Check for empty string too

        if name in self.robots:
            del self.robots[name]
            self.logger.debug(f"Robot {name} deleted successfully")
        else:
            # Optionally raise an error if trying to delete a robot that does not exist
            self.logger.error(f"No robot found with the name {name}")
            raise KeyError(f"No robot found with the name {name}")
    
    
    def clear_robots(self):
        """Remove all cached Robot instances.
        Subsequent calls to create_robot() will return newly created Robots.
        Existing robot instances will continue to work, but their time sync and token refresh
        threads will be stopped.
        """
        self.robots = {}


    def register_service_client(self, client_class):
        """Registers a service client in the SDK."""
        service_name = getattr(client_class, 'default_service_name', None)
        if service_name and service_name not in self.service_client_factories_by_name:
            self.service_client_factories_by_name[service_name] = client_class
            self.logger.debug(f"Registered service client factory for {service_name}")
        else:
            self.logger.warning(f"Service client {service_name} is already registered or has no default service name.")



