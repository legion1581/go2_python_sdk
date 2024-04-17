from cyclonedds.pub import DataWriter
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.core import Qos, Policy
from cyclonedds.util import duration
import time
import numpy as np

from communicator.idl.unitree_api.msg.dds_ import RequestIdentity_, RequestLease_, RequestPolicy_, RequestHeader_, Request_, Response_

domainParticipant = DomainParticipant(0)
qos = Qos(
    Policy.Reliability.Reliable(duration(microseconds=200)),
    Policy.Deadline(duration(microseconds=1000)),
    Policy.Durability.TransientLocal,
    Policy.History.KeepLast(10)
)
writer = DataWriter(domainParticipant, Topic(domainParticipant, "rt/api/sport/request", Request_, qos))

# Initial ID value
request_id = 0

time.sleep(1)

# This loop will send a new message every 1 second
while True:

    id = RequestIdentity_(request_id, 1016)  
    lease = RequestLease_(0)
    policy = RequestPolicy_(1, False)
    header = RequestHeader_(identity=id, lease=lease, policy=policy)
    req = Request_(header=header, parameter='' , binary=[0])

    print(req)

    writer.write(req)

    # Increment the request ID for the next message
    request_id += 1

    # Wait for 1 second before sending the next message
    time.sleep(0.1)
