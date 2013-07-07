from canvas import PseudoCanvas
from chunk import Chunk
from constants import MAX_ROWS, BLOCK_SIZE, MAX_COLUMNS, BLOCKS_PER_CHUNK
from util import grid_to_coordinates
from PIL import Image
import os


def save_tile(canvas, row, col):
    if not os.path.exists("data/{}".format(row)):
        os.mkdir("data/{}".format(row))
    canvas.save("data/{}/{}.png".format(row, col))


class MapDrawer:
    def __init__(self, map_, MAX_ROWS=MAX_ROWS):
        self.map = map_
        self.MAX_ROWS = MAX_ROWS
        if self.MAX_ROWS % 4 != 0:
            raise Exception("`MAX_ROWS` must be divisible by 4")
        self.width = MAX_COLUMNS * BLOCK_SIZE
        self.height = BLOCK_SIZE // 4 * (self.MAX_ROWS + 1) + BLOCKS_PER_CHUNK * BLOCK_SIZE // 2
        self.canvas = None
        self.init_canvas()
        self.grid = self.map.get_draw_grid()

    def init_canvas(self):
        if self.canvas:
            del self.canvas
        self.canvas = Image.new("RGBA", (self.width, self.height))

    def draw_step(self, L, R, row):
        """Draw MAX_ROWS rows on canvas (thus fill it entirely)"""
        if row % 4 != 0:
            raise Exception("`row` must be divisible by 4")
        for i in range(self.MAX_ROWS):
            for col in range(L, R + 1):
                if (row, col) in self.grid:
                    y_offset = BLOCK_SIZE / 4 * i
                    x_offset = (col - L) * BLOCK_SIZE / 2
                    x, z = grid_to_coordinates(row, col)
                    Chunk(self.map, x, z).draw(PseudoCanvas(self.canvas, x_offset, y_offset))

                    print row, col
            row += 1
        return row

    def draw_range(self, L, R):
        """Generate tiles for rows in range [L; R]"""
        ROW_START = 0
        ROW_END = 50

        row = ROW_START
        last_tiled = ROW_START - 1
        while row <= ROW_END:
            started_at = row
            row = self.draw_step(L, R, row)
            # our canvas is about to end!
            # (this also means it's the time to crop some tiles)
            end = row - 2
            if row > ROW_END:
                end = started_at + MAX_ROWS + BLOCKS_PER_CHUNK
            for r in range(last_tiled + 1, end):
                for c in range(L + 1, R):
                    if r % 4 == 0 and c % 2 == 0:
                        x = (c - L) * BLOCK_SIZE//2
                        y = (r - started_at) * BLOCK_SIZE//4
                        C = self.canvas.crop((x, y, x + BLOCK_SIZE, y + BLOCK_SIZE))
                        save_tile(C, r, c)
                        last_tiled = r

            # to not lose any data we crop part of the image and move it on top
            remove = MAX_ROWS * BLOCK_SIZE // 4
            c = self.canvas.crop((0, remove, self.width, self.height))
            c.load()
            self.init_canvas()
            self.canvas.paste(c, (0, 0), c)
