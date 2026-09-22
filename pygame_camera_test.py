import pygame
import cv2
import sys

pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOTIONSTRIKE")

clock = pygame.time.Clock()

# Open webcam
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("❌ Could not open webcam")
    sys.exit()

running = True

while running:

    # -----------------------------
    # Pygame events
    # -----------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # -----------------------------
    # Get webcam frame
    # -----------------------------

    ret, frame = cap.read()

    if not ret:
        print("❌ Could not read webcam")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # OpenCV BGR → RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert OpenCV image → Pygame surface
    frame = cv2.resize(frame, (WIDTH, HEIGHT))

    camera_surface = pygame.surfarray.make_surface(
        frame.swapaxes(0, 1)
    )

    # -----------------------------
    # Draw camera
    # -----------------------------

    screen.blit(camera_surface, (0, 0))

    # -----------------------------
    # Update
    # -----------------------------

    pygame.display.flip()

    clock.tick(60)


cap.release()
pygame.quit()
sys.exit()