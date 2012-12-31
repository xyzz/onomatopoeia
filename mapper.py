#!/usr/bin/env python2
import os.path
import os
from PIL import Image, ImageDraw
from map import Map
from blocks import build_block
from constants import *
from util import *

# name: (top, side)
textures = {
    "default:dirt_with_grass": ("default_grass.png", "default_dirt.png"),
    "default:stone": ("default_stone.png", "default_stone.png"),
    "default:dirt": ("default_dirt.png", "default_dirt.png"),
    "default:tree": ("default_tree.png", "default_tree.png"),
    "default:leaves": ("default_leaves.png", "default_leaves.png"),
    "default:wood": ("default_wood.png", "default_wood.png"),
    "default:cobble": ("default_cobble.png", "default_cobble.png")
}

blocks = {}

for name in textures:
    top = Image.open(os.path.join("textures", textures[name][0])).convert("RGBA")
    side = Image.open(os.path.join("textures", textures[name][1])).convert("RGBA")
    blocks[name] = build_block(top, side)

map = Map(".")


def drawNode(canvas, x, y, z, block, start):
    canvas.paste(block, (start[0] + NODE_SIZE/2 * (z - x), start[1] + NODE_SIZE/4 * (x + z - 2 * y)), block)


def drawBlock(canvas, bx, by, bz, start):
    map_block = map.getBlock(bx, by, bz)
    for y in range(NODES_PER_BLOCK):
        for z in range(NODES_PER_BLOCK):
            for x in range(NODES_PER_BLOCK):
                p = map_block.get(x, y, z)
                if p in textures:
                    drawNode(canvas, x + bx * NODES_PER_BLOCK, y + by * NODES_PER_BLOCK, z + bz * NODES_PER_BLOCK, blocks[p], start)

cached_chunks = {}

def makeChunk(cx, cz):
    if (cx, cz) not in cached_chunks:
        canvas = Image.new("RGBA", (BLOCK_SIZE, CHUNK_HEIGHT))
        for by in range(-8, 8):
            drawBlock(canvas, cx, by, cz, (BLOCK_SIZE/2 * (cx - cz + 1) - NODE_SIZE/2, BLOCK_SIZE/4 * (BLOCKS_PER_CHUNK - cz - cx) - NODE_SIZE/2))
        cached_chunks[(cx, cz)] = canvas
    return cached_chunks[(cx, cz)]


def fullMap():
    canvas = Image.new("RGBA", (5000, 5000))
    start = (3000, 3000)
    for y in range(-1, 10):
        print(y)
        for z in range(-5, 5):
            for x in range(-5, 5):
                drawBlock(canvas, x, y, z, start)
    canvas.save("map.png")


def chunks3(canvas, x, z, step):
    chunk = makeChunk(x + step, z + step)
    canvas.paste(chunk, (0, (16 + step) * BLOCK_SIZE/2), chunk)
    #del chunk
    chunk = makeChunk(x + step + 1, z + step)
    canvas.paste(chunk, (-BLOCK_SIZE/2, (16 + step) * BLOCK_SIZE/2 + BLOCK_SIZE/4), chunk)
    #del chunk
    chunk = makeChunk(x + step, z + step + 1)
    canvas.paste(chunk, (BLOCK_SIZE/2, (16 + step) * BLOCK_SIZE/2 + BLOCK_SIZE/4), chunk)
    #del chunk

# row = x + z
# col = z - x
# x = (row - col) / 2
# z = (row + col) / 2
def dummyMakeTile(row, col):
    x, z = gridToCoords(row, col)
    x = (row - col) / 2
    z = (row + col) / 2
    canvas = Image.new("RGBA", (BLOCK_SIZE, 18 * BLOCK_SIZE/2))
    for i in range(-16, 2):
        print("step {}".format(i))
        chunks3(canvas, x, z, i)
    tile = canvas.crop((0, 16 * BLOCK_SIZE/2, BLOCK_SIZE, 18 * BLOCK_SIZE/2))
    del canvas
    return tile

coords = map.getCoordinatesToDraw()

step = 0
for row, col in coords:
    step += 1
    print("[{}%]".format(100.0 * step / len(coords)))
    if row % 4 != 0 or col % 2 != 0:
        continue
    path = os.path.join("data", "5", "{}".format(row / 4 ))
    if not os.path.exists(path):
        os.makedirs(path)
    dummyMakeTile(row, col).save(os.path.join(path, "{}.png".format(col / 2)))

# zoom 4 ---> 0

to_join = coords

for zoom in range(4, -1, -1):
    new_join = set()
    for row, col in to_join:
        if zoom == 4:
            if row % 4 != 0 or col % 2 != 0:
                continue
            row /= 4
            col /= 2
        if row % 2 == 1:
            row -= 1
        if col % 2 == 1:
            col -= 1
        new_join.add((row, col))
    to_join = new_join
    print(to_join)

    for row, col in to_join:
        #print("join {} {}".format(row, col))
        R = row / 2
        C = col / 2
        path = os.path.join("data", "{}".format(zoom), "{}".format(R))
        if not os.path.exists(path):
            os.makedirs(path)
        canvas = Image.new("RGBA", (BLOCK_SIZE, BLOCK_SIZE))
        for dx in range(0, 2):
            for dz in range(0, 2):
                if zoom == 3 and row == 2 and col == -2:
                    print("test...")
                try:
                    tile = Image.open(os.path.join("data", "{}".format(zoom + 1), "{}".format(row + dx), "{}.png".format(col + dz))).convert("RGBA")
                except IOError:
                    tile = Image.new("RGBA", (BLOCK_SIZE, BLOCK_SIZE))
                tile = tile.resize((BLOCK_SIZE/2, BLOCK_SIZE/2))
                canvas.paste(tile, (dz * BLOCK_SIZE/2, dx * BLOCK_SIZE/2), tile)
        canvas.save(os.path.join(path, "{}.png".format(C)))
