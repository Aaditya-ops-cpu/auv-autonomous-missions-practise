from pymavlink import mavutil
import time
import math
connection_string = 'udpin:127.0.0.1:14550'
master = mavutil.mavlink_connection(connection_string)
master.wait_heartbeat()
print("Connected!")

def get_heading():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        return msg.hdg / 100.0
    return 0

def set_yaw_rate(yaw_rate_rads):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000011111000111, 
        0, 0, 0,
        0, 0, 0, 
        0, 0, 0, 
        0, yaw_rate_rads) 

def turn_to_heading(target_deg):

    while True:
        current = get_heading()
        error = target_deg - current
        if error > 180:  error -= 360
        if error < -180: error += 360
        
        print(f"Current: {current:.1f}  Target: {target_deg}  Error: {error:.1f}")
        if abs(error) < 5:
            print("Target Heading Reached!")
            set_yaw_rate(0)
            break
        Kp = 0.05 
        turn_speed = error * Kp 
        
        if turn_speed > 0:
            turn_speed = max(turn_speed, 0.2)
        else:
            turn_speed = min(turn_speed, -0.2)

        turn_speed = max(min(turn_speed, 1.5), -1.5)
        
        set_yaw_rate(turn_speed)
        time.sleep(0.1)
print("Arming...")
master.arducopter_arm()
master.motors_armed_wait()
print("Armed! Switching to GUIDED.")

mode_id = master.mode_mapping()['GUIDED']
master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)

turn_to_heading(0)
time.sleep(2)

turn_to_heading(90)
time.sleep(2)

turn_to_heading(270)

print("Mission Complete. Disarming.")
master.arducopter_disarm()
