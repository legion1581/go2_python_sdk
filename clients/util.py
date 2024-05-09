# Add clients and communicator directory to sys path
import sys, os
import logging
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import struct

#####
# CRC Caluclation for low level
#####
class LowLevelCRC():

    def _reverse_byte_order(self, data):
        # Check that the length of the data is a multiple of 4
        if len(data) % 4 != 0:
            raise ValueError("The length of the data must be a multiple of 4 bytes")

        # Split the data into 4-byte chunks and reverse each chunk
        reversed_chunks = [data[i:i+4][::-1] for i in range(0, len(data), 4)]
        
        # Join all reversed chunks back into a single byte string
        reversed_data = b''.join(reversed_chunks)
        return reversed_data

    def _crc32mpeg2(self, buf, crc=0xffffffff):

        for val in buf:
            crc ^= val << 24
            for _ in range(8):
                crc = crc << 1 if (crc & 0x80000000) == 0 else (crc << 1) ^ 0x104c11db7
        return crc

    def calc_crc_low_cmd(self, cmd) -> bytes:

        packed_data = b''
        packed_data += self._reverse_byte_order(struct.pack('<4B',
                *cmd.head,
                cmd.level_flag, 
                cmd.frame_reserve))
        packed_data += struct.pack('>4I', 
                *cmd.sn, 
                *cmd.version)
        packed_data += self._reverse_byte_order(struct.pack('<H 2x',  
                cmd.bandwidth))
        # Pack Motor data
        for motor in cmd.motor_cmd:
            packed_data += self._reverse_byte_order(struct.pack('<B 3x',
                motor.mode))
            packed_data += struct.pack('>5f 3I',
                motor.q,
                motor.dq,
                motor.tau,
                motor.kp,
                motor.kd,
                *motor.reserve)
        packed_data += self._reverse_byte_order(struct.pack('<4B',
                cmd.bms_cmd.off,
                *cmd.bms_cmd.reserve))
        packed_data += self._reverse_byte_order(struct.pack('<55B x',
                *cmd.wireless_remote,
                *cmd.led,
                *cmd.fan,
                cmd.gpio))
        packed_data += struct.pack('>I',
                cmd.reserve)
        return self._crc32mpeg2(packed_data)

    def calc_crc_low_state(self, state) -> bytes:

        packed_data = b''
        packed_data += self._reverse_byte_order(struct.pack('<4B', 
                *state.head, 
                state.level_flag, 
                state.frame_reserve))
        
        packed_data += struct.pack('>4I',
                *state.sn, 
                *state.version)
        
        packed_data += self._reverse_byte_order(struct.pack('<H 2x',
                state.bandwidth))

        # Serialization of a single IMUState_ object
        packed_data += struct.pack('>13f', 
                *state.imu_state.quaternion,
                *state.imu_state.gyroscope, 
                *state.imu_state.accelerometer, 
                *state.imu_state.rpy)
        packed_data += self._reverse_byte_order(struct.pack('<B 3x',
                state.imu_state.temperature))

        # Serializing motor states
        for motor in state.motor_state:
            packed_data += self._reverse_byte_order(struct.pack('<B 3x',
                    motor.mode))
            packed_data += struct.pack('>7f',
                    motor.q, 
                    motor.dq, 
                    motor.ddq, 
                    motor.tau_est, 
                    motor.q_raw, 
                    motor.dq_raw, 
                    motor.ddq_raw)
            packed_data += self._reverse_byte_order(struct.pack('<B 3x',
                    motor.temperature))
            packed_data += struct.pack('>3I',
                    motor.lost, 
                    *motor.reserve)

        # Serializing BMS state
        packed_data += self._reverse_byte_order(struct.pack('<4B',
                state.bms_state.version_high,
                state.bms_state.version_low,
                state.bms_state.status,
                state.bms_state.soc))
        packed_data += struct.pack('>i',
                                    state.bms_state.current)
        packed_data += self._reverse_byte_order(struct.pack('<H 4B 15H',
                state.bms_state.cycle,
                *state.bms_state.bq_ntc,
                *state.bms_state.mcu_ntc,
                *state.bms_state.cell_vol))

        packed_data += self._reverse_byte_order(struct.pack('<8h', 
                *state.foot_force, 
                *state.foot_force_est))
        packed_data += struct.pack('>I',
                state.tick)
        packed_data += self._reverse_byte_order(struct.pack('<40B B 3x',
                *state.wireless_remote, 
                state.bit_flag))
        packed_data += struct.pack('>f',
                state.adc_reel)
        packed_data += self._reverse_byte_order(struct.pack('<2B 2x',
                state.temperature_ntc1, 
                state.temperature_ntc2))
        packed_data += struct.pack('>2f', 
                state.power_v, 
                state.power_a)
        packed_data += self._reverse_byte_order(struct.pack('<4H',
                *state.fan_frequency))
        packed_data += struct.pack('>I',
                state.reserve)

        return self._crc32mpeg2(packed_data)

#####
#
#####

#####
#Logger functions
#####

class DedupLoggingMessages(logging.Filter):
    """Logger filter to prevent duplicated messages from being logged.


    Args:
        always_print_logger_levels (set[logging.Level]): A set of logging levels which
                                                    any logged message at that level will
                                                    always be logged.
    """


    def __init__(self, always_print_logger_levels={logging.CRITICAL, logging.ERROR}):
        # Warning level mapped to last message logged.
        self.last_error_message = None
        self.always_print_logger_levels = always_print_logger_levels


    def filter(self, record):
        warning_level = record.levelno
        # Always allow messages above a certain warning level to be logged.
        if warning_level in self.always_print_logger_levels:
            return True


        error_message = record.getMessage()
        # Deduplicate logged messages by preventing a message that was just logged to be sent again.
        if self.last_error_message != error_message and error_message is not None:
            self.last_error_message = error_message
            return True


        return False

def get_logger():
    return logging.getLogger()


def does_dedup_filter_exist(logger, always_print_logger_levels):
    """Check if the DedupLoggingMessages filter exists for a logger.


    Returns:
        Boolean indicating if the DedupLoggingMessages filter already exists and matches the new parameters.
    """
    for filt in logger.filters:
        if type(
                filt
        ) == DedupLoggingMessages and filt.always_print_logger_levels == always_print_logger_levels:
            return True
    return False



def setup_logging(verbose=False, include_dedup_filter=False,
                  always_print_logger_levels={logging.CRITICAL, logging.ERROR}):
    """Set up a basic streaming console handler at the root logger.


    Args:
        verbose (boolean): if False (default) show messages at INFO level and above,
                           if True show messages at DEBUG level and above.
        include_dedup_filter (boolean): If true, the logger includes a filter which
                                        will prevent repeated duplicated messages
                                        from being logged.
        always_print_logger_levels (set[logging.Level]): A set of logging levels which
                                                        any logged message at that level will
                                                        always be logged.
    """
    logger = get_logger()


    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO


    if not logger.handlers:
        streamlog = logging.StreamHandler()
        streamlog.setLevel(level)
        streamlog.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s'))
        if include_dedup_filter:
            # Propagate the filter through the handler. logging.Filter does not propagate to other
            # child loggers on its own, and must be attached to the handler.
            streamlog.addFilter(DedupLoggingMessages(always_print_logger_levels))
        logger.addHandler(streamlog)


    if logger.handlers and include_dedup_filter:
        # If a logger has existing handlers, check if the filter is there already. Also check if it is part of the
        # main log already. If not, add it to a new handler.
        filter_exists = None
        for handler in logger.handlers:
            filter_exists = filter_exists or does_dedup_filter_exist(handler,
                                                                     always_print_logger_levels)
        if not filter_exists:
            dedupFilterLog = logging.StreamHandler()
            # Propagate the filter through the handler. logging.Filter does not propagate to other
            # child loggers on its own, and must be attached to the handler.
            dedupFilterLog.addFilter(DedupLoggingMessages(always_print_logger_levels))
            logger.addHandler(dedupFilterLog)


    # Add the level and filter onto just the regular logger as well.
    logger.setLevel(level)
    if include_dedup_filter:
        if not does_dedup_filter_exist(logger, always_print_logger_levels):
            logger.addFilter(DedupLoggingMessages(always_print_logger_levels))

#####
#
#####

class PeriodicTask:
    def __init__(self, logger=None):
        self.task = None
        self.logger = logger or logging.getLogger(__name__)

    async def start(self, interval, callback, *args, **kwargs):
        if self.task is None or self.task.done():
            self.logger.info("Starting task loop.")
            return asyncio.create_task(self.run_loop(interval, callback, *args, **kwargs))


    async def stop(self):
        if self.task and not self.task.done():
            self.task.cancel()
            self.logger.info("Task loop stopped.")
            try:
                await self.task
            except asyncio.CancelledError:
                self.logger.info("Task was cancelled.")

    async def run_loop(self, interval_ms, callback, *args, **kwargs):
        try:
            while True:
                await callback(*args, **kwargs)
                await asyncio.sleep(interval_ms / 1000)
        except asyncio.CancelledError:
            self.logger.info("Task loop was cancelled.")
        except Exception as e:
            self.logger.error(f"Error in task loop: {e}")


