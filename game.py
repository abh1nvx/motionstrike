import pygame
import random
import json
from pathlib import Path


class Game:

    # COLORS
    BG = (7, 10, 20)
    PANEL = (12, 17, 31)
    WHITE = (245, 248, 255)
    MUTED = (145, 155, 180)
    CYAN = (0, 220, 255)
    BLUE = (70, 130, 255)
    PURPLE = (160, 90, 255)
    GREEN = (70, 255, 150)
    RED = (255, 65, 80)
    ORANGE = (255, 150, 40)
    YELLOW = (255, 220, 70)

    def __init__(self, cam_width=640, cam_height=480):
        self.cam_width = cam_width
        self.cam_height = cam_height

        self.big_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.medium_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.tiny_font = pygame.font.SysFont("Arial", 16)

        self.state = "START"
        self.player_name = ""
        self.score = 0
        self.lives = 1
        self.level = 1

        self.target = None
        self.target_type = None
        self.target_x = 0
        self.target_y = 0
        self.target_radius = 25

        self.spawn_timer = 0.0
        self.spawn_interval = 0.62
        self.target_timer = 0.0
        self.virus_duration = 2.35

        self.base_speeds = {
            "normal": 220,
            "virus": 205,
            "powerup": 245,
            "danger": 235,
        }

        self.level_thresholds = [0, 25, 60, 110, 180, 270, 390, 540]

        # Reset leaderboard when the app launches
        self.leaderboard_file = str(
            Path(__file__).parent / "motionstrike_leaderboard.json"
        )
        self.leaderboard = []
        self.save_leaderboard()

        # Sound
        self.sounds_enabled = False
        self.sounds = {}
        self.music_loaded = False
        self.load_sounds()

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
    # SOUND SYSTEM
    # ============================================================

    def load_sounds(self):
        self.sounds_enabled = False
        self.sounds = {}
        self.music_loaded = False

        sound_folder = Path(__file__).parent / "sounds"

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sounds_enabled = True
        except pygame.error as error:
            print("Audio could not be initialized:", error)
            return

        music_path = sound_folder / "background_music.mp3"

        try:
            if music_path.exists():
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(0.25)
                self.music_loaded = True
                print("Background music loaded!")
            else:
                print("Missing background music:", music_path)
        except pygame.error as error:
            print("Background music could not load:", error)

        for key, filename in (
            ("touch", "touch.mp3"),
            ("quit", "quit.mp3"),
        ):
            sound_path = sound_folder / filename

            try:
                if sound_path.exists():
                    self.sounds[key] = pygame.mixer.Sound(str(sound_path))
                    self.sounds[key].set_volume(0.7)
                    print(filename, "loaded!")
                else:
                    print("Missing sound:", sound_path)
            except pygame.error as error:
                print(filename, "could not load:", error)

    def play_sound(self, name):
        if not self.sounds_enabled:
            return

        sound = self.sounds.get(name)

        if sound:
            try:
                sound.play()
            except pygame.error as error:
                print("Sound playback error:", error)

    def start_music(self):
        if not self.sounds_enabled or not self.music_loaded:
            return

        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        except pygame.error as error:
            print("Music playback error:", error)

    def play_quit_sound(self):
        if not self.sounds_enabled:
            return

        try:
            pygame.mixer.music.stop()
            quit_sound = self.sounds.get("quit")

            if quit_sound:
                channel = quit_sound.play()
                if channel:
                    while channel.get_busy():
                        pygame.time.wait(10)

        except pygame.error as error:
            print("Quit sound error:", error)

    # ============================================================
    # LEADERBOARD
    # ============================================================

    def load_leaderboard(self):
        try:
            with open(
                self.leaderboard_file, "r", encoding="utf-8"
            ) as file:
                data = json.load(file)

            return data if isinstance(data, list) else []

        except (OSError, json.JSONDecodeError) as error:
            print("Leaderboard load error:", error)
            return []

    def save_leaderboard(self):
        try:
            with open(
                self.leaderboard_file, "w", encoding="utf-8"
            ) as file:
                json.dump(self.leaderboard, file, indent=4)

        except OSError as error:
            print("Leaderboard save error:", error)

    def add_score_to_leaderboard(self):
        name = self.player_name.strip() or "PLAYER"

        self.leaderboard.append({
            "name": name,
            "score": int(self.score)
        })

        self.leaderboard.sort(
            key=lambda entry: entry.get("score", 0),
            reverse=True
        )

        self.leaderboard = self.leaderboard[:10]
        self.save_leaderboard()

    # ============================================================
    # GAME LOGIC
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

        self.spawn_target()
        self.start_music()

    def spawn_target(self):
        roll = random.random()

        if roll < 0.55:
            self.target_type = "normal"
        elif roll < 0.75:
            self.target_type = "virus"
        elif roll < 0.90:
            self.target_type = "powerup"
        else:
            self.target_type = "danger"

        margin = self.target_radius + 10

        self.target_x = random.randint(
            margin, self.cam_width - margin
        )
        self.target_y = -self.target_radius
        self.target_timer = 0.0
        self.target = True

    def get_target_speed(self):
        speed = self.base_speeds.get(self.target_type, 220)
        multiplier = 1.0 + (0.17 * (self.level - 1))
        return speed * multiplier

    def update_level(self):
        new_level = 1

        for index, threshold in enumerate(
            self.level_thresholds, start=1
        ):
            if self.score >= threshold:
                new_level = index

        self.level = new_level

    def catch_target(self):
        self.play_sound("touch")

        points = {
            "normal": 2,
            "virus": 10,
            "powerup": 5,
            "danger": -30,
        }

        self.score = max(
            0, self.score + points.get(self.target_type, 0)
        )

        self.update_level()
        self.target = None
        self.target_type = None
        self.spawn_timer = 0.0

    def miss_target(self):
        self.play_sound("quit")
        self.game_over()

    def game_over(self):
        if self.state == "GAME_OVER":
            return

        self.state = "GAME_OVER"
        self.target = None
        self.target_type = None
        self.add_score_to_leaderboard()

    def update(self, fingertip, dt):
        if self.state != "PLAYING":
            return

        dt = min(dt, 0.05)

        if self.target is None:
            self.spawn_timer += dt

            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0.0
                self.spawn_target()

        if self.target:
            self.target_y += self.get_target_speed() * dt
            self.target_timer += dt

            if fingertip is not None:
                fx, fy = fingertip
                dx = fx - self.target_x
                dy = fy - self.target_y

                if dx * dx + dy * dy <= 20 ** 2:
                    self.catch_target()
                    return

            if self.target_y - self.target_radius > self.cam_height:
                self.miss_target()
                return

    # ============================================================
    # DRAW START SCREEN
    # ============================================================

    def draw_start_screen(self, screen):
        width, height = screen.get_size()
        screen.fill(self.BG)

        for x in range(0, width, 40):
            pygame.draw.line(
                screen, (15, 22, 40), (x, 0), (x, height), 1
            )

        for y in range(0, height, 40):
            pygame.draw.line(
                screen, (15, 22, 40), (0, y), (width, y), 1
            )

        pygame.draw.rect(screen, self.RED, (0, 0, width, 6))

        title = self.big_font.render(
            "MOTIONSTRIKE", True, self.WHITE
        )
        screen.blit(title, title.get_rect(center=(width // 2, 75)))

        subtitle = self.medium_font.render(
            "CATCH THE VIRUS", True, self.CYAN
        )
        screen.blit(
            subtitle, subtitle.get_rect(center=(width // 2, 130))
        )

        card_width = min(1000, width - 120)
        card = pygame.Rect(
            (width - card_width) // 2, 165, card_width, 500
        )

        pygame.draw.rect(
            screen, self.PANEL, card, border_radius=20
        )
        pygame.draw.rect(
            screen, (40, 55, 85), card, 2, border_radius=20
        )

        name_title = self.medium_font.render(
            "PLAYER NAME", True, self.MUTED
        )
        screen.blit(name_title, (card.x + 45, card.y + 28))

        name_box = pygame.Rect(
            card.x + 45, card.y + 68, card.width - 90, 52
        )

        pygame.draw.rect(
            screen, (7, 11, 22), name_box, border_radius=10
        )
        pygame.draw.rect(
            screen, self.CYAN, name_box, 2, border_radius=10
        )

        name_text = self.player_name or "Type your name..."
        name_color = self.WHITE if self.player_name else self.MUTED

        name_surface = self.medium_font.render(
            name_text, True, name_color
        )
        screen.blit(
            name_surface, (name_box.x + 16, name_box.y + 10)
        )

        rules_title = self.medium_font.render(
            "HOW TO PLAY", True, self.CYAN
        )
        screen.blit(rules_title, (card.x + 45, card.y + 145))

        rules = [
            ("1", "CATCH EVERY BALL BEFORE IT FALLS", self.WHITE),
            ("2", "MISS ANY BALL = GAME OVER", self.RED),
            ("3", "ORANGE BALL = -30 POINTS", self.ORANGE),
        ]

        rule_y = card.y + 190

        for number, rule_text, color in rules:
            pygame.draw.circle(
                screen, color, (card.x + 67, rule_y + 15), 17
            )

            number_surface = self.small_font.render(
                number, True, self.BG
            )
            screen.blit(
                number_surface,
                number_surface.get_rect(
                    center=(card.x + 67, rule_y + 15)
                )
            )

            rule_surface = self.medium_font.render(
                rule_text, True, color
            )
            screen.blit(
                rule_surface, (card.x + 100, rule_y)
            )
            rule_y += 48

        controls = self.small_font.render(
            "MOVE YOUR HAND  •  CATCH THE BALLS  •  ESC TO QUIT",
            True, self.MUTED
        )
        screen.blit(
            controls,
            controls.get_rect(center=(width // 2, card.y + 375))
        )

        start_text = self.medium_font.render(
            "PRESS ENTER TO START", True, self.GREEN
        )
        screen.blit(
            start_text,
            start_text.get_rect(center=(width // 2, card.y + 425))
        )

        footer = self.tiny_font.render(
            "SJS COMPUTER EXHIBITION 2026  •  MOTION TRACKING GAME",
            True, (90, 100, 125)
        )
        screen.blit(
            footer,
            footer.get_rect(center=(width // 2, height - 18))
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

        width = screen.get_width()
        hud_height = 82

        pygame.draw.rect(
            screen, (5, 8, 16), (0, 0, width, hud_height)
        )
        pygame.draw.line(
            screen, (40, 55, 85),
            (0, hud_height), (width, hud_height), 2
        )

        section_width = width // 3

        screen.blit(self.score_label, (35, 10))

        score_text = self.medium_font.render(
            str(self.score), True, self.WHITE
        )
        screen.blit(score_text, (35, 40))

        level_center = section_width + section_width // 2
        screen.blit(
            self.level_label,
            self.level_label.get_rect(center=(level_center, 25))
        )

        level_text = self.medium_font.render(
            str(self.level), True, self.CYAN
        )
        screen.blit(
            level_text,
            level_text.get_rect(center=(level_center, 58))
        )

        life_center = section_width * 2 + section_width // 2
        screen.blit(
            self.life_label,
            self.life_label.get_rect(center=(life_center, 25))
        )

        pygame.draw.circle(
            screen, self.RED, (life_center - 7, 53), 7
        )
        pygame.draw.circle(
            screen, self.RED, (life_center + 7, 53), 7
        )
        pygame.draw.polygon(
            screen, self.RED,
            [
                (life_center - 14, 56),
                (life_center + 14, 56),
                (life_center, 72)
            ]
        )

        if not self.target:
            return

        tx = int(self.target_x * scale_x)
        ty = int(self.target_y * scale_y)
        radius = int(
            self.target_radius * min(scale_x, scale_y)
        )

        pygame.draw.circle(
            screen, (25, 35, 55), (tx, ty), radius + 9
        )

        if self.target_type == "normal":
            pygame.draw.circle(screen, self.BLUE, (tx, ty), radius)
            pygame.draw.circle(screen, self.CYAN, (tx, ty), radius, 3)
            pygame.draw.circle(
                screen, self.WHITE, (tx - 7, ty - 7), 4
            )

        elif self.target_type == "virus":
            pygame.draw.circle(screen, self.RED, (tx, ty), radius)
            pygame.draw.circle(
                screen, (255, 110, 120), (tx, ty), radius, 3
            )
            pygame.draw.circle(
                screen, self.WHITE, (tx - 8, ty - 4), 4
            )
            pygame.draw.circle(
                screen, self.WHITE, (tx + 8, ty - 4), 4
            )
            pygame.draw.line(
                screen, self.WHITE,
                (tx - 8, ty + 8), (tx + 8, ty + 8), 3
            )

        elif self.target_type == "powerup":
            pygame.draw.circle(screen, self.GREEN, (tx, ty), radius)
            pygame.draw.circle(
                screen, self.WHITE, (tx, ty), radius, 3
            )
            pygame.draw.line(
                screen, self.BG,
                (tx - 10, ty), (tx + 10, ty), 5
            )
            pygame.draw.line(
                screen, self.BG,
                (tx, ty - 10), (tx, ty + 10), 5
            )

        elif self.target_type == "danger":
            pygame.draw.circle(
                screen, self.ORANGE, (tx, ty), radius
            )
            pygame.draw.circle(
                screen, self.YELLOW, (tx, ty), radius, 3
            )
            pygame.draw.line(
                screen, self.BG,
                (tx - 10, ty), (tx + 10, ty), 5
            )

    # ============================================================
    # GAME OVER SCREEN
    # ============================================================

    def draw_game_over(self, screen):
        width, height = screen.get_size()
        screen.fill(self.BG)

        for x in range(0, width, 40):
            pygame.draw.line(
                screen, (14, 20, 35), (x, 0), (x, height), 1
            )

        for y in range(0, height, 40):
            pygame.draw.line(
                screen, (14, 20, 35), (0, y), (width, y), 1
            )

        panel_width = min(900, width - 100)
        panel_height = min(620, height - 80)
        panel_x = (width - panel_width) // 2
        panel_y = (height - panel_height) // 2

        panel = pygame.Rect(
            panel_x, panel_y, panel_width, panel_height
        )

        pygame.draw.rect(
            screen, self.PANEL, panel, border_radius=20
        )
        pygame.draw.rect(
            screen, self.RED, panel, 2, border_radius=20
        )

        title = self.big_font.render(
            "GAME OVER", True, self.RED
        )
        screen.blit(
            title,
            title.get_rect(center=(width // 2, panel_y + 65))
        )

        player_text = self.medium_font.render(
            self.player_name.strip() or "PLAYER",
            True, self.WHITE
        )
        screen.blit(
            player_text,
            player_text.get_rect(center=(width // 2, panel_y + 120))
        )

        score_caption = self.small_font.render(
            "FINAL SCORE", True, self.MUTED
        )
        screen.blit(
            score_caption,
            score_caption.get_rect(center=(width // 2, panel_y + 165))
        )

        score_text = self.big_font.render(
            str(self.score), True, self.CYAN
        )
        screen.blit(
            score_text,
            score_text.get_rect(center=(width // 2, panel_y + 220))
        )

        leaderboard_title = self.medium_font.render(
            "LEADERBOARD", True, self.WHITE
        )
        screen.blit(
            leaderboard_title,
            leaderboard_title.get_rect(center=(width // 2, panel_y + 285))
        )

        row_y = panel_y + 325

        for index, entry in enumerate(self.leaderboard[:5]):
            name = str(entry.get("name", "PLAYER"))
            score = int(entry.get("score", 0))

            rank_surface = self.small_font.render(
                f"{index + 1}.", True, self.CYAN
            )
            name_surface = self.small_font.render(
                name[:20], True, self.WHITE
            )
            score_surface = self.small_font.render(
                str(score), True, self.YELLOW
            )

            screen.blit(rank_surface, (panel_x + 70, row_y))
            screen.blit(name_surface, (panel_x + 115, row_y))
            screen.blit(
                score_surface,
                score_surface.get_rect(
                    right=panel_x + panel_width - 70,
                    top=row_y
                )
            )

            row_y += 32

        restart = self.small_font.render(
            "PRESS ENTER TO PLAY AGAIN     •     ESC TO QUIT",
            True, self.GREEN
        )
        screen.blit(
            restart,
            restart.get_rect(
                center=(width // 2, panel_y + panel_height - 30)
            )
        )

    # ============================================================
    # KEYBOARD INPUT
    # ============================================================

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "START":

            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]

            elif event.key == pygame.K_RETURN:
                if self.player_name.strip():
                    self.start()

            elif event.key == pygame.K_ESCAPE:
                self.play_quit_sound()
                self.state = "QUIT"

            elif len(self.player_name) < 18:
                if event.unicode.isprintable():
                    self.player_name += event.unicode

        elif self.state == "GAME_OVER":

            if event.key == pygame.K_RETURN:
                self.player_name = ""
                self.state = "START"

            elif event.key == pygame.K_ESCAPE:
                self.play_quit_sound()
                self.state = "QUIT"