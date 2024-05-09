
import logging

from .util import LowLevelCRC
from .pub_sub import Subscriber, Publisher

class BasicClient:
    default_service_name = 'low_level_client'

    def __init__(self, communicator, *args, **kwargs):
        self.communicator = communicator
        self.crc = LowLevelCRC()
        self.logger = logging.getLogger(__class__.__name__)
        self.sub_freq = kwargs.pop('sub_freq', 'HF')  # Default frequency to None if not provided

        self.LowCmd_=self.communicator.data_class_manager.get_data_class('LowCmd_')
        self.LowState_=self.communicator.data_class_manager.get_data_class('LowState_')

        # Initialize Publisher for sending requests
        self.low_cmd = self.communicator.data_class_manager.create_zeroed_dataclass(self.LowCmd_)
        self.low_cmd.head=b'\xfe\xef'
        self.low_cmd.level_flag=0xFF

        self.basic_publisher = Publisher(
            communicator=self.communicator,
            topic_name='LOW_CMD',
            data_class= self.LowCmd_,
            logger=self.logger
        )

        #Initialize Subscriber for listening to low state updates
        self.low_state = self.communicator.data_class_manager.create_zeroed_dataclass(self.LowState_)

        self.basic_subscriber = Subscriber(
            communicator=self.communicator,
            topic_name='LOW_STATE',
            frequency= self.sub_freq,
            callback = self.process_low_state_update,
            data_class=self.LowState_,
            start_listening=True,
            logger=self.logger
        )

    def update_from(self, other):
        """Update settings from another client instance."""
        self.logger = other.logger.getChild(self.__class__.__name__)
    
    def publish_with_crc(self):
         self.low_cmd.crc = self.crc.calc_crc_low_cmd(self.low_cmd)
         self.basic_publisher.write(self.low_cmd)

    #Subscriber handler
    async def process_low_state_update(self, data):
        """ Process incoming data and execute callbacks. """
        if self.crc.calc_crc_low_state(data) == data.crc:
            # self.low_state = data
            for attr, value in data.__dict__.items():
                setattr(self.low_state, attr, value)
        else:
            self.logger.error("CRC Mismatch")
