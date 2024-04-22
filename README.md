# Unofficial Python SDK for Unitree Go2

This is an unofficial Python SDK designed to interface with the Unitree Go2 robots, supporting various models including AIR, PRO, and EDU. It provides a high-level API for interacting with the robots using CycloneDDS middleware or WebRTC, ensuring broad compatibility and easy integration. Note that WebRTC is not yet implemented.

### CycloneDDS Driver(Implemented)

CycloneDDS is an open-source implementation of the Data Distribution Service (DDS) standard, which is a middleware protocol used by Unitree Go2.

* CycloneDDS works out of the box only with the EDU version.
* For use with AIR/PRO models, a custom firmware upgrade is required. Please visit theroboverse.com and our Discord group for more details.

### WebRTC Driver (Not yet implemented)

WebRTC (Web Real-Time Communication) is an open-source project and technology that enables real-time communication of audio, video, and data directly within web browsers and mobile applications. Internally, the robot includes a webrtc_bridge that converts WebRTC to DDS. The Unitree Go2 app uses WebRTC as a transport layer.

* Works with AIR, PRO, and EDU models out of the box, but is limited to topics when publishing/subscribing. For example, low-level commands would not work fully as rt/lowcmd is not supported. Reading is only supported through rt/lf/lowstate (lf for low frequency).


## Features

- **Multiple Client Support**: Includes `sport_client`, `basic_client`, `vui_client`, `robotstate_client`, and `lidar_client` to cover a wide range of functionalities.
- **Compatibility**: Works with AIR, PRO, and EDU models, ensuring a broad usage scope.
- **Flexible Communication**: Supports cycloneDDS middleware and Webrtc for communication, providing options based on your project needs.

## Roadmap

- [x] `sport_client` - Control and manage robot movements.
- [x] `motion_swither_client` - Support for switching between normal and advanced sport modes
- [ ] `basic_client` - Support for lowlevel commands.
- [ ] `vui_client` - Voice control interfaces.
- [ ] `robotstate_client` - Stop/launch robot services .
- [ ] `audio_client` - Audio interfaces.
- [ ] `photo_client` - Photo interfaces.
- [ ] `lidar_client` - Interface with the robot's LiDAR system for mapping and navigation.

### Installation

Follow these step-by-step instructions to install the SDK:

```bash
git clone https://github.com/legion1581/go2_python_sdk.git
cd go2_python_sdk
pip install -r requirements.txt
```

### Thanks

To TheRoboVerse community! Visit us at theroboverse.com for more information and support.