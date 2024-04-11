"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: geometry_msgs.msg.dds_
  IDL file: PoseWithCovariance_.idl

"""

from enum import auto
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
import communicator.idl.geometry_msgs


@dataclass
@annotate.final
@annotate.autoid("sequential")
class PoseWithCovariance_(idl.IdlStruct, typename="communicator.idl.geometry_msgs.msg.dds_.PoseWithCovariance_"):
    pose: 'communicator.idl.geometry_msgs.msg.dds_.Pose_'
    covariance: types.array[types.float64, 36]

