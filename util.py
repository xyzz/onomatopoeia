def unsignedToSigned(i, max_positive):
    if i < max_positive:
        return i
    else:
        return i - 2 * max_positive


def readU8(f):
    return ord(f.read(1))


def readU16(f):
    return ord(f.read(1)) * 256 + ord(f.read(1))


def readU32(f):
    return ord(f.read(1)) * 256 * 256 * 256 + ord(f.read(1)) * 256 * 256 + ord(f.read(1)) * 256 + ord(f.read(1))


def readS32(f):
    return unsignedToSigned(ord(f.read(1)) * 256 * 256 * 256 + ord(f.read(1)) * 256 * 256 + ord(f.read(1)) * 256 + ord(f.read(1)), 2 ** 31)
