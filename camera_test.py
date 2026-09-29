import cv2

for i in range(3):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"Camera {i}: NOT AVAILABLE")
        continue

    ret, frame = cap.read()

    if ret:
        cv2.imshow(f"CAMERA INDEX {i}", frame)
        print(f"Camera {i}: WORKING — press a key on its window")
    else:
        print(f"Camera {i}: NO FRAME")

    cap.release()

print("\nPress any key to close the camera windows.")
cv2.waitKey(0)
cv2.destroyAllWindows()