import pygame
from .round import Round
from .sounds import Sounds

# Game Engine

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (190, 50, 50)

# Difficulty presets: (rounds, min wait ms, max wait ms), keyed by menu number.
DIFFICULTIES = {
    pygame.K_1: ("Easy", 3, 1500, 4000),
    pygame.K_2: ("Medium", 5, 1000, 3000),
    pygame.K_3: ("Hard", 8, 500, 2000),
}
KEYPAD = {pygame.K_KP1: pygame.K_1, pygame.K_KP2: pygame.K_2, pygame.K_KP3: pygame.K_3}


class GameEngine:
    def __init__(self, width, height, rounds_total=5, min_wait_ms=1000, max_wait_ms=3000):
        self.width = width
        self.height = height

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.round = Round(self.min_wait_ms, self.max_wait_ms)
        self.reaction_times = []

        self.result_shown_at = None
        self.result_pause_ms = 800  # brief pause on the result screen between rounds

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.difficulty = "Medium"
        self.game_over = False
        self.sounds = Sounds()

    def handle_event(self, event):
        if self.game_over:
            # Results screen: 1/2/3 start a new session at that difficulty,
            # Esc/Q quits. Clicks and Space are deliberately ignored so a
            # leftover tap from the last round can't trigger anything.
            if event.type == pygame.KEYDOWN:
                key = KEYPAD.get(event.key, event.key)
                if key in DIFFICULTIES:
                    self._start_game(key)
                elif key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        is_click = event.type == pygame.MOUSEBUTTONDOWN
        is_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        if (is_click or is_space) and self.round.state in ("waiting", "go"):
            reaction_ms = self.round.register_input()
            if reaction_ms is not None:
                self.reaction_times.append(reaction_ms)
            else:  # None means false start: not recorded
                self.sounds.play_false_start()
            self.result_shown_at = pygame.time.get_ticks()

    def _start_game(self, difficulty_key):
        name, rounds, min_wait, max_wait = DIFFICULTIES[difficulty_key]
        self.difficulty = name
        self.rounds_total = rounds
        self.min_wait_ms = min_wait
        self.max_wait_ms = max_wait
        self.reaction_times = []
        self.result_shown_at = None
        self.game_over = False
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def handle_input(self):
        # Reserved for continuously-held-key input; every action here
        # is a discrete click/keypress, handled in handle_event.
        pass

    def update(self):
        if self.game_over:
            return

        was_waiting = self.round.state == "waiting"
        self.round.update()
        if was_waiting and self.round.state == "go":
            self.sounds.play_go()

        if self.round.state in ("result", "false_start"):
            now = pygame.time.get_ticks()
            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_next_round(self):
        # A false start isn't recorded, so the round is simply replayed.
        if len(self.reaction_times) >= self.rounds_total:
            self.game_over = True
            self.sounds.play_session_end()
            return
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return round(sum(self.reaction_times) / len(self.reaction_times))

    def _render_game_over(self, screen):
        screen.fill(BLUE)

        title = self.big_font.render("Session Complete!", True, WHITE)
        screen.blit(title, title.get_rect(center=(self.width // 2, 40)))

        # One row per round; split into two columns for longer sessions.
        per_col = 5
        row_h = 34
        top = 95
        cols = (len(self.reaction_times) + per_col - 1) // per_col
        col_w = self.width // max(cols, 1)
        for i, ms in enumerate(self.reaction_times):
            col, row = divmod(i, per_col)
            row_surf = self.font.render(f"Round {i + 1}: {ms} ms", True, WHITE)
            x = col * col_w + (col_w - row_surf.get_width()) // 2
            screen.blit(row_surf, (x, top + row * row_h))

        avg = self.big_font.render(
            f"Average: {self.average_reaction_ms()} ms", True, WHITE
        )
        screen.blit(avg, avg.get_rect(center=(self.width // 2, 295)))

        menu = self.small_font.render(
            "Play again:  1 Easy   2 Medium   3 Hard", True, WHITE
        )
        screen.blit(menu, menu.get_rect(center=(self.width // 2, 347)))
        quit_hint = self.small_font.render("Esc / Q to quit", True, WHITE)
        screen.blit(quit_hint, quit_hint.get_rect(center=(self.width // 2, 377)))

    def render(self, screen):
        if self.game_over:
            self._render_game_over(screen)
            return

        if self.round.state == "waiting":
            bg = GRAY
            message = "Wait for green..."
        elif self.round.state == "go":
            bg = GREEN
            message = "Click now!"
        elif self.round.state == "false_start":
            bg = RED
            message = "False start! Too soon"
        else:
            bg = BLUE
            message = f"{self.round.reaction_ms} ms"

        screen.fill(bg)

        text_surf = self.big_font.render(message, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(text_surf, text_rect)

        round_num = min(len(self.reaction_times) + 1, self.rounds_total)
        round_text = self.font.render(f"Round {round_num}/{self.rounds_total}", True, WHITE)
        screen.blit(round_text, (10, 10))

        avg_text = self.font.render(f"Avg: {self.average_reaction_ms()} ms", True, WHITE)
        screen.blit(avg_text, (self.width - 190, 10))
