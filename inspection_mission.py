from pymavlink import mavutil
import time
import sys
connection_string = 'udpin:127.0.0.1:14550'
print(f"Connecting to {connection_string}...")
master = mavutil.mavlink_connection(connection_string)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Connected to system:", master.target_system, ", component:", master.target_component)

def arm_sub():
    print("Arming motors...")
    master.arducopter_arm()
    master.motors_armed_wait()
    print("Motors Armed!")

def set_mode(mode):
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    print(f"Mode set to {mode}")

def set_velocity(vx, vy, vz, yaw_rate):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111, # Bitmask asking to control velocity only
        0, 0, 0, # Position (ignored)
        vx, vy, vz, # Velocity (m/s)
        0, 0, 0, # Acceleration (ignored)
        0, yaw_rate)

set_mode('GUIDED') 
arm_sub()

print("Diving to -5m...")
# velocity z is positive for DOWN
for i in range(10): 
    set_velocity(0, 0, 0.5, 0)
    time.sleep(1)

    print("Starting Square Pattern...")

    print("Leg 1: North")
    for i in range(5):
        set_velocity(1, 0, 0, 0) # 1 m/s North (x), 0 East (y)
        time.sleep(1)
    
    print("Leg 2: East")
    for i in range(5):
        set_velocity(0, 1, 0, 0) # 0 North, 1 m/s East (y)
        time.sleep(1)
    print("Leg 3: South")
    for i in range(5):
        set_velocity(-1, 0, 0, 0) # -1 North (South), 0 East
        time.sleep(1)

    print("Leg 4: West")
    for i in range(5):
        set_velocity(0, -1, 0, 0) # 0 North, -1 East (West)
        time.sleep(1
print("Surfacing...")
set_mode('SURFACE') 

print("Mission Complete.")
