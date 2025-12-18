class Scene:
    def __init__(self):
        self.entities = []

    def add(self, entity):
        self.entities.append(entity)

    def update(self):
        for e in self.entities:
            if e.active:
                e.update()

    def draw(self, gfx):
        for e in self.entities:
            if e.active:
                e.draw(gfx)
