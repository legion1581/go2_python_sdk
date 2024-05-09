import logging

class Robot:
    def __init__(self, communicator, serialNumber=None, name=None):
        self._name = name
        self.serialNumber = serialNumber
        self.logger = logging.getLogger(self._name or self.serialNumber)
        self.communicator = communicator
        self.communicator.update_from(self)
        self.client_name = None
        
        # Updated from sdk object
        self.service_client_instance_by_name = {}
        self.service_client_factories_by_name={}
        
    def ensure_client(self, service_name, *args, **kwargs):
        """
        Ensure a Client for a given service. If the client does not exist, create it using the factory.

        Args:
            service_name (str): The name of the service.
            client_factory (callable): A factory function or lambda to create a new client if one does not exist.

        Returns:
            The client instance associated with the given service name.

        Raises:
            ValueError: If the client_factory is not provided and the client does not exist.
        """
        client = self.service_client_instance_by_name.get(service_name)
        if not client:
            client_factory = self.service_client_factories_by_name.get(service_name)
            if client_factory:
                client = client_factory(self.communicator, *args, **kwargs)
                self.service_client_instance_by_name[service_name] = client
                self.logger.debug(f'Created client for {service_name}')
            else:
                raise ValueError(f"No client factory available for {service_name}")
        client.update_from(self)
        return client
    
    def update_from(self, other):
        """
        Update this robot's service clients and configuration from another robot or a similar object.

        Args:
            other (Robot): Another robot object whose configurations and clients will be copied.
        """
        self.service_client_factories_by_name.update(other.service_client_factories_by_name)
        self.logger = other.logger.getChild(self._name or self.serialNumber)
        self.client_name = other.client_name

