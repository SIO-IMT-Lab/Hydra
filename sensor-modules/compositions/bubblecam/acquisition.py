import cv2
import EasyPySpin
import time

cap = EasyPySpin.VideoCapture(0)

directory = "/media/grant/T7 Shield/BubbleCam_Data"
frame_rate = 10

try:
    while True:
        ret, frame = cap.read()
        current_time_stamp = time.strftime("%Y%m%d_%H%M%S")
        img_directory = f"{directory}/img_{current_time_stamp}.png"
        cv2.imwrite(img_directory, frame)

except KeyboardInterrupt:
    cap.release()