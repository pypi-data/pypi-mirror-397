import pygame

class TileMap:
    def __init__(self,data,tile_size,tileset):
        self.data=data
        self.ts=tile_size
        self.tileset=tileset
    def draw(self,screen):
        for y,row in enumerate(self.data):
            for x,t in enumerate(row):
                if t>=0:
                    screen.blit(self.tileset[t],(x*self.ts,y*self.ts))
