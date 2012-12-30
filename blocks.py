# Taken from Minecraft Overviewer
import sys
import imp
import os
import os.path
import zipfile
from cStringIO import StringIO
import math
from random import randint
import numpy
from PIL import Image, ImageEnhance, ImageOps, ImageDraw
import logging
import functools


bgcolor=(26, 26, 26, 0)

extension_alpha_over = None


def alpha_over(dest, src, pos_or_rect=(0, 0), mask=None):
    """Composite src over dest, using mask as the alpha channel (if
    given), otherwise using src's alpha channel. pos_or_rect can
    either be a position or a rectangle, specifying where on dest to
    put src. Falls back to dest.paste() if the alpha_over extension
    can't be found."""
    if mask == None:
        mask = src

    global extension_alpha_over
    if extension_alpha_over != None:
        # extension ALWAYS expects rects, so convert if needed
        if len(pos_or_rect) == 2:
            pos_or_rect = (pos_or_rect[0], pos_or_rect[1], src.size[0], src.size[1])
        extension_alpha_over(dest, src, pos_or_rect, mask)
    else:
        # fallback
        dest.paste(src, pos_or_rect, mask)


def transform_image_top(img):
    """Takes a PIL image and rotates it left 45 degrees and shrinks the y axis
    by a factor of 2. Returns the resulting image, which will be 24x12 pixels

    """

    # Resize to 17x17, since the diagonal is approximately 24 pixels, a nice
    # even number that can be split in half twice
    img = img.resize((17, 17), Image.ANTIALIAS)

    # Build the Affine transformation matrix for this perspective
    transform = numpy.matrix(numpy.identity(3))
    # Translate up and left, since rotations are about the origin
    transform *= numpy.matrix([[1,0,8.5],[0,1,8.5],[0,0,1]])
    # Rotate 45 degrees
    ratio = math.cos(math.pi/4)
    #transform *= numpy.matrix("[0.707,-0.707,0;0.707,0.707,0;0,0,1]")
    transform *= numpy.matrix([[ratio,-ratio,0],[ratio,ratio,0],[0,0,1]])
    # Translate back down and right
    transform *= numpy.matrix([[1,0,-12],[0,1,-12],[0,0,1]])
    # scale the image down by a factor of 2
    transform *= numpy.matrix("[1,0,0;0,2,0;0,0,1]")

    transform = numpy.array(transform)[:2,:].ravel().tolist()

    newimg = img.transform((24,12), Image.AFFINE, transform)
    return newimg


def transform_image_side(img):
    """Takes an image and shears it for the left side of the cube (reflect for
    the right side)"""

    # Size of the cube side before shear
    img = img.resize((12,12), Image.ANTIALIAS)

    # Apply shear
    transform = numpy.matrix(numpy.identity(3))
    transform *= numpy.matrix("[1,0,0;-0.5,1,0;0,0,1]")

    transform = numpy.array(transform)[:2,:].ravel().tolist()

    newimg = img.transform((12,18), Image.AFFINE, transform)
    return newimg


def transform_image_slope(img):
    """Takes an image and shears it in the shape of a slope going up
    in the -y direction (reflect for +x direction). Used for minetracks"""

    # Take the same size as trasform_image_side
    img = img.resize((12,12), Image.ANTIALIAS)

    # Apply shear
    transform = numpy.matrix(numpy.identity(3))
    transform *= numpy.matrix("[0.75,-0.5,3;0.25,0.5,-3;0,0,1]")
    transform = numpy.array(transform)[:2,:].ravel().tolist()

    newimg = img.transform((24,24), Image.AFFINE, transform)

    return newimg


def transform_image_angle(img, angle):
    """Takes an image an shears it in arbitrary angle with the axis of
    rotation being vertical.

    WARNING! Don't use angle = pi/2 (or multiplies), it will return
    a blank image (or maybe garbage).

    NOTE: angle is in the image not in game, so for the left side of a
    block angle = 30 degree.
    """

    # Take the same size as trasform_image_side
    img = img.resize((12,12), Image.ANTIALIAS)

    # some values
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    # function_x and function_y are used to keep the result image in the 
    # same position, and constant_x and constant_y are the coordinates
    # for the center for angle = 0.
    constant_x = 6.
    constant_y = 6.
    function_x = 6.*(1-cos_angle)
    function_y = -6*sin_angle
    big_term = ( (sin_angle * (function_x + constant_x)) - cos_angle* (function_y + constant_y))/cos_angle

    # The numpy array is not really used, but is helpful to 
    # see the matrix used for the transformation.
    transform = numpy.array([[1./cos_angle, 0, -(function_x + constant_x)/cos_angle],
                             [-sin_angle/(cos_angle), 1., big_term ],
                             [0, 0, 1.]])

    transform = tuple(transform[0]) + tuple(transform[1])

    newimg = img.transform((24,24), Image.AFFINE, transform)

    return newimg


def build_block(top, side):
    """From a top texture and a side texture, build a block image.
    top and side should be 16x16 image objects. Returns a 24x24 image

    """
    img = Image.new("RGBA", (24,24), bgcolor)

    original_texture = top.copy()
    top = transform_image_top(top)

    if not side:
        alpha_over(img, top, (0,0), top)
        return img

    side = transform_image_side(side)
    otherside = side.transpose(Image.FLIP_LEFT_RIGHT)

    # Darken the sides slightly. These methods also affect the alpha layer,
    # so save them first (we don't want to "darken" the alpha layer making
    # the block transparent)
    sidealpha = side.split()[3]
    side = ImageEnhance.Brightness(side).enhance(0.9)
    side.putalpha(sidealpha)
    othersidealpha = otherside.split()[3]
    otherside = ImageEnhance.Brightness(otherside).enhance(0.8)
    otherside.putalpha(othersidealpha)

    alpha_over(img, top, (0,0), top)
    alpha_over(img, side, (0,6), side)
    alpha_over(img, otherside, (12,6), otherside)

    # Manually touch up 6 pixels that leave a gap because of how the
    # shearing works out. This makes the blocks perfectly tessellate-able
    for x,y in [(13,23), (17,21), (21,19)]:
        # Copy a pixel to x,y from x-1,y
        img.putpixel((x,y), img.getpixel((x-1,y)))
    for x,y in [(3,4), (7,2), (11,0)]:
        # Copy a pixel to x,y from x+1,y
        img.putpixel((x,y), img.getpixel((x+1,y)))

    return img

def build_full_block(top, side1, side2, side3, side4, bottom=None):
    """From a top texture, a bottom texture and 4 different side textures,
    build a full block with four differnts faces. All images should be 16x16 
    image objects. Returns a 24x24 image. Can be used to render any block.

    side1 is in the -y face of the cube     (top left, east)
    side2 is in the +x                      (top right, south)
    side3 is in the -x                      (bottom left, north)
    side4 is in the +y                      (bottom right, west)

    A non transparent block uses top, side 3 and side 4.

    If top is a tuple then first item is the top image and the second
    item is an increment (integer) from 0 to 16 (pixels in the
    original minecraft texture). This increment will be used to crop the
    side images and to paste the top image increment pixels lower, so if
    you use an increment of 8, it will draw a half-block.

    NOTE: this method uses the bottom of the texture image (as done in 
    minecraft with beds and cackes)

    """

    increment = 0
    if isinstance(top, tuple):
        increment = int(round((top[1] / 16.)*12.)) # range increment in the block height in pixels (half texture size)
        crop_height = increment
        top = top[0]
        if side1 != None:
            side1 = side1.copy()
            ImageDraw.Draw(side1).rectangle((0, 0,16,crop_height),outline=(0,0,0,0),fill=(0,0,0,0))
        if side2 != None:
            side2 = side2.copy()
            ImageDraw.Draw(side2).rectangle((0, 0,16,crop_height),outline=(0,0,0,0),fill=(0,0,0,0))
        if side3 != None:
            side3 = side3.copy()
            ImageDraw.Draw(side3).rectangle((0, 0,16,crop_height),outline=(0,0,0,0),fill=(0,0,0,0))
        if side4 != None:
            side4 = side4.copy()
            ImageDraw.Draw(side4).rectangle((0, 0,16,crop_height),outline=(0,0,0,0),fill=(0,0,0,0))

    img = Image.new("RGBA", (24,24), bgcolor)

    # first back sides
    if side1 != None :
        side1 = transform_image_side(side1)
        side1 = side1.transpose(Image.FLIP_LEFT_RIGHT)

        # Darken this side.
        sidealpha = side1.split()[3]
        side1 = ImageEnhance.Brightness(side1).enhance(0.9)
        side1.putalpha(sidealpha)

        alpha_over(img, side1, (0,0), side1)


    if side2 != None :
        side2 = transform_image_side(side2)

        # Darken this side.
        sidealpha2 = side2.split()[3]
        side2 = ImageEnhance.Brightness(side2).enhance(0.8)
        side2.putalpha(sidealpha2)

        alpha_over(img, side2, (12,0), side2)

    if bottom != None :
        bottom = transform_image_top(bottom)
        alpha_over(img, bottom, (0,12), bottom)

    # front sides
    if side3 != None :
        side3 = transform_image_side(side3)

        # Darken this side
        sidealpha = side3.split()[3]
        side3 = ImageEnhance.Brightness(side3).enhance(0.9)
        side3.putalpha(sidealpha)

        alpha_over(img, side3, (0,6), side3)

    if side4 != None :
        side4 = transform_image_side(side4)
        side4 = side4.transpose(Image.FLIP_LEFT_RIGHT)

        # Darken this side
        sidealpha = side4.split()[3]
        side4 = ImageEnhance.Brightness(side4).enhance(0.8)
        side4.putalpha(sidealpha)

        alpha_over(img, side4, (12,6), side4)

    if top != None :
        top = transform_image_top(top)
        alpha_over(img, top, (0, increment), top)

    return img
