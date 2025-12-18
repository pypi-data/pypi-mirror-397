class Scene:
    def start(self):
        pass

    def update(self, dt):
        pass

    def draw(self, win):
        pass

class SceneManager:
    def __init__(self, scene):
        self.scene = scene
        self.scene.start()

    def switch(self, scene):
        self.scene = scene
        self.scene.start()
