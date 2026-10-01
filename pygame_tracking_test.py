import cv2
import pygame
import sys
import numpy as np
import ctypes

from hand_tracker import HandTracker
from game import Game


# ============================================================
# DISPLAY
# ============================================================

WIDTH = 1280
HEIGHT = 720

WINDOWED_SIZE = (WIDTH, HEIGHT)


# ============================================================
# CAMERA
# ============================================================

CAMERA_INDEX = 1

CAM_WIDTH = 640
CAM_HEIGHT = 480


# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame.init()

FULLSCREEN = False

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption("MOTIONSTRIKE")

clock = pygame.time.Clock()


# ============================================================
# CAMERA INITIALIZATION
# ============================================================

print(
    f"📷 Connecting to Logitech BRIO "
    f"on Camera Index {CAMERA_INDEX}..."
)

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)

# If DirectShow fails
if not cap.isOpened():

    print(
        "⚠ DirectShow failed. "
        "Trying default camera backend..."
    )

    cap.release()

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )


# Read first frame BEFORE forcing resolution
ret, frame = cap.read()

if not ret:

    print(
        "❌ Failed to read frame from Logitech BRIO."
    )

    cap.release()
    pygame.quit()
    sys.exit()


print(
    "✅ Logitech BRIO connected successfully!"
)


# ============================================================
# HAND TRACKER
# ============================================================

tracker = HandTracker(
    "hand_landmarker.task"
)


# ============================================================
# GAME
# ============================================================

game = Game(
    CAM_WIDTH,
    CAM_HEIGHT
)


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # --------------------------------------------------------
    # DELTA TIME
    # --------------------------------------------------------

    dt = clock.tick(60) / 1000.0

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        # Close window
        if event.type == pygame.QUIT:

            running = False
            continue

        # F10: Toggle maximize / restore
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_F10
        ):

            hwnd = pygame.display.get_wm_info()["window"]

            if ctypes.windll.user32.IsZoomed(hwnd):

                ctypes.windll.user32.ShowWindow(
                    hwnd,
                    9  # Restore
                )

            else:

                ctypes.windll.user32.ShowWindow(
                    hwnd,
                    3  # Maximize
                )

            continue

        # F11: Toggle fullscreen/windowed mode
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_F11
        ):

            FULLSCREEN = not FULLSCREEN

            if FULLSCREEN:

                screen = pygame.display.set_mode(
                    (0, 0),
                    pygame.FULLSCREEN
                )

            else:

                screen = pygame.display.set_mode(
                    WINDOWED_SIZE,
                    pygame.RESIZABLE
                )

            WIDTH, HEIGHT = screen.get_size()

            continue

        # Handle window resizing
        if event.type == pygame.VIDEORESIZE and not FULLSCREEN:

            WIDTH = max(1, event.w)
            HEIGHT = max(1, event.h)

            WINDOWED_SIZE = (WIDTH, HEIGHT)

            screen = pygame.display.set_mode(
                WINDOWED_SIZE,
                pygame.RESIZABLE
            )

            continue

        # Pass all other events to the game
        # This includes mouse clicks and keyboard input
        game.handle_event(event)

    if not running:
        break

    # --------------------------------------------------------
    # GAME QUIT STATE
    # --------------------------------------------------------

    if game.state == "QUIT":

        running = False
        continue

    # --------------------------------------------------------
    # CAMERA FRAME
    # --------------------------------------------------------

    # Read a fresh frame EVERY main-loop iteration
    ret, frame = cap.read()

    if not ret:
        continue

    # Mirror the camera feed to match the user-facing view
    frame = cv2.flip(frame, 1)

    # Resize to stable working resolution for tracking
    frame = cv2.resize(
        frame,
        (
            CAM_WIDTH,
            CAM_HEIGHT
        ),
        interpolation=cv2.INTER_LINEAR
    )

    # --------------------------------------------------------
    # HAND TRACKING
    # --------------------------------------------------------

    fingertip = None

    if game.state == "PLAYING":

        fingertip = tracker.get_fingertip(
            frame
        )

        game.update(
            fingertip,
            dt
        )

    # --------------------------------------------------------
    # DRAW CAMERA / BACKGROUND
    # --------------------------------------------------------

    if game.state == "PLAYING":

        # Convert BGR -> RGB
        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Convert camera frame to Pygame surface
        camera_surface = pygame.image.frombuffer(
            frame_rgb.tobytes(),
            (
                CAM_WIDTH,
                CAM_HEIGHT
            ),
            "RGB"
        ).copy()

        # Resize camera display to the current window size
        camera_surface = pygame.transform.smoothscale(
            camera_surface,
            screen.get_size()
        )

        # Draw camera across the entire window
        screen.blit(
            camera_surface,
            (0, 0)
        )

    else:

        screen.fill(
            game.BG
        )

    # --------------------------------------------------------
    # GAME UI
    # --------------------------------------------------------

    game.draw(
        screen,
        WIDTH / CAM_WIDTH,
        HEIGHT / CAM_HEIGHT
    )

    # --------------------------------------------------------
    # HAND CURSOR
    # --------------------------------------------------------

    if (
        game.state == "PLAYING"
        and fingertip is not None
    ):

        fx, fy = fingertip

        screen_x = int(
            fx *
            WIDTH /
            CAM_WIDTH
        )

        screen_y = int(
            fy *
            HEIGHT /
            CAM_HEIGHT
        )

        # Outer ring
        pygame.draw.circle(
            screen,
            (0, 255, 170),
            (
                screen_x,
                screen_y
            ),
            15,
            2
        )

        # Inner dot
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (
                screen_x,
                screen_y
            ),
            5
        )

        # Small targeting lines
        pygame.draw.line(
            screen,
            (0, 255, 170),
            (
                screen_x - 24,
                screen_y
            ),
            (
                screen_x - 10,
                screen_y
            ),
            2
        )

        pygame.draw.line(
            screen,
            (0, 255, 170),
            (
                screen_x + 10,
                screen_y
            ),
            (
                screen_x + 24,
                screen_y
            ),
            2
        )

        pygame.draw.line(
            screen,
            (0, 255, 170),
            (
                screen_x,
                screen_y - 24
            ),
            (
                screen_x,
                screen_y - 10
            ),
            2
        )

        pygame.draw.line(
            screen,
            (0, 255, 170),
            (
                screen_x,
                screen_y + 10
            ),
            (
                screen_x,
                screen_y + 24
            ),
            2
        )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()


# ============================================================
# CLEANUP
# ============================================================

print(
    "🛑 Closing MotionStrike..."
)

game.play_quit_sound()

tracker.close()
cap.release()
pygame.quit()
sys.exit()