import pygame

class Sprite:
    def __init__(self, image, pos=(0,0)):
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self, x=0, y=0):
        self.rect.x += x
        self.rect.y += y

class Group:
    def __init__(self, *sprites):
        self.sprites = list(sprites)

    def add(self, s):
        self.sprites.append(s)

    def draw(self, screen):
        for s in self.sprites:
            s.draw(screen)
