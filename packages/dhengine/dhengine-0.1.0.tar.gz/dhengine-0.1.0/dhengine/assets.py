import pygame

class Image:
    def load(self, path):
        return pygame.image.load(path).convert_alpha()

class Font:
    def __init__(self, path=None, size=24):
        self.f = pygame.font.Font(path, size)

    def render(self, text, color=(255,255,255)):
        return self.f.render(text, True, color)
