class Graphics:
    def __init__(self, canvas):
        self.canvas = canvas

    def clear(self):
        self.canvas.delete("all")

    def rect(self, x, y, w, h, color="white"):
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=color, outline=""
        )

    def text(self, x, y, text, color="white"):
        self.canvas.create_text(x, y, text=text, fill=color, anchor="nw")
