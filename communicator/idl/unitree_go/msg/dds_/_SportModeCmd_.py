"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.10.2
  Module: unitree_go.msg.dds_
  IDL file: SportModeCmd_.idl

"""

from enum import auto
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
import unitree_go


@dataclass
@annotate.final
@annotate.autoid("sequential")
class SportModeCmd_(idl.IdlStruct, typename="unitree_go.msg.dds_.SportModeCmd_"):
    mode: types.uint8
    gait_type: types.uint8
    speed_level: types.uint8
    foot_raise_height: types.float32
    body_height: types.float32
    position: types.array[types.float32, 2]
    euler: types.array[types.float32, 3]
    velocity: types.array[types.float32, 2]
    yaw_speed: types.float32
    bms_cmd: 'unitree_go.msg.dds_.BmsCmd_'
    path_point: types.array['unitree_go.msg.dds_.PathPoint_', 30]


