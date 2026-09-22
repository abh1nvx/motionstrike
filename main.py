import cv2

from hand_tracker import HandTracker
from game import Game


def main():

    # -----------------------------
    # Camera
    # -----------------------------

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # -----------------------------
    # Systems
    # -----------------------------

    tracker = HandTracker()
    game = Game(640, 480)

    print("🟢 MOTIONSTRIKE STARTED!")
    print("🎯 Hit the red targets with your index finger.")
    print("❌ Press Q to quit.")

    while True:

        ret, frame = cap.read()

        if not ret:
            print("❌ Could not read webcam frame.")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        # -----------------------------
        # Hand tracking
        # -----------------------------

        fingertip = tracker.get_fingertip(frame)

        # -----------------------------
        # Game update
        # -----------------------------

        hit = game.update(fingertip)

        if hit:
            print(f"💥 HIT! Score: {game.score}")

        # -----------------------------
        # Draw cursor
        # -----------------------------

        if fingertip is not None:

            x, y = fingertip

            cv2.circle(
                frame,
                (x, y),
                12,
                (0, 255, 0),
                -1
            )

        # -----------------------------
        # Draw game
        # -----------------------------

        game.draw(frame)

        # -----------------------------
        # Display
        # -----------------------------

        cv2.imshow(
            "MOTIONSTRIKE",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # -----------------------------
    # Cleanup
    # -----------------------------

    cap.release()
    tracker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()