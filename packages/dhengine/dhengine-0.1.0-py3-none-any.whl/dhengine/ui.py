import pygame

class Button:
    def __init__(self,rect,text,font):
        self.rect=pygame.Rect(rect)
        self.text=text
        self.font=font
    def draw(self,screen):
        pygame.draw.rect(screen,(100,100,100),self.rect)
        t=self.font.render(self.text)
        screen.blit(t,t.get_rect(center=self.rect.center))
    def clicked(self,pos):
        return self.rect.collidepoint(pos)
