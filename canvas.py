class PseudoCanvas:
    def __init__(self, canvas, x_offset=0, y_offset=0):
        if isinstance(canvas, PseudoCanvas):
            self.canvas = canvas.canvas
            self.x_offset = x_offset + canvas.x_offset
            self.y_offset = y_offset + canvas.y_offset
        else:
            self.canvas = canvas
            self.x_offset = x_offset
            self.y_offset = y_offset

    def draw(self, image, x, y):
        self.canvas.paste(image, (int(x + self.x_offset), int(y + self.y_offset)), image)
