from pymavlink import mavutil
import time
import sys

# 1. Connect to the Simulation
# SITL opens port 14550 for GCS and usually 14551 or others for scripts. 
# MAVProxy forwards data to udpin:127.0.0.1:14550 by default. 
# We will connect as a UDP client listening for the heartbeat.
connection_string = 'udpin:127.0.0.1:14550'
print(f"Connecting to {connection_string}...")
master = mavutil.mavlink_connection(connection_string)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Connected to system:", master.target_system, ", component:", master.target_component)

# 2. Function to Arm the Thrusters
def arm_sub():
    print("Arming motors...")
    master.arducopter_arm()
    master.motors_armed_wait()
    print("Motors Armed!")

# 3. Function to Change Flight Mode
def set_mode(mode):
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)
    print(f"Mode set to {mode}")

# 4. Function to Move (Velocity Control)
def set_velocity(vx, vy, vz, yaw_rate):
    master.mav.set_position_target_local_ned_send(
        0, master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111, # Bitmask asking to control velocity only
        0, 0, 0, # Position (ignored)
        vx, vy, vz, # Velocity (m/s)
        0, 0, 0, # Acceleration (ignored)
        0, yaw_rate)

# --- THE MISSION ---

# Step A: Initialize
set_mode('GUIDED') 
arm_sub()

# Step B: Dive to 5 meters
print("Diving to -5m...")
# velocity z is positive for DOWN
for i in range(10): 
    set_velocity(0, 0, 0.5, 0)
    time.sleep(1)

# Step C: Move Forward
# Step C: Swim in a Square
    print("Starting Square Pattern...")

    # Leg 1: North
    print("Leg 1: North")
    for i in range(5):
        set_velocity(1, 0, 0, 0) # 1 m/s North (x), 0 East (y)
        time.sleep(1)
    
    # Leg 2: East
    print("Leg 2: East")
    for i in range(5):
        set_velocity(0, 1, 0, 0) # 0 North, 1 m/s East (y)
        time.sleep(1)

    # Leg 3: South
    print("Leg 3: South")
    for i in range(5):
        set_velocity(-1, 0, 0, 0) # -1 North (South), 0 East
        time.sleep(1)

    # Leg 4: West
    print("Leg 4: West")
    for i in range(5):
        set_velocity(0, -1, 0, 0) # 0 North, -1 East (West)
        time.sleep(1)
# Step D: Surface
print("Surfacing...")
set_mode('SURFACE') 

print("Mission Complete.")
