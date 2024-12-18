import numpy as np
import matplotlib.pyplot as plt
import final3  # นำเข้าโมดูล final2 เพื่อดึงค่าพิกัด x, y
from final3 import coordinates_in_cm

target = coordinates_in_cm

def inverse_kinematics(x, y, l1, l2):
    # Calculate joint angles using inverse kinematics
    r = np.sqrt(x**2 + y**2)
    theta2 = np.arccos((r**2 - l1**2 - l2**2) / (2 * l1 * l2))
    theta1 = np.arctan2(y, x) - np.arctan2(l2 * np.sin(theta2), l1 + l2 * np.cos(theta2))
    return theta1, theta2

def forward_kinematics(theta1, theta2, l1, l2):
    # Calculate end effector position using forward kinematics
    x = l1 * np.cos(theta1) + l2 * np.cos(theta1 + theta2)
    y = l1 * np.sin(theta1) + l2 * np.sin(theta1 + theta2)
    return x, y

# Robot arm parameters
l1, l2 = 20.5, 25.5  # Link lengths

# ดึงค่าพิกัด x และ y จาก current_coordinates ของ final2
target_x = target["x"]
target_y = -target["y"]

# ตรวจสอบค่าพิกัดก่อน
print(f"Target coordinates: x = {target_x}, y = {target_y}")

# คำนวณมุม joint
theta1, theta2 = inverse_kinematics(target_x, target_y, l1, l2)

# คำนวณตำแหน่งสำหรับการแสดงผล
x0, y0 = 0, 0  # ตำแหน่งของฐาน
x1, y1 = l1 * np.cos(theta1), l1 * np.sin(theta1)  # ตำแหน่งของจุดเชื่อมต่อแรก
x2, y2 = forward_kinematics(theta1, theta2, l1, l2)  # ตำแหน่งของ end effector

# การแสดงผล
plt.figure(figsize=(4, 4))
plt.plot([x0, x1], [y0, y1], 'b-', linewidth=2, label='Link 1')
plt.plot([x1, x2], [y1, y2], 'g-', linewidth=2, label='Link 2')
plt.plot(x2, y2, 'ro', markersize=10, label='End Effector')
plt.plot(target_x, target_y, 'mx', markersize=10, label='Target')

plt.title('2-Link Robot Arm - Inverse Kinematics')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.legend()

# ปรับขนาดพื้นที่ให้เหมาะสมกับการแสดงผล
axis_limit = max(abs(target_x), abs(target_y), l1 + l2) + 1
plt.xlim(-axis_limit, axis_limit)
plt.ylim(-axis_limit, axis_limit)
plt.axis('equal')

print(f"Joint angles: theta1 = {np.degrees(theta1):.2f}°, theta2 = {np.degrees(theta2):.2f}°")
print(f"End effector position: ({x2:.2f}, {y2:.2f})")

plt.show()
