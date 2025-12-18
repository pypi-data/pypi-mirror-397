import pygame

class Clock:
    def __init__(self, fps=60):
        self.c = pygame.time.Clock()
        self.fps = fps

    def tick(self):
        return self.c.tick(self.fps)
