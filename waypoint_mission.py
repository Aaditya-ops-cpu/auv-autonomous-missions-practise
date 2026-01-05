from pymavlink import mavutil
import time
import math

connection_string = 'udpin:127.0.0.1:14550'
print(f"Connecting to {connection_string}...")
master = mavutil.mavlink_connection(connection_string)
master.wait_heartbeat()
print("Connected!")

def get_location():
    print("Waiting for GPS lock...")
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    lat = msg.lat / 1e7
    lon = msg.lon / 1e7
    alt = msg.relative_alt / 1000.0
    print(f"Current Location: {lat}, {lon}")
    return lat, lon, alt

def upload_mission(waypoints):
    master.mav.mission_clear_all_send(master.target_system, master.target_component)
    master.recv_match(type='MISSION_ACK', blocking=True)
    print("Old Mission Cleared.")

    count = len(waypoints)
    master.mav.mission_count_send(master.target_system, master.target_component, count)

    for i in range(count):
        msg = master.recv_match(type=['MISSION_REQUEST'], blocking=True)
        print(f"Uploading Waypoint {msg.seq}...")
        
        wp = waypoints[msg.seq]
        master.mav.mission_item_int_send(
            master.target_system, master.target_component,
            msg.seq,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 1, 
            0, 0, 0, 0, 
            int(wp[0] * 1e7), 
            int(wp[1] * 1e7), 
            int(wp[2])        
        )
    
    ack = master.recv_match(type='MISSION_ACK', blocking=True)
    print(f"Upload Complete! Result: {ack.type}")

start_lat, start_lon, _ = get_location()
offset = 0.00015 
target_depth = -5.0 

mission_list = [
    [start_lat + offset, start_lon, target_depth],
    
    [start_lat + offset, start_lon + offset, target_depth],
    
    [start_lat, start_lon + offset, target_depth],
    
    [start_lat, start_lon, target_depth]
]

upload_mission(mission_list)
print("Arming...")
master.arducopter_arm()
master.motors_armed_wait()

print("Switching to AUTO Mode...")
mode_id = master.mode_mapping()['AUTO']
master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)

print("Mission Started! Monitoring progress...")

while True:
    msg = master.recv_match(type='MISSION_CURRENT', blocking=True)
    current_wp = msg.seq
    nav_msg = master.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True)
    dist_to_wp = nav_msg.wp_dist
    pos_msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    current_depth = pos_msg.relative_alt / 1000.0
    hb = master.recv_match(type='HEARTBEAT', blocking=True)
    is_armed = (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) > 0
    status = "ARMED" if is_armed else "DISARMED"
    print(f"WP: {current_wp} | Dist: {dist_to_wp}m | Depth: {current_depth:.2f}m | {status}")
    
    time.sleep(1)
