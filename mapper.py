#!/usr/bin/env python2
import os.path
import os
import sys
from PIL import Image, ImageDraw
from map import Map
from blocks import build_block
from constants import *
from util import *

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
    "default:wood": ("default_wood.png", "default_wood.png"),
    "fire:basic_flame": ("fire_basic_flame.png", "fire_basic_flame.png"),
    "wool:white": ("wool_white.png", "wool_white.png"),
    "wool:grey": ("wool_grey.png", "wool_grey.png"),
    "wool:black": ("wool_black.png", "wool_black.png"),
    "wool:red": ("wool_red.png", "wool_red.png"),
    "wool:yellow": ("wool_yellow.png", "wool_yellow.png"),
    "wool:green": ("wool_green.png", "wool_green.png"),
    "wool:cyan": ("wool_cyan.png", "wool_cyan.png"),
    "wool:blue": ("wool_blue.png", "wool_blue.png"),
    "wool:magenta": ("wool_magenta.png", "wool_magenta.png"),
    "wool:orange": ("wool_orange.png", "wool_orange.png"),
    "wool:violet": ("wool_violet.png", "wool_violet.png"),
    "wool:brown": ("wool_brown.png", "wool_brown.png"),
    "wool:pink": ("wool_pink.png", "wool_pink.png"),
    "wool:dark_grey": ("wool_dark_grey.png", "wool_dark_grey.png"),
    "wool:dark_green": ("wool_dark_green.png", "wool_dark_green.png")
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
    """ returns max y of visible node """
    map_block = map.getBlock(bx, by, bz)
    maxy = -1
    for y in range(NODES_PER_BLOCK):
        for z in range(NODES_PER_BLOCK):
            for x in range(NODES_PER_BLOCK):
                p = map_block.get(x, y, z)
                if p in textures:
                    drawNode(canvas, x + bx * NODES_PER_BLOCK, y + by * NODES_PER_BLOCK, z + bz * NODES_PER_BLOCK, blocks[p], start)
                    maxy = max(maxy, y + by * NODES_PER_BLOCK)
    return maxy

cached_chunks = {}

def makeChunk(cx, cz):
    maxy = -1
    canvas = Image.new("RGBA", (BLOCK_SIZE, CHUNK_HEIGHT))
    for by in range(-8, 8):
        maxy = max(maxy, drawBlock(canvas, cx, by, cz, (BLOCK_SIZE/2 * (cx - cz + 1) - NODE_SIZE/2, BLOCK_SIZE/4 * (BLOCKS_PER_CHUNK - cz - cx) - NODE_SIZE/2)))
    return canvas, maxy


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
    maxy = -1
    chunk, y = makeChunk(x, z)
    maxy = max(maxy, y)
    canvas.paste(chunk, (0, step * BLOCK_SIZE/2), chunk)
    del chunk
    chunk, y = makeChunk(x + 1, z)
    maxy = max(maxy, y)
    canvas.paste(chunk, (-BLOCK_SIZE/2, step * BLOCK_SIZE/2 + BLOCK_SIZE/4), chunk)
    del chunk
    chunk, y = makeChunk(x, z + 1)
    maxy = max(maxy, y)
    canvas.paste(chunk, (BLOCK_SIZE/2, step * BLOCK_SIZE/2 + BLOCK_SIZE/4), chunk)
    del chunk
    return maxy


saved_tiles = set()


def saveTile(tile, row, col, zoom=5):
    if (row, col, zoom) in saved_tiles:
        print("WARN: tile %d %d @ %d already saved!" % (row, col, zoom))
    else:
        path = os.path.join("data", str(zoom), str(row))
        if not os.path.exists(path):
            os.makedirs(path)
        tile.save(os.path.join(path, "%d.png" % col))
        saved_tiles.add((row, col, zoom))


# row = x + z
# col = z - x
# x = (row - col) / 2
# z = (row + col) / 2
def dummyMakeTile(row, col):
    x, z = gridToCoords(row, col)
    canvas = Image.new("RGBA", (BLOCK_SIZE, 18 * BLOCK_SIZE/2))
    back = Image.new("RGBA", (BLOCK_SIZE, 18 * BLOCK_SIZE/2))
    for i in range(1, -17, -1):
        chunks3(back, x + i, z + i, 16 + i)
        back.paste(canvas, (0, 0), canvas)
        canvas, back = back, canvas

        canvas.save("%d.png" % i)

        tile = canvas.crop((0, 16 * BLOCK_SIZE/2, BLOCK_SIZE, 18 * BLOCK_SIZE/2))
        alpha = tile.split()[-1]
        fail = False
        for x in alpha.getdata():
            if x == 0:
                fail = True
                break
        if not fail:
            print("not fail! %d" % i)
            del canvas
            del back
            saveTile(tile, row / 4, col / 2)
            return

    tile = canvas.crop((0, 16 * BLOCK_SIZE/2, BLOCK_SIZE, 18 * BLOCK_SIZE/2))
    del back
    del canvas
    saveTile(tile, row / 4, col / 2)



cnt = 0
done = set()

# assume it's safe to start with (x, z)
def stupidMakeTiles(x, z):
    # TODO:                                  v
    canvas = Image.new("RGBA", (BLOCK_SIZE, 100 * BLOCK_SIZE))
    step = 0
    last = 0
    while True:
        print("tiling %d %d" % (x + step, z + step))
        row, col = coordsToGrid(x + step, z + step)
        y = chunks3(canvas, x + step, z + step, step)
        #canvas.save("step_{}.png".format(step))
        if row % 4 == 0:
            tile = canvas.crop((0, last, BLOCK_SIZE, last + BLOCK_SIZE))
            last += BLOCK_SIZE
            saveTile(tile, row / 4, col / 2)
            del tile
            global cnt
            cnt += 1
        done.add((x + step, z + step))
        step += 1
        print("y is %d" % y)
        if y == -1:
            break


def getNext(row, col):
    if (row, col) not in tile_next:
        # return something evil
        return (2 ** 16, 2 ** 16)
    return tile_next[(row, col)]


# last_drawn_row[col] => row
# used to determine chunks_in_row and not to redraw same tile several times
last_drawn_row = {}

def getLastDrawn(row):
    if row not in last_drawn_row:
        return -2 ** 16
    return last_drawn_row[row]


# assume it's safe to start with (x, z)
def stupidMakeTilesV2(row, col):
    CHUNKS_IN_ROW = 0
    stop_at = row
    while CHUNKS_IN_ROW < 10 and getLastDrawn(stop_at) < row:
        stop_at += 1
        CHUNKS_IN_ROW += 1
    print "CHUNKS_IN_ROW is set to %d" % CHUNKS_IN_ROW
    if CHUNKS_IN_ROW == 0:
        return
    CHUNKS_BUFFER = 50
    width = CHUNKS_IN_ROW * BLOCK_SIZE
    height = CHUNKS_BUFFER * BLOCK_SIZE/2 + (CHUNK_HEIGHT - BLOCK_SIZE/2)
    canvas = Image.new("RGBA", (width, height))
    step = 0
    delta = 0
    break_in = -1
    while True:
        print("step %d" % step)
        if break_in < 0:
            min_next_row = 2 ** 16
            for i in range(CHUNKS_IN_ROW + step % 2):
                cur_row = row + step
                cur_col = col - step % 2 + 2 * i
                if (cur_row, cur_col) in needed_tiles:
                    done.add((cur_row, cur_col))
                x, z = gridToCoords(cur_row, cur_col)
                chunk = makeChunk(x, z)
                X = BLOCK_SIZE * i - BLOCK_SIZE/2 * (step % 2)
                Y = BLOCK_SIZE/4 * step
                canvas.paste(chunk[0], (X, Y - delta), chunk[0])

                min_next_row = min(min_next_row, getNext(cur_row, cur_col)[0])
                last_drawn_row[cur_col] = cur_row

        if step % 3 == 2:
            for i in range(CHUNKS_IN_ROW):
                X = i * BLOCK_SIZE
                Y = BLOCK_SIZE * ((step - 6) // 3)
                Y = BLOCK_SIZE * (step // 3)
                tile = canvas.crop((X, Y - delta, X + BLOCK_SIZE, Y + BLOCK_SIZE - delta))
                cur_row = row + step
                cur_col = col + 2 * i
                cur_row -= 1
                if cur_row % 2 == 1:
                    cur_row -= 1
                drawn_tiles.add((cur_row, cur_col))
                saveTile(tile, cur_row // 3, cur_col / 2)
                del tile
        step += 1
        if break_in < 0:
            if step % CHUNKS_BUFFER == 0:
                print("reinit canvas")
                new_canvas = Image.new("RGBA", (width, height))
                part = canvas.crop((0, BLOCK_SIZE/2 * (CHUNKS_BUFFER - 2), width, height))
                new_canvas.paste(part, (0, 0), part)
                del canvas
                canvas = new_canvas
                delta += BLOCK_SIZE/2 * (CHUNKS_BUFFER - 2)

        if break_in == 0:
            break
        elif break_in > 0:
            print("break in %d" % break_in)
            break_in -= 1

        if break_in < 0:
            if min_next_row - (row + step) > 32:
                print("done, %d steps" % step)
                print("next row is %d" % min_next_row)
                break_in = CHUNKS_BUFFER * 3
    del canvas


def zoomTiles(to_join):
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

        for row, col in to_join:
            #print("join {} {}".format(row, col))
            R = row / 2
            C = col / 2
            path = os.path.join("data", str(zoom), str(R))
            if not os.path.exists(path):
                os.makedirs(path)
            canvas = Image.new("RGBA", (BLOCK_SIZE, BLOCK_SIZE))
            for dx in range(0, 2):
                for dz in range(0, 2):
                    try:
                        tile = Image.open(os.path.join("data", str(zoom + 1), str(row + dx), "%d.png" % (col + dz))).convert("RGBA")
                    except IOError:
                        tile = Image.new("RGBA", (BLOCK_SIZE, BLOCK_SIZE))
                    tile = tile.resize((BLOCK_SIZE/2, BLOCK_SIZE/2))
                    canvas.paste(tile, (dz * BLOCK_SIZE/2, dx * BLOCK_SIZE/2), tile)
            canvas.save(os.path.join(path, "%d.png" % C))


#stupidMakeTilesV2(-8, -8)
needed_tiles = set()
drawn_tiles = set()
raw_tiles = list(map.getCoordinatesToDraw())
tiles_to_start_draw = []
for row, col in raw_tiles:
    needed_tiles.add((row, col))
    if row % 3 == 0 and col % 2 == 0 and row % 4 == 2:
        tiles_to_start_draw.append((row, col))
tiles_to_start_draw.sort()

by_column = {}
for row, col in raw_tiles:
    if col not in by_column:
        by_column[col] = []
    by_column[col].append(row)

for col in by_column:
    by_column[col].sort()

tile_next = {}
for col in by_column:
    for i in range(len(by_column[col]) - 1):
        tile_next[(by_column[col][i], col)] = (by_column[col][i + 1], col)

for i in tile_next:
    print(i, " => ", tile_next[i])

try:
    done = set()
    """
    stupidMakeTilesV2(-18, -8)
    stupidMakeTilesV2(-12, -14)
    """
    for row, col in tiles_to_start_draw:
        if (row, col) not in done:
            print("[%.3f]" % (100.0 * len(done) / len(needed_tiles)))
            print("starting ", row, col)
            stupidMakeTilesV2(row, col)
except KeyboardInterrupt:
    print("Interrupted")

"""
if not os.path.exists("timestamp"):
    raw_coords = list(map.getCoordinatesToDraw())
    coords = []
    for row, col in raw_coords:
        if row % 4 != 0 or col % 2 != 0:
            continue
        coords.append(gridToCoords(row, col))
    coords.sort()

    for coord in coords:
        if coord in done:
            continue
        print("{0}% done".format(100.0 * cnt / len(coords)))
        stupidMakeTiles(*coord)
else:
    timestamp = int(open("timestamp").read())

    done = set()
    for coord in map.getCoordinates():
        if map.getBlock(*coord).timestamp > timestamp:
            dummyMakeTile(*coordsToGrid(coord[0], coord[1]))
"""

# zoom 4 ---> 0
zoomTiles(drawn_tiles)
