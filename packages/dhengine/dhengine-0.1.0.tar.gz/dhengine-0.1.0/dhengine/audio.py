import pygame
pygame.mixer.init()

class Sound:
    def __init__(self, path):
        self.s = pygame.mixer.Sound(path)

    def play(self):
        self.s.play()

class Music:
    def load(self, path):
        pygame.mixer.music.load(path)

    def play(self, loop=-1):
        pygame.mixer.music.play(loop)

    def stop(self):
        pygame.mixer.music.stop()
