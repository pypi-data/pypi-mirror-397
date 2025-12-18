import pygame

class Fade:
    def __init__(self,size,color=(0,0,0)):
        self.s=pygame.Surface(size)
        self.s.fill(color)
        self.a=0
    def draw(self,screen,step=5):
        self.a=min(255,self.a+step)
        self.s.set_alpha(self.a)
        screen.blit(self.s,(0,0))
