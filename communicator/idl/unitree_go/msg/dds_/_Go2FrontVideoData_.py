"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.10.2
  Module: unitree_go.msg.dds_
  IDL file: Go2FrontVideoData_.idl

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
class Go2FrontVideoData_(idl.IdlStruct, typename="communicator.idl.unitree_go.msg.dds_.Go2FrontVideoData_"):
    time_frame: types.uint64
    video720p: types.sequence[types.uint8]
    video360p: types.sequence[types.uint8]
    video180p: types.sequence[types.uint8]

