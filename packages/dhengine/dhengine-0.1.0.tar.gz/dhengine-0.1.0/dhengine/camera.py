class Camera:
    def __init__(self):
        self.x=0
        self.y=0
    def follow(self,t):
        self.x=t.rect.centerx
        self.y=t.rect.centery
    def apply(self,r):
        return r.move(-self.x,-self.y)
