import pygame
import sys

# Initialize Pygame
pygame.init()

# Window settings
WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOTIONSTRIKE")

# Game clock
clock = pygame.time.Clock()

# Colors
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)

running = True

while running:

    # Handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Background
    screen.fill(BLACK)

    # Title
    font = pygame.font.Font(None, 64)

    title = font.render(
        "MOTIONSTRIKE",
        True,
        WHITE
    )

    screen.blit(
        title,
        (WIDTH // 2 - title.get_width() // 2, 40)
    )

    # Update display
    pygame.display.flip()

    # Limit FPS
    clock.tick(60)

pygame.quit()
sys.exit()