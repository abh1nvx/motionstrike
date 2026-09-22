import pygame
import cv2
import sys

from hand_tracker import HandTracker
from game import Game


pygame.init()

WIDTH = 1280
HEIGHT = 720

CAM_WIDTH = 640
CAM_HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOTIONSTRIKE")

clock = pygame.time.Clock()

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

if not cap.isOpened():
    print("❌ Could not open webcam")
    sys.exit()

tracker = HandTracker()

game = Game(
    CAM_WIDTH,
    CAM_HEIGHT
)

running = True

print("🟢 MOTIONSTRIKE GAME STARTED!")
print("🎯 Hit the target with your index finger.")


while running:

    # -----------------------------
    # Pygame events
    # -----------------------------

    for event in pygame.event.get():

     if event.type == pygame.QUIT:
        running = False

     elif event.type == pygame.KEYDOWN:

        print("KEY PRESSED:", pygame.key.name(event.key))

        if event.key == pygame.K_r:

            if game.game_over:
                game.restart()
                print("🔄 GAME RESTARTED!")

    # -----------------------------
    # Webcam
    # -----------------------------

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)


    # -----------------------------
    # Hand tracking
    # -----------------------------

    fingertip = tracker.get_fingertip(frame)


    # -----------------------------
    # Game logic
    # -----------------------------

    hit = game.update(fingertip)

    if hit:
        print(f"💥 HIT! Score: {game.score}")


    # -----------------------------
    # Camera → Pygame
    # -----------------------------

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    frame_rgb = cv2.resize(
        frame_rgb,
        (WIDTH, HEIGHT)
    )

    camera_surface = pygame.surfarray.make_surface(
        frame_rgb.swapaxes(0, 1)
    )

    screen.blit(
        camera_surface,
        (0, 0)
    )


    # -----------------------------
    # Draw target
    # -----------------------------

    game.draw(
        screen,
        WIDTH / CAM_WIDTH,
        HEIGHT / CAM_HEIGHT
    )


    # -----------------------------
    # Draw fingertip
    # -----------------------------

    if fingertip is not None:

        x, y = fingertip

        pygame_x = int(
            x * WIDTH / CAM_WIDTH
        )

        pygame_y = int(
            y * HEIGHT / CAM_HEIGHT
        )

        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (pygame_x, pygame_y),
            18,
            3
        )

        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (pygame_x, pygame_y),
            5
        )


    pygame.display.flip()

    clock.tick(60)


cap.release()
tracker.close()

pygame.quit()
sys.exit()