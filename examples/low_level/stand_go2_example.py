import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from communicator.cyclonedds.ddsCommunicator import DDSCommunicator
from clients.basic_client import BasicClient
import clients.util

class StandUp:
    def __init__(self, basic_client: BasicClient):
        self.basic_client = basic_client
        self.logger = basic_client.logger
        self.low_cmd = basic_client.low_cmd
        self.low_state = basic_client.low_state
        self.basic_pub = basic_client.basic_publisher
        self.motion_time = 0
        self.first_run = True
        self.done = False
        self.percent_1 = 0
        self.percent_2 = 0
        self.percent_3 = 0
        self.percent_4 = 0
        self.duration_1 = 500
        self.duration_2 = 500
        self.duration_3 = 1000
        self.duration_4 = 900
        self.start_pos = [0] * 12  # Assuming 12 joints
        self.Kp = 60.0
        self.Kd = 5.0
        self.target_pos_1 = [0.0, 1.36, -2.65, 0.0, 1.36, -2.65, -0.2, 1.36, -2.65, 0.2, 1.36, -2.65]
        self.target_pos_2 = [0.0, 0.67, -1.3, 0.0, 0.67, -1.3, 0.0, 0.67, -1.3, 0.0, 0.67, -1.3]
        self.target_pos_3 = [-0.35, 1.36, -2.65, 0.35, 1.36, -2.65, -0.5, 1.36, -2.65, 0.5, 1.36, -2.65]

        for j in range(12):
            self.low_cmd.motor_cmd[j].mode = 0x01
            self.low_cmd.motor_cmd[j].q = 2.146E+9
            self.low_cmd.motor_cmd[j].dq = 16000.0



    async def update_low_level_values(self):
        if self.done:
            return
        
        if self.percent_4 < 1:
            self.logger.info("Read sensor data example:")
            self.logger.info(f"Joint 0 pos: {self.low_state.motor_state[0].q}")
            self.logger.info(f"Imu accelerometer: x: {self.low_state.imu_state.accelerometer[0]} y: {self.low_state.imu_state.accelerometer[1]} z: {self.low_state.imu_state.accelerometer[2]}")
            self.logger.info(f"Foot force: {self.low_state.foot_force}")

        self.motion_time += 1
        if self.motion_time >= 500:
            if self.first_run:
                self.start_pos = [self.low_state.motor_state[i].q for i in range(12)]
                self.first_run = False

            self.percent_1 += 1 / self.duration_1
            self.percent_1 = min(self.percent_1, 1)
            if self.percent_1 < 1:
                for j in range(12):
                    # Assuming low_cmd is a class that has motor_cmd which is a list of commands
                    self.low_cmd.motor_cmd[j].q = (1 - self.percent_1) * self.start_pos[j] + self.percent_1 * self.target_pos_1[j]
                    self.low_cmd.motor_cmd[j].dq = 0
                    self.low_cmd.motor_cmd[j].kp = self.Kp
                    self.low_cmd.motor_cmd[j].kd = self.Kd
                    self.low_cmd.motor_cmd[j].tau = 0

            if self.percent_1 == 1 and self.percent_2 < 1:
                self.percent_2 += 1 / self.duration_2
                self.percent_2 = min(self.percent_2, 1)
                for j in range(12):
                    self.low_cmd.motor_cmd[j].q = (1 - self.percent_2) * self.target_pos_1[j] + self.percent_2 * self.target_pos_2[j]

            # remain in the standing position for a while
            if self.percent_1 == 1 and self.percent_2 == 1 and self.percent_3 < 1:
                self.percent_3 += 1 / self.duration_3
                self.percent_3 = min(self.percent_3, 1)
                for j in range(12):
                    self.low_cmd.motor_cmd[j].q = self.target_pos_2[j]

            if self.percent_1 == 1 and self.percent_2 == 1 and self.percent_3 == 1 and self.percent_4 <= 1:
                self.percent_4 += 1 / self.duration_4
                self.percent_4 = min(self.percent_4, 1)
                for j in range(12):
                    self.low_cmd.motor_cmd[j].q = (1 - self.percent_4) * self.target_pos_2[j] + self.percent_4 * self.target_pos_3[j]
            
            if self.percent_4 == 1 and not self.done:
                self.logger.info("The example is done!")
                self.done = True

            self.basic_client.publish_with_crc()

async def main():

    # Set up a logger with verbose output enabled. This allows for detailed logging output which can be useful for debugging.
    clients.util.setup_logging(verbose=False)

    # Initialize the SDK with a custom name, which is used to identify the SDK instance and its associated logs.
    sdk = clients.create_standard_sdk('UnitreeGo2SDK')

    # Create a robot instance using the DDS protocol. 
    # `domainId=0` is used as it is currently the standard for all Go2 robots, although a script to change this on the robot is planned.
    # `interface="eth0"` specifies the network interface the DDS should use.
    # Each robot is uniquely identified by a serial number, allowing for multiple robots to be managed by the SDK.
    robot = sdk.create_robot(DDSCommunicator(domainId=45, interface="wlan1"), serialNumber='B42D2000NCS8JJ82')

    # Instantiate the BasicClient
    # The `ensure_client` method checks if the client exists and creates it if not, ensuring that the robot can use this client.
    robot_basic_client : BasicClient = robot.ensure_client(BasicClient.default_service_name, sub_freq='HF')
    # rs = RobotState(communicator)

    # await rs_cmd.SetReportFreq(1, 60)

    # while (rs.get_service_status("sport_mode")):
    #     await rs_cmd.ServiceSwitch("sport_mode", False)
    #     await asyncio.sleep(1)

    standup = StandUp(robot_basic_client)

    async def update_task():
        await standup.update_low_level_values()

    timer = clients.util.PeriodicTask(robot_basic_client.logger)
    await timer.start(2, update_task)

    # Keep the main coroutine alive long enough to observe results (adjust as necessary)
    await asyncio.sleep(120)  # Run for 2 minutes for demonstration purposes
if __name__ == "__main__":
    asyncio.run(main())
    

    
    

