from communicator.constants import WEBRTC_TOPICS
from communicator.communicatorWrapper import CommunicatorWrapper

class WebRTCCommunictor(CommunicatorWrapper):
    def __init__(self):
        pass
    def get_topic_by_name(self, name):
        return WEBRTC_TOPICS[name]
    