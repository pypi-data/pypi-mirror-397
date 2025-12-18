class Body:
    def __init__(self,rect,vel=(0,0),gravity=0):
        self.rect=rect
        self.vx,self.vy=vel
        self.g=gravity
    def update(self):
        self.vy+=self.g
        self.rect.x+=self.vx
        self.rect.y+=self.vy

def collide(a,b):
    return a.rect.colliderect(b.rect)
