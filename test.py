from chunk import Chunk
import unittest
from PIL import Image
from block import Block
from canvas import PseudoCanvas
from constants import BLOCK_SIZE
import constants
from map_drawer import MapDrawer


class DummyMapBlock():
    def get(self, x, y, z):
        return "default:nyancat"


class DummyMap():
    def get_draw_grid(self):
        out = set()
        for row in range(-100, 100):
            for col in range(-100, 100):
                if (row + col) % 2 == 0:
                    out.add((row, col))
        return out

    def get_block(self, x, y, z):
        return DummyMapBlock()


class TestMapper(unittest.TestCase):

    def setUp(self):
        self.map = DummyMap()

    def assertSameImages(self, first, second):
        if list(first.getdata()) != list(second.getdata()):
            raise self.failureException("Images differ")

    def test_block(self):
        im = Image.new("RGBA", (BLOCK_SIZE, BLOCK_SIZE))
        Block(self.map, 0, 0, 0).draw(PseudoCanvas(im))
        self.assertSameImages(Image.open("test_data/block.png"), im)

    def test_chunk(self):
        im = Image.new("RGBA", (BLOCK_SIZE, 17 * BLOCK_SIZE // 2))
        Chunk(self.map, 0, 0).draw(PseudoCanvas(im))
        self.assertSameImages(Image.open("test_data/chunk.png"), im)

    def test_map_one_step(self):
        x = MapDrawer(self.map, MAX_ROWS=4)
        x.draw_step(-3, 3, 0)
        self.assertSameImages(Image.open("test_data/map_one_step.png"), x.canvas)
