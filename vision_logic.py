import cv2
import numpy as np

height, width = 400, 600
frame = np.zeros((height, width, 3), dtype="uint8")


cv2.circle(frame, (450, 200), 50, (0, 0, 255), -1)

print("--- Camera Frame Captured ---")
print(f"Image Resolution: {width}x{height}")

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

mask = cv2.inRange(hsv, lower_red, upper_red)

contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

center_x = 0

if len(contours) > 0:
    c = max(contours, key=cv2.contourArea)
    
    M = cv2.moments(c)
    if M["m00"] != 0:
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        
        print(f"TARGET FOUND at X: {center_x}, Y: {center_y}")
else:
    print("No Target Found!")

screen_center = width / 2
error = center_x - screen_center

print(f"Screen Center: {screen_center}")
print(f"Target Error: {error} pixels")

if error > 20:
    print("ACTION: TURN RIGHT >> (Target is to the right)")
elif error < -20:
    print("ACTION: << TURN LEFT (Target is to the left)")
else:
    print("ACTION: -- CENTERED -- (Fire Torpedoes!)")

cv2.imwrite("robot_view.jpg", frame)
cv2.imwrite("robot_mask.jpg", mask)
print("Debug images saved as 'robot_view.jpg' and 'robot_mask.jpg'")
