import pygame

class Events:
    def poll(self):
        return pygame.event.get()

    def quit(self, events):
        return any(e.type == pygame.QUIT for e in events)

    def key(self, k):
        return pygame.key.get_pressed()[k]

    def mouse(self):
        return pygame.mouse.get_pos(), pygame.mouse.get_pressed()
