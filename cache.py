from PIL import Image
from blocks import build_block
import os
from textures import TEXTURES

for name in TEXTURES:
    print(name)
    top = Image.open(os.path.join("textures", TEXTURES[name][0])).convert("RGBA")
    side = Image.open(os.path.join("textures", TEXTURES[name][1])).convert("RGBA")
    build_block(top, side).save(os.path.join("cache", "{}.png".format(name)))
