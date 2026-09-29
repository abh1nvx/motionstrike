import pygame
import random
import json
import os


class Game:
    # ============================================================
    # COLORS
    # ============================================================

    BG = (7, 10, 20)
    PANEL = (12, 17, 31)
    PANEL_2 = (17, 23, 40)

    WHITE = (245, 248, 255)
    MUTED = (145, 155, 180)

    CYAN = (0, 220, 255)
    BLUE = (70, 130, 255)
    PURPLE = (160, 90, 255)

    GREEN = (70, 255, 150)
    RED = (255, 65, 80)
    ORANGE = (255, 150, 40)
    YELLOW = (255, 220, 70)

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self, cam_width=640, cam_height=480):

        self.cam_width = cam_width
        self.cam_height = cam_height

        # Fonts
        self.big_font = pygame.font.SysFont(
            "Arial", 72, bold=True
        )

        self.title_font = pygame.font.SysFont(
            "Arial", 64, bold=True
        )

        self.medium_font = pygame.font.SysFont(
            "Arial", 30, bold=True
        )

        self.small_font = pygame.font.SysFont(
            "Arial", 20
        )

        self.tiny_font = pygame.font.SysFont(
            "Arial", 16
        )

        # Game state
        self.state = "START"

        self.player_name = ""
        self.score = 0

        # ONLY ONE LIFE
        self.lives = 1

        self.level = 1

        # Target
        self.target = None
        self.target_type = None

        self.target_x = 0
        self.target_y = 0
        self.target_radius = 25

        # Timers
        self.spawn_timer = 0.0
        self.spawn_interval = 0.62

        self.target_timer = 0.0
        self.virus_duration = 2.35

        # Difficulty
        self.base_speeds = {
            "normal": 220,
            "virus": 205,
            "powerup": 245,
            "danger": 235,
        }

        self.level_thresholds = [
            0,
            25,
            60,
            110,
            180,
            270,
            390,
            540,
        ]

        # Leaderboard
        self.leaderboard_file = "motionstrike_leaderboard.json"

        self.leaderboard = self.load_leaderboard()

        # Sound
        # Disabled for now because custom sounds will be supplied later.
        self.sounds_enabled = False
        self.sounds = {}

        # Cached UI text
        self.score_label = self.medium_font.render(
            "SCORE", True, self.MUTED
        )

        self.level_label = self.medium_font.render(
            "LEVEL", True, self.MUTED
        )

        self.life_label = self.medium_font.render(
            "LIFE", True, self.MUTED
        )

    # ============================================================
    # LEADERBOARD
    # ============================================================

    def load_leaderboard(self):

        if not os.path.exists(self.leaderboard_file):
            return []

        try:
            with open(
                self.leaderboard_file,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            if isinstance(data, list):
                return data

        except Exception:
            pass

        return []

    def save_leaderboard(self):

        try:
            with open(
                self.leaderboard_file,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    self.leaderboard,
                    f,
                    indent=4
                )

        except Exception:
            pass

    def add_score_to_leaderboard(self):

        name = self.player_name.strip()

        if not name:
            name = "PLAYER"

        self.leaderboard.append({
            "name": name,
            "score": int(self.score)
        })

        self.leaderboard.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        self.leaderboard = self.leaderboard[:10]

        self.save_leaderboard()

    # ============================================================
    # SOUND HOOK
    # ============================================================

    def play_sound(self, name):

        if not self.sounds_enabled:
            return

        sound = self.sounds.get(name)

        if sound:
            try:
                sound.play()
            except Exception:
                pass

    # ============================================================
    # START GAME
    # ============================================================

    def start(self):

        self.state = "PLAYING"

        self.score = 0
        self.lives = 1
        self.level = 1

        self.target = None
        self.target_type = None

        self.spawn_timer = 0.0
        self.target_timer = 0.0

        # First ball appears quickly
        self.spawn_target()

    # ============================================================
    # SPAWN TARGET
    # ============================================================

    def spawn_target(self):

        # Target types
        roll = random.random()

        if roll < 0.55:
            target_type = "normal"

        elif roll < 0.75:
            target_type = "virus"

        elif roll < 0.90:
            target_type = "powerup"

        else:
            target_type = "danger"

        self.target_type = target_type

        # Random X position
        margin = self.target_radius + 10

        self.target_x = random.randint(
            margin,
            self.cam_width - margin
        )

        # Start above the visible area
        self.target_y = -self.target_radius

        self.target_timer = 0.0

        self.target = True

    # ============================================================
    # TARGET SPEED
    # ============================================================

    def get_target_speed(self):

        speed = self.base_speeds.get(
            self.target_type,
            220
        )

        # Increase speed every level
        multiplier = 1.0 + (
            0.17 * (self.level - 1)
        )

        return speed * multiplier

    # ============================================================
    # LEVEL
    # ============================================================

    def update_level(self):

        new_level = 1

        for i, threshold in enumerate(
            self.level_thresholds,
            start=1
        ):

            if self.score >= threshold:
                new_level = i

        if new_level != self.level:

            self.level = new_level

            self.play_sound("level")

    # ============================================================
    # TARGET CAUGHT
    # ============================================================

    def catch_target(self):

        if self.target_type == "normal":

            self.score += 2
            self.play_sound("catch")

        elif self.target_type == "virus":

            self.score += 10
            self.play_sound("virus")

        elif self.target_type == "powerup":

            self.score += 5
            self.play_sound("powerup")

        elif self.target_type == "danger":

            # ORANGE BALL
            self.score -= 30

            # Don't allow ridiculous negative scores
            # You can remove this if you want negative
            # leaderboard scores.
            if self.score < 0:
                self.score = 0

            self.play_sound("danger")

        self.update_level()

        self.target = None
        self.target_type = None
        self.spawn_timer = 0.0

    # ============================================================
    # MISSED TARGET
    # ============================================================

    def miss_target(self):

        # IMPORTANT:
        # ANY missed ball = GAME OVER
        self.game_over()

    # ============================================================
    # GAME OVER
    # ============================================================

    def game_over(self):

        if self.state == "GAME_OVER":
            return

        self.state = "GAME_OVER"

        self.target = None
        self.target_type = None

        self.add_score_to_leaderboard()

        self.play_sound("gameover")

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, fingertip, dt):

        if self.state != "PLAYING":
            return

        # Prevent huge frame jumps
        dt = min(dt, 0.05)

        # --------------------------------------------------------
        # SPAWN
        # --------------------------------------------------------

        if self.target is None:

            self.spawn_timer += dt

            if self.spawn_timer >= self.spawn_interval:

                self.spawn_timer = 0.0
                self.spawn_target()

        # --------------------------------------------------------
        # MOVE TARGET
        # --------------------------------------------------------

        if self.target:

            speed = self.get_target_speed()

            self.target_y += speed * dt

            self.target_timer += dt

            # ----------------------------------------------------
            # COLLISION
            # ----------------------------------------------------

            if fingertip is not None:

                fx, fy = fingertip

                dx = fx - self.target_x
                dy = fy - self.target_y

                distance_squared = (
                    dx * dx +
                    dy * dy
                )

                collision_distance = 20

                if distance_squared <= (
                    collision_distance *
                    collision_distance
                ):

                    self.catch_target()
                    return

            # ----------------------------------------------------
            # MISSED BALL
            # ----------------------------------------------------

            if (
                self.target_y -
                self.target_radius
                >
                self.cam_height
            ):

                # ANY ball missed = GAME OVER
                self.miss_target()
                return

    # ============================================================
    # DRAW START SCREEN
    # ============================================================

    def draw_start_screen(self, screen):

        width = screen.get_width()
        height = screen.get_height()

        screen.fill(self.BG)

        # --------------------------------------------------------
        # Background grid
        # --------------------------------------------------------

        grid_spacing = 40

        for x in range(
            0,
            width,
            grid_spacing
        ):

            pygame.draw.line(
                screen,
                (15, 22, 40),
                (x, 0),
                (x, height),
                1
            )

        for y in range(
            0,
            height,
            grid_spacing
        ):

            pygame.draw.line(
                screen,
                (15, 22, 40),
                (0, y),
                (width, y),
                1
            )

        # --------------------------------------------------------
        # Accent
        # --------------------------------------------------------

        pygame.draw.rect(
            screen,
            self.RED,
            (0, 0, width, 6)
        )

        # --------------------------------------------------------
        # Title
        # --------------------------------------------------------

        title = self.big_font.render(
            "MOTIONSTRIKE",
            True,
            self.WHITE
        )

        title_rect = title.get_rect(
            center=(width // 2, 75)
        )

        screen.blit(
            title,
            title_rect
        )

        subtitle = self.medium_font.render(
            "CATCH THE VIRUS",
            True,
            self.CYAN
        )

        subtitle_rect = subtitle.get_rect(
            center=(width // 2, 130)
        )

        screen.blit(
            subtitle,
            subtitle_rect
        )

        # --------------------------------------------------------
        # Main card
        # --------------------------------------------------------

        card_width = min(
            1000,
            width - 120
        )

        card_height = 500

        card_x = (
            width -
            card_width
        ) // 2

        card_y = 165

        pygame.draw.rect(
            screen,
            self.PANEL,
            (
                card_x,
                card_y,
                card_width,
                card_height
            ),
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            (40, 55, 85),
            (
                card_x,
                card_y,
                card_width,
                card_height
            ),
            width=2,
            border_radius=20
        )

        # --------------------------------------------------------
        # NAME INPUT
        # --------------------------------------------------------

        name_title = self.medium_font.render(
            "PLAYER NAME",
            True,
            self.MUTED
        )

        screen.blit(
            name_title,
            (
                card_x + 45,
                card_y + 28
            )
        )

        name_box = pygame.Rect(
            card_x + 45,
            card_y + 68,
            card_width - 90,
            52
        )

        pygame.draw.rect(
            screen,
            (7, 11, 22),
            name_box,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.CYAN,
            name_box,
            width=2,
            border_radius=10
        )

        name_text = self.player_name

        if not name_text:

            name_text = "Type your name..."

            name_color = self.MUTED

        else:

            name_color = self.WHITE

        name_surface = self.medium_font.render(
            name_text,
            True,
            name_color
        )

        screen.blit(
            name_surface,
            (
                name_box.x + 16,
                name_box.y + 10
            )
        )

        # --------------------------------------------------------
        # HOW TO PLAY
        # --------------------------------------------------------

        rules_title = self.medium_font.render(
            "HOW TO PLAY",
            True,
            self.CYAN
        )

        screen.blit(
            rules_title,
            (
                card_x + 45,
                card_y + 145
            )
        )

        rules = [
            (
                "1",
                "CATCH EVERY BALL BEFORE IT FALLS",
                self.WHITE
            ),
            (
                "2",
                "MISS ANY BALL = GAME OVER",
                self.RED
            ),
            (
                "3",
                "ORANGE BALL = -30 POINTS",
                self.ORANGE
            ),
        ]

        rule_y = card_y + 190

        for number, text, color in rules:

            # Number badge
            pygame.draw.circle(
                screen,
                color,
                (
                    card_x + 67,
                    rule_y + 15
                ),
                17
            )

            number_surface = self.small_font.render(
                number,
                True,
                self.BG
            )

            number_rect = number_surface.get_rect(
                center=(
                    card_x + 67,
                    rule_y + 15
                )
            )

            screen.blit(
                number_surface,
                number_rect
            )

            rule_surface = self.medium_font.render(
                text,
                True,
                color
            )

            screen.blit(
                rule_surface,
                (
                    card_x + 100,
                    rule_y
                )
            )

            rule_y += 48

        # --------------------------------------------------------
        # CONTROLS
        # --------------------------------------------------------

        controls = self.small_font.render(
            "MOVE YOUR HAND  •  CATCH THE BALLS  •  ESC TO QUIT",
            True,
            self.MUTED
        )

        controls_rect = controls.get_rect(
            center=(
                width // 2,
                card_y + 375
            )
        )

        screen.blit(
            controls,
            controls_rect
        )

        # --------------------------------------------------------
        # START PROMPT
        # --------------------------------------------------------

        start_text = self.medium_font.render(
            "PRESS ENTER TO START",
            True,
            self.GREEN
        )

        start_rect = start_text.get_rect(
            center=(
                width // 2,
                card_y + 425
            )
        )

        screen.blit(
            start_text,
            start_rect
        )

        # --------------------------------------------------------
        # Footer
        # --------------------------------------------------------

        footer = self.tiny_font.render(
            "SJS COMPUTER EXHIBITION 2026  •  MOTION TRACKING GAME",
            True,
            (90, 100, 125)
        )

        footer_rect = footer.get_rect(
            center=(
                width // 2,
                height - 18
            )
        )

        screen.blit(
            footer,
            footer_rect
        )

    # ============================================================
    # DRAW GAMEPLAY
    # ============================================================

    def draw(self, screen, scale_x=1.0, scale_y=1.0):

        if self.state == "START":

            self.draw_start_screen(screen)
            return

        if self.state == "GAME_OVER":

            self.draw_game_over(screen)
            return

        # --------------------------------------------------------
        # GAME HUD
        # --------------------------------------------------------

        width = screen.get_width()

        hud_height = 82

        pygame.draw.rect(
            screen,
            (5, 8, 16),
            (0, 0, width, hud_height)
        )

        pygame.draw.line(
            screen,
            (40, 55, 85),
            (0, hud_height),
            (width, hud_height),
            2
        )

        section_width = width // 3

        # SCORE
        screen.blit(
            self.score_label,
            (
                35,
                10
            )
        )

        score_text = self.medium_font.render(
            str(self.score),
            True,
            self.WHITE
        )

        screen.blit(
            score_text,
            (
                35,
                40
            )
        )

        # LEVEL
        level_label_rect = self.level_label.get_rect(
            center=(
                section_width + section_width // 2,
                25
            )
        )

        screen.blit(
            self.level_label,
            level_label_rect
        )

        level_text = self.medium_font.render(
            str(self.level),
            True,
            self.CYAN
        )

        level_rect = level_text.get_rect(
            center=(
                section_width + section_width // 2,
                58
            )
        )

        screen.blit(
            level_text,
            level_rect
        )

        # LIFE
        life_label_rect = self.life_label.get_rect(
            center=(
                section_width * 2 +
                section_width // 2,
                25
            )
        )

        screen.blit(
            self.life_label,
            life_label_rect
        )

        # One-life indicator
        heart_x = (
            section_width * 2 +
            section_width // 2
        )

        heart_y = 56

        pygame.draw.circle(
            screen,
            self.RED,
            (
                heart_x - 7,
                heart_y - 3
            ),
            7
        )

        pygame.draw.circle(
            screen,
            self.RED,
            (
                heart_x + 7,
                heart_y - 3
            ),
            7
        )

        pygame.draw.polygon(
            screen,
            self.RED,
            [
                (
                    heart_x - 14,
                    heart_y
                ),
                (
                    heart_x + 14,
                    heart_y
                ),
                (
                    heart_x,
                    heart_y + 16
                )
            ]
        )

        # --------------------------------------------------------
        # TARGET
        # --------------------------------------------------------

        if self.target:

            tx = int(
                self.target_x * scale_x
            )

            ty = int(
                self.target_y * scale_y
            )

            radius = int(
                self.target_radius *
                min(scale_x, scale_y)
            )

            # Glow
            glow_radius = radius + 9

            pygame.draw.circle(
                screen,
                (25, 35, 55),
                (
                    tx,
                    ty
                ),
                glow_radius
            )

            # ----------------------------------------------------
            # NORMAL
            # ----------------------------------------------------

            if self.target_type == "normal":

                pygame.draw.circle(
                    screen,
                    self.BLUE,
                    (
                        tx,
                        ty
                    ),
                    radius
                )

                pygame.draw.circle(
                    screen,
                    self.CYAN,
                    (
                        tx,
                        ty
                    ),
                    radius,
                    3
                )

                pygame.draw.circle(
                    screen,
                    self.WHITE,
                    (
                        tx - 7,
                        ty - 7
                    ),
                    4
                )

            # ----------------------------------------------------
            # VIRUS
            # ----------------------------------------------------

            elif self.target_type == "virus":

                pygame.draw.circle(
                    screen,
                    self.RED,
                    (
                        tx,
                        ty
                    ),
                    radius
                )

                pygame.draw.circle(
                    screen,
                    (255, 110, 120),
                    (
                        tx,
                        ty
                    ),
                    radius,
                    3
                )

                # Virus eyes
                pygame.draw.circle(
                    screen,
                    self.WHITE,
                    (
                        tx - 8,
                        ty - 4
                    ),
                    4
                )

                pygame.draw.circle(
                    screen,
                    self.WHITE,
                    (
                        tx + 8,
                        ty - 4
                    ),
                    4
                )

                pygame.draw.line(
                    screen,
                    self.WHITE,
                    (
                        tx - 8,
                        ty + 8
                    ),
                    (
                        tx + 8,
                        ty + 8
                    ),
                    3
                )

            # ----------------------------------------------------
            # POWERUP
            # ----------------------------------------------------

            elif self.target_type == "powerup":

                pygame.draw.circle(
                    screen,
                    self.GREEN,
                    (
                        tx,
                        ty
                    ),
                    radius
                )

                pygame.draw.circle(
                    screen,
                    self.WHITE,
                    (
                        tx,
                        ty
                    ),
                    radius,
                    3
                )

                # Plus
                pygame.draw.line(
                    screen,
                    self.BG,
                    (
                        tx - 10,
                        ty
                    ),
                    (
                        tx + 10,
                        ty
                    ),
                    5
                )

                pygame.draw.line(
                    screen,
                    self.BG,
                    (
                        tx,
                        ty - 10
                    ),
                    (
                        tx,
                        ty + 10
                    ),
                    5
                )

            # ----------------------------------------------------
            # ORANGE DANGER BALL
            # ----------------------------------------------------

            elif self.target_type == "danger":

                pygame.draw.circle(
                    screen,
                    self.ORANGE,
                    (
                        tx,
                        ty
                    ),
                    radius
                )

                pygame.draw.circle(
                    screen,
                    self.YELLOW,
                    (
                        tx,
                        ty
                    ),
                    radius,
                    3
                )

                # Minus symbol
                pygame.draw.line(
                    screen,
                    self.BG,
                    (
                        tx - 10,
                        ty
                    ),
                    (
                        tx + 10,
                        ty
                    ),
                    5
                )

    # ============================================================
    # GAME OVER SCREEN
    # ============================================================

    def draw_game_over(self, screen):

        width = screen.get_width()
        height = screen.get_height()

        screen.fill(self.BG)

        # Background grid

        for x in range(
            0,
            width,
            40
        ):

            pygame.draw.line(
                screen,
                (14, 20, 35),
                (x, 0),
                (x, height),
                1
            )

        for y in range(
            0,
            height,
            40
        ):

            pygame.draw.line(
                screen,
                (14, 20, 35),
                (0, y),
                (width, y),
                1
            )

        # Main panel

        panel_width = min(
            900,
            width - 100
        )

        panel_height = min(
            620,
            height - 80
        )

        panel_x = (
            width -
            panel_width
        ) // 2

        panel_y = (
            height -
            panel_height
        ) // 2

        pygame.draw.rect(
            screen,
            self.PANEL,
            (
                panel_x,
                panel_y,
                panel_width,
                panel_height
            ),
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            self.RED,
            (
                panel_x,
                panel_y,
                panel_width,
                panel_height
            ),
            width=2,
            border_radius=20
        )

        # Game over title

        title = self.big_font.render(
            "GAME OVER",
            True,
            self.RED
        )

        title_rect = title.get_rect(
            center=(
                width // 2,
                panel_y + 65
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # Player

        player_text = self.medium_font.render(
            self.player_name.strip() or "PLAYER",
            True,
            self.WHITE
        )

        player_rect = player_text.get_rect(
            center=(
                width // 2,
                panel_y + 120
            )
        )

        screen.blit(
            player_text,
            player_rect
        )

        # Score

        score_caption = self.small_font.render(
            "FINAL SCORE",
            True,
            self.MUTED
        )

        score_caption_rect = score_caption.get_rect(
            center=(
                width // 2,
                panel_y + 165
            )
        )

        screen.blit(
            score_caption,
            score_caption_rect
        )

        score_text = self.big_font.render(
            str(self.score),
            True,
            self.CYAN
        )

        score_rect = score_text.get_rect(
            center=(
                width // 2,
                panel_y + 220
            )
        )

        screen.blit(
            score_text,
            score_rect
        )

        # Leaderboard title

        leaderboard_title = self.medium_font.render(
            "LEADERBOARD",
            True,
            self.WHITE
        )

        leaderboard_rect = leaderboard_title.get_rect(
            center=(
                width // 2,
                panel_y + 285
            )
        )

        screen.blit(
            leaderboard_title,
            leaderboard_rect
        )

        # Leaderboard rows

        top_scores = self.leaderboard[:5]

        row_y = panel_y + 325

        for index, entry in enumerate(
            top_scores
        ):

            name = str(
                entry.get(
                    "name",
                    "PLAYER"
                )
            )

            score = int(
                entry.get(
                    "score",
                    0
                )
            )

            rank = f"{index + 1}."

            rank_surface = self.small_font.render(
                rank,
                True,
                self.CYAN
            )

            name_surface = self.small_font.render(
                name[:20],
                True,
                self.WHITE
            )

            score_surface = self.small_font.render(
                str(score),
                True,
                self.YELLOW
            )

            screen.blit(
                rank_surface,
                (
                    panel_x + 70,
                    row_y
                )
            )

            screen.blit(
                name_surface,
                (
                    panel_x + 115,
                    row_y
                )
            )

            score_rect = score_surface.get_rect(
                right=panel_x +
                panel_width -
                70,
                top=row_y
            )

            screen.blit(
                score_surface,
                score_rect
            )

            row_y += 32

        # Restart prompt

        restart = self.small_font.render(
            "PRESS ENTER TO PLAY AGAIN     •     ESC TO QUIT",
            True,
            self.GREEN
        )

        restart_rect = restart.get_rect(
            center=(
                width // 2,
                panel_y +
                panel_height -
                30
            )
        )

        screen.blit(
            restart,
            restart_rect
        )

    # ============================================================
    # KEYBOARD INPUT
    # ============================================================

    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        # --------------------------------------------------------
        # START SCREEN
        # --------------------------------------------------------

        if self.state == "START":

            if event.key == pygame.K_BACKSPACE:

                self.player_name = (
                    self.player_name[:-1]
                )

            elif event.key == pygame.K_RETURN:

                if self.player_name.strip():

                    self.start()

            elif event.key == pygame.K_ESCAPE:

                self.state = "QUIT"

            else:

                # Accept normal printable characters
                if len(self.player_name) < 18:

                    if event.unicode.isprintable():

                        self.player_name += (
                            event.unicode
                        )

        # --------------------------------------------------------
        # GAME OVER
        # --------------------------------------------------------

        elif self.state == "GAME_OVER":

            if event.key == pygame.K_RETURN:

                self.player_name = ""
                self.start()

            elif event.key == pygame.K_ESCAPE:

                self.state = "QUIT"