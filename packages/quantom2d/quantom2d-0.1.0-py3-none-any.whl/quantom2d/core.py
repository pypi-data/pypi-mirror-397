import tkinter as tk

from .scene import Scene
from .graphics import Graphics
from .input import Input
from .time import Time

class Game:
    def __init__(self, width=800, height=600, title="Quantom2D", fps=60):
        self.root = tk.Tk()
        self.root.title(title)

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()

        self.graphics = Graphics(self.canvas)
        self.scene = Scene()
        self.fps = fps
        self.running = False

        self.root.bind("<KeyPress>", Input.key_down)
        self.root.bind("<KeyRelease>", Input.key_up)

    def set_scene(self, scene):
        self.scene = scene

    def start(self):
        self.running = True
        self._loop()
        self.root.mainloop()

    def _loop(self):
        if not self.running:
            return

        Time.update()
        self.scene.update()

        self.graphics.clear()
        self.scene.draw(self.graphics)

        delay = int(1000 / self.fps)
        self.root.after(delay, self._loop)
