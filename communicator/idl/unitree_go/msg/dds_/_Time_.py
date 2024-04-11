"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: unitree_go.msg.dds_
  IDL file: Time_.idl

"""

from enum import auto
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
import communicator.idl.unitree_go


@dataclass
@annotate.final
@annotate.autoid("sequential")
class Time_(idl.IdlStruct, typename="communicator.idl.unitree_go.msg.dds_.Time_"):
    sec: types.int32
    nanosec: types.uint32


