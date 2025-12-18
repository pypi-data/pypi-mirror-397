class Entity:
    def __init__(self):
        self.c={}
    def add(self,k,v):
        self.c[k]=v

class System:
    def update(self,entities,dt):
        pass

class World:
    def __init__(self):
        self.entities=[]
        self.systems=[]
    def add_entity(self,e):
        self.entities.append(e)
    def add_system(self,s):
        self.systems.append(s)
    def update(self,dt):
        for s in self.systems:
            s.update(self.entities,dt)
