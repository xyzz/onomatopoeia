from constants import BLOCK_SIZE
import os
from PIL import Image

canvas = Image.new("RGBA", (5000, 8000))

offset_x = 2500
offset_y = 500

for row in os.listdir("data"):
    for col in os.listdir(os.path.join("data", row)):
        R = int(row)
        C = int(os.path.splitext(col)[0])
        print(R, C)
        particle = Image.open(os.path.join("data", row, col))
        canvas.paste(particle, (offset_x + C // 2 * BLOCK_SIZE, offset_y + R // 4 * BLOCK_SIZE), particle)

canvas.show()
