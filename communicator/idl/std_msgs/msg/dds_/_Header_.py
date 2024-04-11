"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.10.2
  Module: std_msgs.msg.dds_
  IDL file: Header_.idl

"""

from enum import auto
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
import communicator.idl.std_msgs

if TYPE_CHECKING:
    import communicator.idl.builtin_interfaces.msg.dds_



@dataclass
@annotate.final
@annotate.autoid("sequential")
class Header_(idl.IdlStruct, typename="communicator.idl.std_msgs.msg.dds_.Header_"):
    stamp: 'communicator.idl.builtin_interfaces.msg.dds_.Time_'
    frame_id: str

