from map_drawer import MapDrawer
import os
from chunk import Chunk
from block import Block
from canvas import PseudoCanvas
from constants import BLOCK_SIZE, INF, BLOCKS_PER_CHUNK, MAX_COLUMNS, MAX_ROWS
from map import Map
from PIL import Image
from util import grid_to_coordinates

map_ = Map(".")
grid = map_.get_draw_grid()
print(grid)

# canvas = Image.new("RGBA", (5000, 5000))
# Chunk(map_, 0, 0).draw(PseudoCanvas(canvas, 0, 0))
# Block(map_, 0, 0, 0).draw(PseudoCanvas(canvas, 0, 0))
# canvas.show()

drawer = MapDrawer(map_)
drawer.draw_range(-5, 5)