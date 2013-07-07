from block import Block
from canvas import PseudoCanvas
from constants import BLOCK_SIZE


class Chunk:
    def __init__(self, map_, x, z):
        self.map = map_
        self.x = x
        self.z = z

    def draw(self, canvas):
        for y in range(-8, 8):
            Block(self.map, self.x, y, self.z).draw(PseudoCanvas(canvas, 0, BLOCK_SIZE//2 * (7 - y)))
