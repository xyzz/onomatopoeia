from constants import NODES_PER_BLOCK, BLOCKS, NODE_SIZE, BLOCK_SIZE


class Block:
    def __init__(self, map_, x, y, z):
        self.map = map_
        self.x = x
        self.y = y
        self.z = z
        self.block = None

    def draw(self, canvas):
        if self.block is None:
            self.block = self.map.get_block(self.x, self.y, self.z)

        for y in range(NODES_PER_BLOCK):
            for x in range(NODES_PER_BLOCK):
                for z in range(NODES_PER_BLOCK - 1, -1, -1):
                    p = self.block.get(x, y, z)
                    if p in BLOCKS:
                        canvas.draw(BLOCKS[p],
                                    NODE_SIZE//2 * (x + z),
                                    (BLOCK_SIZE - NODE_SIZE) * 3 // 4 + NODE_SIZE//4 * (x - z - 2 * y))
