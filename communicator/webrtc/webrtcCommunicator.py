from communicator.topics_and_errors import WEBRTC_TOPICS
from communicator.common import CommunicatorBase

class WebRTCCommunictor(CommunicatorBase):
    def __init__(self):
        pass
    def get_topic_by_name(self, name):
        return WEBRTC_TOPICS[name]
    