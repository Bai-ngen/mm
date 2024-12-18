import numpy as np
import cv2

# สมมุติว่าเรามีจุดตัวอย่างของพิกัดจริง (x_cm, y_cm) และพิกัดจากกล้อง (x_px, y_px)
# ตัวอย่างจุด 3 จุด
points_real = np.array([
    [12, 12],  # จุดที่ 1 (x_cm, y_cm)
    [24, 12],  # จุดที่ 2 (x_cm, y_cm)
    [36, 12],   # จุดที่ 3 (x_cm, y_cm)
    [48, 12], 
    [12, 24],
    [24, 24],
    [36, 24],
    [48, 24],
    [12, 36],
    [24, 36],
    [36, 36],
    [48, 36],
    [12, 48],
    [24, 48],
    [36, 48],
    [48, 48],
])

points_pixels = np.array([
    [94, 93],  # จุดที่ 1 (x_px, y_px)
    [194, 90],  # จุดที่ 2 (x_px, y_px)
    [289, 88],   # จุดที่ 3 (x_px, y_px)
    [377, 86],
    [94, 183],
    [194, 181],
    [298, 180],
    [377, 178],
    [94, 278],
    [194, 274],
    [289, 274],
    [377, 266],
    [94, 376],
    [194, 374],
    [289, 370],
    [377, 363],
])

# การคำนวณค่าสัมประสิทธิ์ด้วยการถดถอยเชิงเส้น (Linear Regression)
# คำนวณสำหรับ x (พิกัดจริง x เทียบกับพิกัดจากกล้อง x)
A_x = np.vstack([points_pixels[:, 0], np.ones(len(points_pixels))]).T
a, b = np.linalg.lstsq(A_x, points_real[:, 0], rcond=None)[0]

# คำนวณสำหรับ y (พิกัดจริง y เทียบกับพิกัดจากกล้อง y)
A_y = np.vstack([points_pixels[:, 1], np.ones(len(points_pixels))]).T
c, d = np.linalg.lstsq(A_y, points_real[:, 1], rcond=None)[0]

# สร้างตัวแปรเก็บค่าสัมประสิทธิ์
coefficients = {
    "a": a,
    "b": b,
    "c": c,
    "d": d
}

# แสดงค่าสัมประสิทธิ์ที่คำนวณได้
print(f"ค่าสัมประสิทธิ์ที่คำนวณได้:")
print(f"a = {coefficients['a']}, b = {coefficients['b']}")
print(f"c = {coefficients['c']}, d = {coefficients['d']}")

# ฟังก์ชันในการคำนวณพิกัดจริงจากพิกัดกล้อง
def convert_to_cm(x_px, y_px):
    x_cm = coefficients["a"] * x_px + coefficients["b"]
    y_cm = coefficients["c"] * y_px + coefficients["d"]
    return x_cm, y_cm

# ทดสอบการคำนวณพิกัดจริง
#x_px, y_px = 94, 376  # ตัวอย่างพิกัดจากกล้อง
#x_cm, y_cm = convert_to_cm(x_px, y_px)
#print(f"พิกัดจริงที่แปลงแล้ว: x = {x_cm:.2f} cm, y = {y_cm:.2f} cm")
