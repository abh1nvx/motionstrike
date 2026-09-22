import random
import math
import pygame


class Game:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # Target settings
        self.target_radius = 35

        # Timer settings
        self.target_time = 3.0
        self.target_start_time = pygame.time.get_ticks()

        # Game stats
        self.score = 0
        self.lives = 3
        self.game_over = False

        # Target position
        self.target_x = 0
        self.target_y = 0

        # Spawn first target
        self.spawn_target()

    def spawn_target(self):
        self.target_x = random.randint(
            70,
            self.width - 70
        )

        self.target_y = random.randint(
            70,
            self.height - 70
        )

        # Reset timer whenever a new target appears
        self.target_start_time = pygame.time.get_ticks()

    def update(self, cursor_position):

        # Don't update after Game Over
        if self.game_over:
            return False

        # Calculate remaining time
        elapsed = (
            pygame.time.get_ticks()
            - self.target_start_time
        ) / 1000

        time_left = self.target_time - elapsed

        # Timer expired
        if time_left <= 0:

            self.lose_life()

            # Spawn a new target if the game isn't over
            if not self.game_over:
                self.spawn_target()

            return False

        # No hand detected
        if cursor_position is None:
            return False

        cursor_x, cursor_y = cursor_position

        # Calculate distance between fingertip and target
        distance = math.sqrt(
            (cursor_x - self.target_x) ** 2
            + (cursor_y - self.target_y) ** 2
        )

        # Target hit
        if distance < self.target_radius:

            self.score += 1

            self.spawn_target()

            return True

        return False

    def lose_life(self):

        if self.game_over:
            return

        self.lives -= 1

        if self.lives <= 0:
            self.lives = 0
            self.game_over = True

    def restart(self):

        self.score = 0
        self.lives = 3
        self.game_over = False

        self.spawn_target()

    def draw(self, screen, scale_x=1, scale_y=1):

        # --------------------------------
        # TARGET
        # --------------------------------

        if not self.game_over:

            target_x = int(
                self.target_x * scale_x
            )

            target_y = int(
                self.target_y * scale_y
            )

            radius = int(
                self.target_radius * scale_x
            )

            # Red target
            pygame.draw.circle(
                screen,
                (220, 40, 60),
                (target_x, target_y),
                radius
            )

            # White target outline
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (target_x, target_y),
                radius,
                3
            )

        # --------------------------------
        # FONTS
        # --------------------------------

        font = pygame.font.Font(None, 48)

        # --------------------------------
        # SCORE
        # --------------------------------

        score_text = font.render(
            f"SCORE: {self.score}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            score_text,
            (20, 20)
        )

        # --------------------------------
        # LIVES
        # --------------------------------

        lives_text = font.render(
            f"LIVES: {self.lives}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            lives_text,
            (20, 65)
        )

        # --------------------------------
        # TIMER
        # --------------------------------

        if not self.game_over:

            elapsed = (
                pygame.time.get_ticks()
                - self.target_start_time
            ) / 1000

            time_left = max(
                0,
                self.target_time - elapsed
            )

        else:
            time_left = 0

        timer_text = font.render(
            f"TIME: {time_left:.1f}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            timer_text,
            (20, 110)
        )

        # --------------------------------
        # GAME OVER SCREEN
        # --------------------------------

        if self.game_over:

            big_font = pygame.font.Font(
                None,
                90
            )

            game_over_text = big_font.render(
                "GAME OVER",
                True,
                (255, 60, 60)
            )

            text_rect = game_over_text.get_rect(
                center=(
                    self.width * scale_x / 2,
                    self.height * scale_y / 2
                )
            )

            screen.blit(
                game_over_text,
                text_rect
            )

            small_font = pygame.font.Font(
                None,
                42
            )

            restart_text = small_font.render(
                "Press R to Restart",
                True,
                (255, 255, 255)
            )

            restart_rect = restart_text.get_rect(
                center=(
                    self.width * scale_x / 2,
                    self.height * scale_y / 2 + 70
                )
            )

            screen.blit(
                restart_text,
                restart_rect
            )