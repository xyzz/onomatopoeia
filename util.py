def getBlockAsInteger(x, y, z):
    return z * 16777216 + y * 4096 + x


def unsignedToSigned(i, max_positive):
    if i < max_positive:
        return i
    else:
        return i - 2 * max_positive


def getIntegerAsBlock(i):
    x = unsignedToSigned(i % 4096, 2048)
    i = int((i - x) / 4096)
    y = unsignedToSigned(i % 4096, 2048)
    i = int((i - y) / 4096)
    z = unsignedToSigned(i % 4096, 2048)
    return x,y,z


def readU8(f):
    return ord(f.read(1))


def readU16(f):
    return ord(f.read(1)) * 256 + ord(f.read(1))


def readU32(f):
    return ord(f.read(1)) * 256 * 256 * 256 + ord(f.read(1)) * 256 * 256 + ord(f.read(1)) * 256 + ord(f.read(1))


def readS32(f):
    return unsignedToSigned(ord(f.read(1)) * 256 * 256 * 256 + ord(f.read(1)) * 256 * 256 + ord(f.read(1)) * 256 + ord(f.read(1)), 2 ** 31)


def grid_to_coordinates(row, col):
    return (col + row) / 2, (col - row) / 2


def coordinates_to_grid(x, z):
    return x - z, x + z
