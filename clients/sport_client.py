import json
import logging
import math
import asyncio
from communicator.constants import ROBOT_CMD
from communicator.idl.unitree_go.msg.dds_ import SportModeState_

logging.basicConfig(level=logging.DEBUG)  # Set the desired level
logger = logging.getLogger(__name__)

class SportClient():
    def __init__(self, communicator):
        # Instantiate communication interface (either DDS or WebRTC)    
        self.communicator = communicator      
        self.sport_topic = self.communicator.get_topic_by_name("SPORT_MOD")    

    async def doRequest(self, api_id, parameter=None, priority=0, noreply=True):

        requestData = {
        'api_id': api_id,
        'parameter': parameter,
        'priority': priority,
        }

        # Send the request and wait for a response if noreply is False
        response = await self.communicator.publishReq(self.sport_topic, requestData, timeout=5) if not noreply else None

        # If noreply is True, just indicate that the request was sent
        if noreply:
            logger.info("Request sent with no reply expected.")
            return True

        # For reply-expected requests, directly return the response which is either None or contains the response data
        return response


    async def Damp(self, ack=True):
        """
        All motor joints stop moving and enter a damping state. 
        This mode has the highest priority and is used for emergency stops in unexpected situations
        """
        action_id = ROBOT_CMD["Damp"]
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False

    async def BalanceStand(self, ack=False):
        """
        Unlock the joint motor and switch from normal standing mode to balanced standing mode.
        In this mode, the attitude and height of the fuselage will always remain balanced, independent of the terrain. 
        You can control the font and height of the body by calling the Euler() and BodyHeight() 
        interfaces (see the corresponding section of the table for details)
        """
        action_id = ROBOT_CMD["BalanceStand"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def StopMove(self, ack=False):
        """
        Stop the current motion and restore the internal motion parameters of Go2 to the default values
        """
        action_id = ROBOT_CMD["StopMove"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def StandUp(self, ack=False):
        """
        The machine dog is standing tall normally, and the motor joint remains locked. 
        Compared to the balanced standing mode, the posture of the robotic dog in this mode will not always maintain balance.
        The default standing height is 0.33m
        """
        action_id = ROBOT_CMD["StandUp"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def StandDown(self, ack=False):
        """
        The robotic dog lies down and the motor joint remains locked
        """
        action_id = ROBOT_CMD["StandDown"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def RecoveryStand(self, ack=False):
        """
        Restore from a overturned or lying state to a balanced standing state. 
        Whether it is overturned or not, it will return to standing
        """
        action_id = ROBOT_CMD["RecoveryStand"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Euler(self, args, units='degrees', ack=False):
        """
        Set the body posture angle for Go2 balance when standing or moving.
        The Euler angle is represented by the rotation order around the relative axis of the body and z-y-x

        Parameters:
            args (dict): A dictionary containing the roll, pitch, and yaw angles.
                - roll: Rotation around the front-to-back axis.
                - pitch: Rotation around the side-to-side axis.
                - yaw: Rotation around the vertical axis.
            units (str): The unit of the angles ('degrees' or 'radians'). Defaults to 'degrees'.
                When using radians, the value range is:
                - roll: [-0.75, 0.75]
                - pitch: [-0.75, 0.75]
                - yaw: [-0.6, 0.6]
        """

        # Ensure roll, pitch, and yaw keys exist in args with a default value of 0 if absent
        roll = float(args.get('roll', 0))
        pitch = float(args.get('pitch', 0))
        yaw = float(args.get('yaw', 0))

        # Convert degrees to radians if necessary
        if units == 'degrees':
            roll = math.radians(roll)
            pitch = math.radians(pitch)
            yaw = math.radians(yaw)
        else:  # Validate ranges for radians
            if not (-0.75 <= roll <= 0.75):
                raise ValueError("Roll angle is out of the valid range [-0.75, 0.75] radians.")
            if not (-0.75 <= pitch <= 0.75):
                raise ValueError("Pitch angle is out of the valid range [-0.75, 0.75] radians.")
            if not (-0.6 <= yaw <= 0.6):
                raise ValueError("Yaw angle is out of the valid range [-0.6, 0.6] radians.")

        para = {
            'x': roll,  # roll angle in radians
            'y': pitch,  # pitch angle in radians
            'z': yaw  # yaw angle in radians
        }

        action_id = ROBOT_CMD["Euler"] 
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Move(self, args, ack=False):
        """
        Control movement speed. The set speed is the speed represented by the body coordinate system

        Parameters:
            args (dict): A dictionary containing the x, y, z speeds.
                - x: Linear velocity in the x direction (m/s). Value range: [-2.5, 5].
                - y: Linear velocity in the y direction (m/s). Value range: [-2.5, 5].
                - z: Angular velocity around the z-axis (rad/s). Value range: [-4, 4].
        """
        # Ensure x, y, and z keys exist in args with a default value of 0 if absent
        x = float(args.get('x', 0))
        y = float(args.get('y', 0))
        z = float(args.get('z', 0))

        # Validate the speed ranges
        if not (-2.5 <= x <= 5):
            raise ValueError("x speed is out of the valid range [-2.5, 5].")
        if not (-2.5 <= y <= 5):
            raise ValueError("y speed is out of the valid range [-2.5, 5].")
        if not (-4 <= z <= 4):
            raise ValueError("z speed is out of the valid range [-4, 4].")

        # Speed parameters
        para = {
            'x': x,  # Linear velocity in the x direction
            'y': y,  # Linear velocity in the y direction
            'z': z   # Angular velocity around the z-axis
        }

        action_id = ROBOT_CMD["Move"] 
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Sit(self, ack=False):
        """
        Special action, robot dog sitting down. 
        It should be noted that special actions need to be executed after the previous action is completed, otherwise it may result in abnormal actions
        """
        action_id = ROBOT_CMD["Sit"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def RiseSit(self, ack=False):
        """
        Restore from sitting to balanced standing
        """
        action_id = ROBOT_CMD["RiseSit"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def SwitchGait(self, d, ack=False):
        """
        The forward climbing mode is for the robot to face the stairs,
        while the reverse climbing mode is for the robot to face the stairs with its back.

        Parameters:
        d (int): Gait enumeration value, with values ranging from 0 to 4, where 
                0 is idle, 1 is trot, 2 is trot running, 3 is forward climbing mode, 
                and 4 is reverse climbing mode.
        """
        # Ensure 'd' is within the valid range
        if not 0 <= d <= 4:
            raise ValueError("Gait enumeration value 'd' must be between 0 and 4.")

        para = {'data': d}

        action_id = ROBOT_CMD["SwitchGait"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Trigger(self, ack=False):
        """
        Have no clue what the method does
        """
        action_id = ROBOT_CMD["Trigger"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def BodyHeight(self, height_cm, ack=False):
        """
        Adjust the body height of the robot to an absolute height specified in centimeters.
        The input height is mapped from a range of [20, 35] centimeters to a corresponding
        relative adjustment range in meters [-0.18, 0.03].

        Parameter: 
            height_cm (float): Absolute height value in centimeters, within the range [20, 35].
        """
        # Define the mapping from centimeters to the corresponding meter range for height adjustment
        min_cm, max_cm = 20, 35
        min_height_m, max_height_m = -0.18, 0.03

        # Check if the input height is within the acceptable range
        if not min_cm <= height_cm <= max_cm:
            raise ValueError("Height must be between 20 and 35 centimeters.")
        
        # Perform linear interpolation from cm to meter range
        height_m = min_height_m + (max_height_m - min_height_m) * ((height_cm - min_cm) / (max_cm - min_cm))

        # Prepare the parameter for the command
        para = {'data': height_m}

        # Get the action ID for BodyHeight command
        action_id = ROBOT_CMD["BodyHeight"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def FootRaiseHeight(self, height_cm, ack=False):
        """
        Adjust the foot raise height of the robot to an absolute height specified in centimeters.
        The input height is mapped from a range of [5, 12] centimeters to a corresponding
        relative adjustment range in meters [-0.06, 0.03].

        Parameter: 
            height_cm (float): Absolute height value in centimeters, within the range [5, 12].
        """
        # Define the mapping from centimeters to the corresponding meter range for height adjustment
        min_cm, max_cm = 5, 12
        min_height_m, max_height_m = -0.06, 0.03

        # Check if the input height is within the acceptable range
        if not min_cm <= height_cm <= max_cm:
            raise ValueError("Height must be between 5 and 12 centimeters.")
        
        # Perform linear interpolation from cm to meter range
        height_m = min_height_m + (max_height_m - min_height_m) * ((height_cm - min_cm) / (max_cm - min_cm))

        # Prepare the parameter for the command
        para = {'data': height_m}

        # Get the action ID for the FootRaiseHeight command
        action_id = ROBOT_CMD["FootRaiseHeight"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def SpeedLevel(self, level, ack=False):
        """
        Set the speed level of the robot dog in the walking gait mode 
        Parameter: 
            level (int): Speed range enumeration value, with values of -1 for slow speed, 0 for normal speed, and 1 for fast speed.
        """
        # Ensure 'level' is within the valid range
        if not -1 <= level <= 1:
            raise ValueError("Level must be -1 (slow speed), 0 (normal speed), or 1 (fast speed).")

        para = {'data': level}

        action_id = ROBOT_CMD["SpeedLevel"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Hello(self, ack=False):
        """
        Shakes hand in a way that signifies saying hello.
        """
        action_id = ROBOT_CMD["Hello"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Stretch(self, ack=False):
        """
        Streaches a few times.
        """
        action_id = ROBOT_CMD["Stretch"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def TrajectoryFollow(self, ack=False):
        """
        Each trajectory point contains the position and speed of the robotic dog at a certain time in the future,
        with the reference coordinate system being the absolute coordinate system of the robot. 
        Through trajectory tracking, more complex and flexible movements can be achieved.
        [Traj(),Traj(),...30times]
        """
        pass

    async def SwitchJoystick(self, flag, ack=False):
        """
        [NOT WORKING!!!!]

        After turning off the remote control response, the remote control commands will not interfere with the current program operation.

        Parameters:
        flag (bool): Set true to respond to the native remote control, and false to not respond to the remote control.
        """
        # Convert the boolean flag to an integer to comply with expected data format
        flag_int = 1 if flag else 0

        para = {'data': flag_int}

        action_id = ROBOT_CMD["SwitchJoystick"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def ContinuousGait(self, flag, ack=False):
        """
        Activates or deactivates continuous gait mode. In continuous gait mode, the robot dog
        will maintain its gait state even when the current speed is 0, allowing for smoother transitions
        between movements.

        Parameters:
        flag (bool): Set to True to activate continuous gait mode, or False to deactivate.
        """
        # Convert the boolean flag to an integer to match the expected data format
        flag_int = 1 if flag else 0

        para = {'data': flag_int}

        action_id = ROBOT_CMD["ContinuousGait"]
        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Wallow(self, ack=False):
        """
        Wallow on the floor
        """
        action_id = ROBOT_CMD["Wallow"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Content(self, ack=False):
        """
        [NOT WORKING!!!!]

        Happy
        """
        action_id = ROBOT_CMD["Content"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Pose(self, flag, ack=False):
        """
        Activates or deactivates pose mode. In pose mode, the robot maintains its position while joystick controls can change its Euler angles (roll, pitch, yaw).

        Parameters:
        flag (bool): If True, activates pose mode. If False, deactivates pose mode and restores normal operation.
        """
        # Convert the boolean flag to an integer to match the expected data format
        flag_int = 1 if flag else 0

        # Prepare the parameter for the control message
        para = {'data': flag_int}

        # Retrieve the action ID for the 'Pose' command from the SPORT_CMD dictionary
        action_id = ROBOT_CMD["Pose"]

        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Scrape(self, ack=False):
        """
        Balances on the hind legs and performs a gesture with the front limbs.
        """
        action_id = ROBOT_CMD["Scrape"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def FrontFlip(self, ack=False):
        """
        Performs a Front Flip
        """
        action_id = ROBOT_CMD["FrontFlip"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def FrontJump(self, ack=False):
        """
        Performs a Front Jump
        """
        action_id = ROBOT_CMD["FrontJump"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def FrontPounce(self, ack=False):
        """
        Performs a Front Pounce
        """
        action_id = ROBOT_CMD["FrontPounce"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Dance1(self, ack=False):
        """
        Performs a Dance1
        """
        action_id = ROBOT_CMD["Dance1"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def Dance2(self, ack=False):
        """
        Performs a Dance2
        """
        action_id = ROBOT_CMD["Dance2"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def WiggleHips(self, ack=False):
        """
        Performs a WiggleHips
        """
        action_id = ROBOT_CMD["WiggleHips"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def GetState(self):
        """
        Retrieve the current status of the robot by sending a request for specific parameters.
        Parses and returns the parameter values from the response.
        """
        parameters = ["state", "gait", "dance", "continuousGait", "economicGait"]
        # data = json.dumps(parameters)

        action_id = ROBOT_CMD["GetState"]
        
        # Ensure doRequest can handle a data dict correctly
        response = await self.doRequest(action_id, parameter=parameters, noreply=False)

        # Initialize an empty dictionary to store the parsed parameters
        parsed_parameters = {}

        # if response and response.header.status == 0:
        if response:
            try:
                # Assuming 'response' is the JSON string with the data
                response_data = json.loads(response.data)
                for param in parameters:
                    if param in response_data:
                        param_value = response_data[param]    
                        # Extract the 'data' key from the parsed JSON of each parameter
                        parsed_parameters[param] = param_value.get('data', None)
                return parsed_parameters
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response data: {e}")
                raise Exception(f"Failed to parse response data: {e}")
        else:
            logger.error("Failed to retrieve state or no response received.")


    async def EconomicGait(self, flag, ack=False):
        """
        Activates or deactivates Economic Gait, other name is Endurance mode, the bettery last for longer 

        Parameters:
        flag (bool): If True, activates pose mode. If False, deactivates pose mode and restores normal operation.
        """
        # Convert the boolean flag to an integer to match the expected data format
        flag_int = 1 if flag else 0

        # Prepare the parameter for the control message
        para = {'data': flag_int}

        # Retrieve the action ID for the 'Pose' command from the SPORT_CMD dictionary
        action_id = ROBOT_CMD["EconomicGait"]

        response = await self.doRequest(action_id, parameter=para, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
    
    async def FingerHeart(self, ack=False):
        """
        Performs a FingerHeart
        """
        action_id = ROBOT_CMD["FingerHeart"] 
        response = await self.doRequest(action_id, noreply=not ack)
        if response:
            # Use f-string for variable interpolation
            logger.info(f"Command with api_id: {action_id} succeeded")
            return True
        else:
            # Use f-string for variable interpolation
            logger.error(f"Command with api_id: {action_id} failed or no response received")
            return False
        
class SportState:
    def __init__(self, communicator, frequency='lf'):
        self.frequency = frequency
        self.communicator = communicator
        self.topic = self._get_topic_name(frequency)
        self.sport_state = None  # Placeholder for the latest sport state
        self.custom_callbacks = []  # List to hold custom callbacks

    def _get_topic_name(self, frequency):
        if frequency == 'lf':
            return self.communicator.get_topic_by_name("LF_SPORT_MOD_STATE")
        elif frequency == 'mf':
            return self.communicator.get_topic_by_name("MF_SPORT_MOD_STATE")
        else:
            return self.communicator.get_topic_by_name("SPORT_MOD_STATE")
        
    def add_custom_callback(self, callback):
        """
        Registers a custom callback to be called when new data arrives.
        """
        if callback not in self.custom_callbacks:
            self.custom_callbacks.append(callback)

    async def process_data(self, data):
        if isinstance(data, SportModeState_):
            self.sport_state = data
            logger.info("Data processed and stored in SportState instance.")
            for callback in self.custom_callbacks:
                await callback(data)
        else:
            logger.error("Received data is not of type SportModeState_")

    async def start_listening(self):
        self.communicator.subscribe(self.topic, SportModeState_, self.process_data)
        logger.info(f"Started listening to {self.topic}")

    async def stop_listening(self):
        await self.communicator.unsubscribe(self.topic)
        logger.info(f"Stopped listening to {self.topic}")

    @classmethod
    async def create_and_listen(cls, comm_protocol="DDS", frequency='lf'):
        instance = cls(comm_protocol, frequency)
        await instance.start_listening()
        return instance



async def main():
    client = SportClient()
    try:
        result = await client.GetState()
        print("Robot state parameters retrieved successfully:")
        for param, value in result.items():
            print(f"{param}: {value}")
    except Exception as e:
        print(f"Failed to retrieve robot state parameters: {e}")

        
# Usage example
if __name__ == "__main__":
    asyncio.run(main())
