from pymavlink import mavutil
import time
import sys

connection_string = 'udpin:127.0.0.1:14550'
master = mavutil.mavlink_connection(connection_string)
master.wait_heartbeat()
print("Connected!")

def get_depth():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg:
        return msg.relative_alt / 1000.0 
    return 0

def set_velocity(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0)
print("Arming...")
master.arducopter_arm()
master.motors_armed_wait()
print("Armed!")

mode_id = master.mode_mapping()['GUIDED']
master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)

target_depth = -10.0 
print(f"Diving to {target_depth} meters...")

current_depth = get_depth()
while current_depth > target_depth + 0.5:
    
    set_velocity(0, 0, 0.5) 
    
    current_depth = get_depth()
    print(f"Sensor Reading: {current_depth:.2f} m")
    
    time.sleep(0.5) 

print("Target Depth Reached! Stopping.")
print("Holding for 3 seconds...")
time.sleep(3)

print("Surfacing...")
while get_depth() < -0.5:
    
    set_velocity(0, 0, -0.5) 
    
    print(f"Depth: {get_depth():.2f} m")
    time.sleep(0.5)

print("Surface Reached! Disarming.")
set_velocity(0, 0, 0)
master.arducopter_disarm()
