
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
    "OBSTACLES_AVOID_REQ": "rt/api/obstacles_avoid/request",
    "OBSTACLES_AVOID_RESPONSE": "rt/api/obstacles_avoid/response",
    "VUI_REQ": "rt/api/vui/request",
    "VUI_RESPONSE": "rt/api/vui/response",
    "GPT_REQ": "rt/api/gpt/request",
    "GPT_RESPONSE": "rt/api/gpt/response",
    "SPORT_MOD_REQ": "rt/api/sport/request",
    "SPORT_RESPONSE": "rt/api/sport/response",
    "ROBOT_STATE_REQ": "rt/api/robot_state/request",
    "ROBOT_STATE_RESPONSE": "rt/api/robot_state/response",
    "AUDIO_HUB_REQ": "rt/api/audiohub/request",
    "AUDIO_HUB_RESPONSE": "rt/api/audiohub/response",
    "CONFIG_REQ": "rt/api/config/request",
    "CONFIG_RESPONSE": "rt/api/config/response",
    "SPORT_MODE_SWITCHER_REQ": "rt/api/motion_switcher/request",
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
    "LOW_CMD": "rt/lowcmd"
}

# Combine WebRTC topics with DDS-specific topics for comprehensive DDS topics
DDS_TOPICS = {**WEBRTC_TOPICS, **DDS_ONLY_TOPICS}

STATUS_CODE_ERROR_DESCRIPTIONS = {
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
    4101: "Wrong number of trajectory points, returned by the client",
    5201: "Service switch execution error",
    5202: "The service is protected and cannot be turned on or off"
    }