#!/usr/bin/env python2
import os.path
from PIL import Image
from map import Map
from blocks import build_block

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

start = (5000, 5000)

canvas = Image.new("RGBA", (10000, 10000))

map = Map(".")


def drawNode(canvas, x, y, z, block):
    canvas.paste(block, (start[0] - 12 * x + 12 * z, start[1] + 6 * x + 6 * z - 12 * y), block)


def drawBlock(canvas, bx, by, bz):
    map_block = map.getBlock(bx, by, bz)
    for y in range(16):
        for z in range(16):
            for x in range(16):
                p = map_block.get(x, y, z)
                if p in textures:
                    drawNode(canvas, x + bx * 16, y + by * 16, z + bz * 16, blocks[p])


P = 10
for by in range(-1, 2):
    for bz in range(-P, P):
        print(bz)
        for bx in range(-P, P):
            drawBlock(canvas, bx, by, bz)

canvas.save("map.png")
