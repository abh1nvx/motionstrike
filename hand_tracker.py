import cv2
import mediapipe as mp
import time


class HandTracker:

    def __init__(self, model_path="hand_landmarker.task"):

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=RunningMode.VIDEO,
            num_hands=1
        )

        self.landmarker = HandLandmarker.create_from_options(options)
        self.start_time = time.monotonic()

    def get_fingertip(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp_ms = int(
            (time.monotonic() - self.start_time) * 1000
        )

        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        if result.hand_landmarks:

            fingertip = result.hand_landmarks[0][8]

            x = int(fingertip.x * frame.shape[1])
            y = int(fingertip.y * frame.shape[0])

            return x, y

        return None

    def close(self):
        self.landmarker.close()