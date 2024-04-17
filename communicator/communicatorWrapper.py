# Common base class for PubSub and ReqRes communication
class CommunicatorWrapper:
    def publish(self, topic, data, data_type):
        raise NotImplementedError

    def subscribe(self, topic, data_type, callback):
        raise NotImplementedError
    
    def unsubscribe(self, topic):
        raise NotImplementedError

    async def publishReq (self, topic, requestData, timeout=5):
        raise NotImplementedError
    
    def get_topic_by_name(self, name):
        raise NotImplementedError