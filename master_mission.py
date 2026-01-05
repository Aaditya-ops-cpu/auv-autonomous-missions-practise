from pymavlink import mavutil
import time
import math
connection_string = 'udpin:127.0.0.1:14550'
master = mavutil.mavlink_connection(connection_string)
master.wait_heartbeat()
print("Connected!")

def get_heading():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg: return msg.hdg / 100.0
    return 0

def get_depth():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    if msg: return msg.relative_alt / 1000.0 
    return 0
def set_cmd(vx, vy, vz, yaw_rate):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000011111000111, 
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, yaw_rate)

def dive_to(target_depth):
    print(f"--- Task: Dive to {target_depth}m ---")
    while get_depth() > target_depth + 0.5:
        set_cmd(0, 0, 0.5, 0) 
        time.sleep(0.5)
    print("Depth Reached!")
    set_cmd(0, 0, 0, 0) 

def turn_to(target_deg):
    print(f"--- Task: Turn to {target_deg}° ---")
    while True:
        current = get_heading()
        error = target_deg - current
        if error > 180: error -= 360
        if error < -180: error += 360
        
        if abs(error) < 5: break
        turn_speed = max(min(error * 0.05, 1.0), -1.0)
        
        if turn_speed > 0: turn_speed = max(turn_speed, 0.2)
        else: turn_speed = min(turn_speed, -0.2)
            
        set_cmd(0, 0, 0, turn_speed)
        time.sleep(0.1)
    print("Heading Locked!")
    set_cmd(0, 0, 0, 0) 

def drive_forward(duration):
    print(f"--- Task: Forward for {duration}s ---")
    
    current = get_heading()
    vx, vy = 0, 0
    if 315 < current or current <= 45: vx = 1 
    elif 45 < current <= 135: vy = 1          
    elif 135 < current <= 225: vx = -1        
    elif 225 < current <= 315: vy = -1        
        
    for _ in range(duration):
        set_cmd(vx, vy, 0, 0)
        time.sleep(1)
    set_cmd(0, 0, 0, 0) 

print("Arming...")
master.arducopter_arm()
master.motors_armed_wait()
mode = master.mode_mapping()['GUIDED']
master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode)
print("Mission Start!")

dive_to(-5.0)
turn_to(0)   
drive_forward(5)

turn_to(90)  
drive_forward(5)

turn_to(180) 
drive_forward(5)

turn_to(270) 
drive_forward(5)

print("Surfacing...")
while get_depth() < -0.5:
    set_cmd(0, 0, -0.5, 0)
    time.sleep(0.5)

print("Mission Complete!")
master.arducopter_disarm()
