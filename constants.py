import os
from PIL import Image

#   Y   Z
#   |  /
#   | /
#   |/
#    \
#     \
#      \
#       X


INF = 10 ** 5
NODE_SIZE = 24
NODES_PER_BLOCK = 16
BLOCK_SIZE = 16 * NODE_SIZE
CHUNK_HEIGHT = 16 * BLOCK_SIZE//2 + BLOCK_SIZE//2
BLOCKS_PER_CHUNK = 16

# performance settings
MAX_COLUMNS = 10
MAX_ROWS = 12

BLOCKS = {}
for filename in os.listdir("cache"):
    name = os.path.splitext(filename)[0]
    BLOCKS[name] = Image.open(os.path.join("cache", filename))
