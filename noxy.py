import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

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

def calculate_and_plot(x, y, l1=20.5, l2=25.5):
    # Robot arm parameters
    try:
        # Calculate joint angles
        theta1, theta2 = inverse_kinematics(x, y, l1, l2)

        # Calculate positions for visualization
        x0, y0 = 0, 0  # Base position
        x1, y1 = l1 * np.cos(theta1), l1 * np.sin(theta1)  # First joint position
        x2, y2 = forward_kinematics(theta1, theta2, l1, l2)  # End effector position

        # Plot the robot arm
        plt.figure(figsize=(4, 4))
        plt.plot([x0, x1], [y0, y1], 'b-', linewidth=2, label='Link 1')
        plt.plot([x1, x2], [y1, y2], 'g-', linewidth=2, label='Link 2')
        plt.plot(x2, y2, 'ro', markersize=10, label='End Effector')
        plt.plot(x, y, 'mx', markersize=10, label='Target')

        plt.title('2-Link Robot Arm - Inverse Kinematics')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.grid(True)
        plt.legend()

        # Adjust plot limits
        axis_limit = max(abs(x), abs(y), l1 + l2) + 1
        plt.xlim(-axis_limit, axis_limit)
        plt.ylim(-axis_limit, axis_limit)
        plt.axis('equal')

        print(f"Target coordinates: x = {x:.2f}, y = {y:.2f}")
        print(f"Joint angles: theta1 = {np.degrees(theta1):.2f}°, theta2 = {np.degrees(theta2):.2f}°")
        print(f"End effector position: ({x2:.2f}, {y2:.2f})")

        plt.show()
    except ValueError:
        messagebox.showerror("Error", "The target point is out of reach for the robot arm.")

def on_submit():
    try:
        x = float(entry_x.get())
        y = float(entry_y.get())
        calculate_and_plot(x, y)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numerical values for x and y.")

# Create GUI
root = tk.Tk()
root.title("2-Link Robot Arm - Inverse Kinematics")

tk.Label(root, text="Enter X coordinate:").grid(row=0, column=0, padx=10, pady=10)
entry_x = tk.Entry(root)
entry_x.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Enter Y coordinate:").grid(row=1, column=0, padx=10, pady=10)
entry_y = tk.Entry(root)
entry_y.grid(row=1, column=1, padx=10, pady=10)

tk.Button(root, text="Calculate and Plot", command=on_submit).grid(row=2, column=0, columnspan=2, pady=20)

root.mainloop()
