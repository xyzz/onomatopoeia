#!/usr/bin/env python2
import os.path
from PIL import Image
from map import Map
from blocks import build_block

# name: (top, side)
textures = {
    "default:bookshelf": ("default_bookshelf.png", "default_bookshelf.png"),
    "default:brick": ("default_brick.png", "default_brick.png"),
    "default:cactus": ("default_cactus_top.png", "default_cactus_side.png"),
    "default:chest": ("default_chest_top.png", "default_chest_front.png"),
    "default:chest_locked": ("default_chest_top.png", "default_chest_lock.png"),
    "default:clay": ("default_clay.png", "default_clay.png"),
    "default:cloud": ("default_cloud.png", "default_cloud.png"),
    "default:cobble": ("default_cobble.png", "default_cobble.png"),
    "default:desert_sand": ("default_desert_sand.png", "default_desert_sand.png"),
    "default:desert_stone": ("default_desert_stone.png", "default_desert_stone.png"),
    "default:dirt": ("default_dirt.png", "default_dirt.png"),
    "default:furnace": ("default_furnace_top.png", "default_furnace_front_active.png"),
    "default:glass": ("default_glass.png", "default_glass.png"),
    "default:dirt_with_grass": ("default_grass.png", "default_dirt.png"),
    "default:dirt_with_grass_footsteps": ("default_grass_footsteps.png", "default_dirt.png"),
    "default:gravel": ("default_gravel.png", "default_gravel.png"),
    "default:jungletree": ("default_jungletree_top.png", "default_jungletree.png"),
    "default:lava_source": ("default_lava.png", "default_lava.png"),
    "default:lava_flowing": ("default_lava.png", "default_lava.png"),
    "default:leaves": ("default_leaves.png", "default_leaves.png"),
    "default:mese": ("default_mese_block.png", "default_mese_block.png"),
    "default:stone_with_coal": ("default_mineral_coal.png", "default_mineral_coal.png"),
    "default:stone_with_iron": ("default_mineral_iron.png", "default_mineral_iron.png"),
    "default:stone_with_mese": ("default_mineral_mese.png", "default_mineral_mese.png"),
    "default:mossycobble": ("default_mossycobble.png", "default_mossycobble.png"),
    "default:nyancat": ("default_nc_side.png", "default_nc_front.png"),
    "default:nyancat_rainbow": ("default_nc_rb.png", "default_nc_rb.png"),
    "default:sand": ("default_sand.png", "default_sand.png"),
    "default:sandstone": ("default_sandstone.png", "default_sandstone.png"),
    "default:steelblock": ("default_steel_block.png", "default_steel_block.png"),
    "default:stone": ("default_stone.png", "default_stone.png"),
    "default:tree": ("default_tree_top.png", "default_tree.png"),
    "default:water_source": ("default_water.png", "default_water.png"),
    "default:water_flowing": ("default_water.png", "default_water.png"),
    "default:wood": ("default_wood.png", "default_wood.png")
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
