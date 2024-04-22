DDS_ERROR_DESCRIPTIONS = {
    3001: "Unknown error",
    3102: "Request sending error",
    3103: "API not registered",
    3104: "Request timeout",
    3105: "Request and response data do not match",
    3106: "Invalid response data",
    3107: "Invalid lease",
    3201: "Response sending error",
    3202: "Internal server error",
    3203: "API not implemented on the server",
    3204: "API parameter error",
    3205: "Request rejected",
    3206: "Invalid lease",
    3207: "Lease already exists",
    }

SPORT_CLIENT_API_ID = {
    "Damp": 1001,
    "BalanceStand": 1002,
    "StopMove": 1003,
    "StandUp": 1004,
    "StandDown": 1005,
    "RecoveryStand": 1006,
    "Euler": 1007,
    "Move": 1008,
    "Sit": 1009,
    "RiseSit": 1010,
    "SwitchGait": 1011,
    "Trigger": 1012,
    "BodyHeight": 1013,
    "FootRaiseHeight": 1014,
    "SpeedLevel": 1015,
    "Hello": 1016,
    "Stretch": 1017,
    "TrajectoryFollow": 1018,
    "ContinuousGait": 1019,
    "Content": 1020, #API not implemented on the server
    "Wallow": 1021,
    "Dance1": 1022,
    "Dance2": 1023,
    "GetBodyHeight": 1024, #API not implemented on the server
    "GetFootRaiseHeight": 1025, #API not implemented on the server
    "GetSpeedLevel": 1026, #API not implemented on the server
    "SwitchJoystick": 1027, #NOT WORKING use bash_runner_client instead!!!
    "Pose": 1028,
    "Scrape": 1029,
    "FrontFlip": 1030,
    "FrontJump": 1031,
    "FrontPounce": 1032,
    "WiggleHips": 1033,
    "GetState": 1034,
    "EconomicGait": 1035,
    "FingerHeart": 1036,
    "Handstand": 1301,
    "CrossStep": 1302,
    "OnesidedStep": 1303,
    "Bound": 1304,
    "LeadFollow": 1045    
}

SPORT_MODE_SWITCH_API_ID = {
    "GetMode": 1001,
    "SetMode": 1002,
    "ReleaseMode": 1003,
    "SetSilent": 1004,
    "GetSilent": 1005
}

#Topics only available through WebRTC (however will work through DDS)

WEBRTC_TOPICS = {
    # General Device Control and Configuration
    "RTC_STATUS": "rt/rtc_status",
    "RTC_STATE": "rt/rtc/state",
    "SERVICE_STATE": "rt/servicestate",
    "SERVICE_STATE_ACTIVATE": "rt/servicestateactivate",
    "PUBLIC_NETWORK_STATUS": "rt/public_network_status",

    # API Requests and Responses
    "VIDEOHUB_INNER": "rt/videohub/inner",
    "FRONT_PHOTO_REQ": "rt/api/videohub/request",
    "VIDEOHUB_RESPONSE": "rt/api/videohub/response",
    "UWB_REQ": "rt/api/uwbswitch/request",
    "UWB_RESPONSE": "rt/api/uwbswitch/response",
    "BASH_REQ": "rt/api/bashrunner/request",
    "BASH_RESPONSE": "rt/api/bashrunner/response",
    "OBSTACLES_AVOID": "rt/api/obstacles_avoid/request",
    "OBSTACLES_AVOID_RESPONSE": "rt/api/obstacles_avoid/response",
    "VUI": "rt/api/vui/request",
    "VUI_RESPONSE": "rt/api/vui/response",
    "GPT": "rt/api/gpt/request",
    "GPT_RESPONSE": "rt/api/gpt/response",
    "SPORT_MOD": "rt/api/sport/request",
    "SPORT_RESPONSE": "rt/api/sport/response",
    "ROBOT_STATE_REQ": "rt/api/robot_state/request",
    "ROBOT_STATE_RESPONSE": "rt/api/robot_state/response",
    "AUDIO_HUB_REQ": "rt/api/audiohub/request",
    "AUDIO_HUB_RESPONSE": "rt/api/audiohub/response",
    "CONFIG_REQ": "rt/api/config/request",
    "CONFIG_RESPONSE": "rt/api/config/response",
    "SPORT_MODE_SWITCHER": "rt/api/motion_switcher/request",
    "SPORT_MODE_SWITCHER_RESPONSE": "rt/api/motion_switcher/response",
    "GAS_SENSOR_REQ": "rt/api/gas_sensor/request",
    "GAS_SENSOR_RESPONSE": "rt/api/gas_sensor/response",

    # SLAM and Mapping
    "SLAM_QT_COMMAND": "rt/qt_command",
    "SLAM_ADD_NODE": "rt/qt_add_node",
    "SLAM_ADD_EDGE": "rt/qt_add_edge",
    "SLAM_QT_NOTICE": "rt/qt_notice",
    "SLAM_PC_TO_IMAGE_LOCAL": "rt/pctoimage_local",
    "SLAM_ODOMETRY": "rt/lio_sam_ros2/mapping/odometry",

    # Query and Feedback
    "QUERY_RESULT_NODE": "rt/query_result_node",
    "QUERY_RESULT_EDGE": "rt/query_result_edge",
    "GPT_FEEDBACK": "rt/gptflowfeedback",

    # Sensor Data
    "ULIDAR_SWITCH": "rt/utlidar/switch",
    "ULIDAR_ARRAY": "rt/utlidar/voxel_map_compressed",
    "ULIDAR_STATE": "rt/utlidar/lidar_state",
    "ROBOTODOM": "rt/utlidar/robot_pose",
    "UWB_STATE": "rt/uwbstate",

    # Device State
    "MULTIPLE_STATE": "rt/multiplestate",
    "LOW_STATE_LF": "rt/lf/lowstate",
    "SPORT_MOD_STATE_LF": "rt/lf/sportmodestate",
    "AUDIO_HUB_PLAY_STATE": "rt/audiohub/player/state",
    "SELF_TEST": "rt/selftest",
    "GAS_SENSOR": "rt/gas_sensor",

    # Arm Commands and Feedback
    "ARM_COMMAND": "rt/arm_Command",
    "ARM_FEEDBACK": "rt/arm_Feedback",

    # Wireless Controller
    "WIRELESS_CONTROLLER": "rt/wirelesscontroller",
}


DDS_ONLY_TOPICS = {
    "SPORT_MOD_STATE": "rt/sportmodestate",
    "SPORT_MOD_STATE_MF": "rt/mf/sportmodestate",
    "ULIDAR": "rt/utlidar/voxel_map",
    "LOW_STATE": "rt/lowstate",
}

# Combine WebRTC topics with DDS-specific topics for comprehensive DDS topics
DDS_TOPICS = {**WEBRTC_TOPICS, **DDS_ONLY_TOPICS}