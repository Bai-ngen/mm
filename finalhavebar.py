import cv2
import numpy as np
from gpiozero import AngularServo,Servo
from time import sleep

# กำหนดพิน GPIO สำหรับเซอร์โวมอเตอร์
servo_270_1 = AngularServo(18, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)
servo_270_2 = AngularServo(19, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)
servo_270_3 = AngularServo(20, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)

# เซอร์โวสำหรับ Gripper (เซอร์โว 360 องศา - Continuous Rotation)
servo_gripper = Servo(21)  # เปลี่ยนพินตามที่ต้องการ

servo_360 = Servo(22)  # เซอร์โวแบบ 360 องศา

# ฟังก์ชัน Inverse Kinematics (คำนวณมุม theta1, theta2)
def inverse_kinematics(x, y, l1, l2):
    r = np.sqrt(x**2 + y**2)

    cos_theta2 = (r**2 - l1**2 - l2**2) / (-2 * l1 * l2)
    cos_theta2 = np.clip(cos_theta2, -1, 1)
    theta2 = np.pi - np.arccos(cos_theta2)

    cos_theta1 = (l2**2 - l1**2 - r**2) / (-2 * l1 * r)
    cos_theta1 = np.clip(cos_theta1, -1, 1)
    theta1 = np.arctan2(y, x) - np.arccos(cos_theta1)

    theta1_deg = np.degrees(theta1)
    theta2_deg = np.degrees(theta2)

    theta1_deg = np.clip(theta1_deg, 0, 270)
    theta2_deg = np.clip(theta2_deg, 0, 270)

    return np.radians(theta1_deg), np.radians(theta2_deg)

# ฟังก์ชันควบคุมเซอร์โว 270 องศา
def control_270_servos(theta1, theta2):
    print(f"Controlling 270-degree servos to angles: {np.degrees(theta1):.2f}°, {np.degrees(theta2):.2f}°")
    servo_270_1.angle = np.degrees(theta1)  # เซอร์โว 1
    servo_270_2.angle = np.degrees(theta2)  # เซอร์โว 2
    sleep(2)

# ฟังก์ชันควบคุมเซอร์โว 360 องศา
def control_360_servo():
    print("Controlling 360-degree servo...")
    servo_360.value = 1    # หมุนไปข้างหน้าสุดกำลัง
    sleep(2)
    servo_360.value = -1   # หมุนย้อนกลับสุดกำลัง
    sleep(2)
    servo_360.value = 0    # หยุดการหมุน

# ฟังก์ชันควบคุม Gripper (เปิด/ปิด โดยใช้เซอร์โว 360 องศา)
def control_gripper(action):
    if action == "open":
        print("Opening gripper...")
        servo_gripper.value = -1  # หมุนทวนเข็มนาฬิกาเพื่อเปิด
    elif action == "close":
        print("Closing gripper...")
        servo_gripper.value = 1   # หมุนตามเข็มนาฬิกาเพื่อปิด
    else:
        print("Invalid action. Please use 'open' or 'close'.")
    sleep(1)

# ฟังก์ชันจับภาพจากกล้องและคำนวณตำแหน่ง
def get_position_from_camera():
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("L - H", "Trackbars", 0, 179, lambda x: None)
    cv2.createTrackbar("L - S", "Trackbars", 0, 255, lambda x: None)
    cv2.createTrackbar("L - V", "Trackbars", 0, 255, lambda x: None)
    cv2.createTrackbar("U - H", "Trackbars", 179, 179, lambda x: None)
    cv2.createTrackbar("U - S", "Trackbars", 255, 255, lambda x: None)
    cv2.createTrackbar("U - V", "Trackbars", 255, 255, lambda x: None)

    while True:
        ret, frame = cap.read()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if ret:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # รับค่าจาก Trackbar สำหรับการเลือกสี
            l_h = cv2.getTrackbarPos("L - H", "Trackbars")
            l_s = cv2.getTrackbarPos("L - S", "Trackbars")
            l_v = cv2.getTrackbarPos("L - V", "Trackbars")
            u_h = cv2.getTrackbarPos("U - H", "Trackbars")
            u_s = cv2.getTrackbarPos("U - S", "Trackbars")
            u_v = cv2.getTrackbarPos("U - V", "Trackbars")

            lower_range = np.array([l_h, l_s, l_v])
            upper_range = np.array([u_h, u_s, u_v])

            mask = cv2.inRange(hsv, lower_range, upper_range)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 6500:
                    continue

                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    # แสดงตำแหน่งของวัตถุ
                    cv2.circle(frame, (cX, cY), 3, (0, 0, 0), -1)
                    cv2.putText(frame, f"Position: ({cX}, {cY})", (cX + 10, cY + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    # แปลงค่าพิกัดจากพิกเซลเป็นเซนติเมตร
                    scaling_factor = 1.05  # ปรับค่าตามความเหมาะสม
                    x_cm = cX / scaling_factor
                    y_cm = cY / scaling_factor

                    print(f"Target Position (cm): ({x_cm}, {y_cm})")
                    cap.release()

                    return x_cm, y_cm

    cap.release()

# เรียกใช้ฟังก์ชัน
try:
    while True:
        # คำนวณตำแหน่งจากกล้อง
        target_x_cm, target_y_cm = get_position_from_camera()

        # ความยาวของแขนหุ่นยนต์
        l1, l2 = 407.1, 354  # เซนติเมตร

        # คำนวณมุมจาก Inverse Kinematics
        theta1, theta2 = inverse_kinematics(target_x_cm, target_y_cm, l1, l2)

        # ควบคุมเซอร์โว 270 องศา
        control_270_servos(theta1, theta2)

        # ควบคุมเซอร์โว 360 องศา
        control_360_servo()

        # ควบคุม Gripper (เปิด/ปิด)
        control_gripper("close")  # ปิด Gripper เพื่อจับของ

        # หน่วงเวลา 10 วินาที ก่อนหมุนกลับ
        sleep(10)

        # หมุนเซอร์โวกลับไปที่ตำแหน่งเดิม
        servo_270_1.angle = 0
        servo_270_2.angle = 0
        servo_270_3.angle = 0
        servo_gripper.value = 0  # หยุดการหมุนของ Gripper (เปิด)
        sleep(2)

except KeyboardInterrupt:
    print("Program stopped by user.")
