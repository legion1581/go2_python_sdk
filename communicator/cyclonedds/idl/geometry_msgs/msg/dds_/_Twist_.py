"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: geometry_msgs.msg.dds_
  IDL file: Twist_.idl

"""

from enum import auto
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
import geometry_msgs


@dataclass
@annotate.final
@annotate.autoid("sequential")
class Twist_(idl.IdlStruct, typename="geometry_msgs.msg.dds_.Twist_"):
    linear: 'geometry_msgs.msg.dds_.Vector3_'
    angular: 'geometry_msgs.msg.dds_.Vector3_'

