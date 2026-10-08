"""Sound effects, synthesised in code so no audio files need to be shipped.

If no audio device is available the mixer can't start; in that case every
play_* method silently does nothing and the game runs without sound.
"""
import math
from array import array

import pygame

PEAK = 0.4  # fraction of full volume, keeps the tones comfortable


def _tone(freq, ms, sample_rate, channels, wave="sine"):
    """Build one tone as raw 16-bit samples, with a short fade in/out so it
    doesn't click at the start and end."""
    n = int(sample_rate * ms / 1000)
    fade = max(1, int(sample_rate * 0.01))
    samples = array("h")
    for i in range(n):
        phase = 2 * math.pi * freq * i / sample_rate
        value = math.sin(phase)
        if wave == "square":
            value = 1.0 if value >= 0 else -1.0
        env = min(1.0, i / fade, (n - i) / fade)
        sample = int(32767 * PEAK * env * value)
        samples.extend([sample] * channels)
    return samples


def _build(notes, sample_rate, channels):
    """Join (freq, ms, wave) notes into one pygame Sound."""
    data = array("h")
    for freq, ms, wave in notes:
        data.extend(_tone(freq, ms, sample_rate, channels, wave))
    return pygame.mixer.Sound(buffer=data.tobytes())


class Sounds:
    def __init__(self):
        self.enabled = False
        self.go = self.false_start = self.session_end = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sample_rate, fmt, channels = pygame.mixer.get_init()
            if fmt != -16:  # we generate signed 16-bit samples
                pygame.mixer.quit()
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
                sample_rate, fmt, channels = pygame.mixer.get_init()

            # "go": short, bright beep
            self.go = _build([(880, 160, "sine")], sample_rate, channels)
            # false start: low, harsh buzz
            self.false_start = _build([(140, 380, "square")], sample_rate, channels)
            # session end: rising C-E-G arpeggio, held on the last note
            self.session_end = _build(
                [(523, 140, "sine"), (659, 140, "sine"), (784, 360, "sine")],
                sample_rate, channels,
            )
            self.enabled = True
        except (pygame.error, NotImplementedError, OSError):
            self.enabled = False

    def _play(self, sound):
        if self.enabled and sound is not None:
            sound.play()

    def play_go(self):
        self._play(self.go)

    def play_false_start(self):
        self._play(self.false_start)

    def play_session_end(self):
        self._play(self.session_end)
