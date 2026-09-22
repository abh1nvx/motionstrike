import cv2
import mediapipe as mp
import time
import random
import math

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# -----------------------------
# MediaPipe setup
# -----------------------------

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# -----------------------------
# Game settings
# -----------------------------

TARGET_RADIUS = 35

with HandLandmarker.create_from_options(options) as landmarker:

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    width = 640
    height = 480

    # First target
    target_x = random.randint(80, width - 80)
    target_y = random.randint(80, height - 80)

    score = 0

    start_time = time.monotonic()

    print("🎯 MotionStrike target test started!")
    print("Move your index finger onto the target.")
    print("Press Q to quit.")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )

        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        cursor_x = None
        cursor_y = None

        # -----------------------------
        # Detect hand
        # -----------------------------

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            # Index fingertip
            fingertip = hand[8]

            cursor_x = int(
                fingertip.x * frame.shape[1]
            )

            cursor_y = int(
                fingertip.y * frame.shape[0]
            )

            # Draw cursor
            cv2.circle(
                frame,
                (cursor_x, cursor_y),
                12,
                (0, 255, 0),
                -1
            )

        # -----------------------------
        # Draw target
        # -----------------------------

        cv2.circle(
            frame,
            (target_x, target_y),
            TARGET_RADIUS,
            (0, 0, 255),
            -1
        )

        # -----------------------------
        # Collision detection
        # -----------------------------

        if cursor_x is not None:

            distance = math.sqrt(
                (cursor_x - target_x) ** 2 +
                (cursor_y - target_y) ** 2
            )

            if distance < TARGET_RADIUS:

                score += 1

                print(f"💥 HIT! Score: {score}")

                target_x = random.randint(
                    80,
                    width - 80
                )

                target_y = random.randint(
                    80,
                    height - 80
                )

        # -----------------------------
        # Score
        # -----------------------------

        cv2.putText(
            frame,
            f"Score: {score}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "MotionStrike - Target Test",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()