import cv2
import numpy as np

# ค่าสัมประสิทธิ์ที่คำนวณได้จากการถดถอยเชิงเส้น
a = 0.12661902191544716  # สำหรับ x
b = -0.269859926661594342  # ค่าคงที่ x
c = 0.12787899035420047  # สำหรับ y
d = 0.7956355778594342   # ค่าคงที่ y

# ตัวแปรสำหรับเก็บค่าพิกัดที่แปลงแล้วในเซนติเมตร
coordinates_in_cm = {"x": None, "y": None}

# ฟังก์ชันที่ใช้ในการคลิกและรับพิกัดจากภาพ
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # คลิกซ้าย
        # ใช้ค่าสัมประสิทธิ์ที่คำนวณได้จากการถดถอยเชิงเส้น
        x_cm = a * x + b  # แปลงพิกัด x จากพิกเซลเป็นเซนติเมตร
        y_cm = c * y + d  # แปลงพิกัด y จากพิกเซลเป็นเซนติเมตร

        # เก็บค่าพิกัดที่แปลงแล้วในตัวแปร
        coordinates_in_cm["x"] = x_cm
        coordinates_in_cm["y"] = y_cm

        print(f"Clicked at pixel coordinates: (x: {x}, y: {y})")
        print(f"Corresponding cm coordinates: (x: {x_cm:.2f}, y: {y_cm:.2f})")

# ฟังก์ชันที่ใช้สำหรับการเปลี่ยนแปลงค่าของ Trackbars
def nothing(x):
    pass

# เปิดการอ่านจากกล้อง (หรือลองใช้ภาพจากไฟล์ได้)
cap = cv2.VideoCapture(1)  # ใช้กล้องดิจิทัล 1 ถ้าต้องการถ่ายจากกล้อง
# หากต้องการใช้ภาพจากไฟล์ แทน cap = cv2.VideoCapture(1) เป็น cap = cv2.imread('path_to_image')

# สร้างหน้าต่างการแสดงภาพ
cv2.namedWindow("Trackbars")

# สร้าง Trackbars สำหรับช่วงสี
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

# ตั้งค่าฟังก์ชันคลิกเมาส์
cv2.setMouseCallback("Trackbars", mouse_click)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # รับค่าจาก trackbars สำหรับช่วงสี
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])

    # สร้าง mask ตามช่วงสี
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # การกรอง noise ด้วยการ erode และ dilate
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # ค้นหาคอนทัวร์
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # วาดคอนทัวร์และคำนวณจุดศูนย์กลาง
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # กำหนดขนาดคอนทัวร์ขั้นต่ำ
            continue

        # คำนวณ bounding box
        x1, y1, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x1, y1), (x1 + w, y1 + h), (0, 255, 0), 2)

        # คำนวณจุดศูนย์กลาง
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 5, (0, 0, 255), -1)  # วาดจุดศูนย์กลาง

            # แสดงพิกัดศูนย์กลาง
            cv2.putText(frame, f"x: {cX}, y: {cY}", (cX + 10, cY + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # แปลงพิกัดจากพิกเซลเป็นเซนติเมตร
            cX_cm = a * cX + b
            cY_cm = c * cY + d

            # เก็บค่าพิกัดในเซนติเมตร
            coordinates_in_cm["x"] = cX_cm
            coordinates_in_cm["y"] = cY_cm

            print(f"Converted coordinates (cm): x: {cX_cm:.2f}, y: {cY_cm:.2f}")

    # แสดงภาพ
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    # ผลลัพธ์ที่ได้จากการทำ mask กับ frame
    res = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow("Result", res)  # แสดงผลลัพธ์ (result)

    # กด 'q' เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
