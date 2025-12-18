import pygame
pygame.init()

class Window:
    def __init__(self, size=(800,600), title="DhEngine"):
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(title)

    def fill(self, color=(0,0,0)):
        self.screen.fill(color)

    def draw(self, obj):
        obj.draw(self.screen)

    def update(self):
        pygame.display.flip()
