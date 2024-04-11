# Unofficial Python SDK for Unitree Go2

This is an Unofficial Python SDK designed to interface with the Unitree Go2 robots, offering support for various models including AIR, PRO, and EDU. It provides a high-level API for interacting with the robots using cycloneDDS middleware or Webrtc, ensuring wide compatibility and easy integration. WebRTC is not yet implemented.

## Features

- **Multiple Client Support**: Includes `sport_client`, `basic_client`, `vui_client`, `robotstate_client`, and `lidar_client` to cover a wide range of functionalities.
- **Compatibility**: Works with AIR, PRO, and EDU models, ensuring a broad usage scope.
- **Flexible Communication**: Supports cycloneDDS middleware and Webrtc for communication, providing options based on your project needs.

## Roadmap

- [x] `sport_client` - Control and manage robot movements.
- [ ] `basic_client` - Support for lowlevel commands.
- [ ] `vui_client` - Voice control interfaces.
- [ ] `robotstate_client` - Stop/launch robot services .
- [ ] `lidar_client` - Interface with the robot's LiDAR system for mapping and navigation.

## Getting Started

This section should provide a quick guide on how to set up and start using the SDK.

### Prerequisites

List any prerequisites here, such as Python version, dependencies, etc.

### Installation

Provide step-by-step instructions to install the SDK, for example:

```bash
git clone https://github.com/legion1581/go2_python_sdk.git
cd unitree-go2-python-sdk
pip install -r requirements.txt
```

### Thanks

To TheRoboVerse community! Visit us at theroboverse.com for more information and support.