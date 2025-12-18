class Animation:
    def __init__(self,frames,speed=0.1):
        self.frames=frames
        self.speed=speed
        self.i=0
    def update(self):
        self.i=(self.i+self.speed)%len(self.frames)
    def frame(self):
        return self.frames[int(self.i)]
