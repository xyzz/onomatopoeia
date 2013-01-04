import sqlite3
import cStringIO
import zlib
import array
import os.path
from util import *


TRANSLATION_TABLE = {
    1: 0x800,  # CONTENT_GRASS
    4: 0x801,  # CONTENT_TREE
    5: 0x802,  # CONTENT_LEAVES
    6: 0x803,  # CONTENT_GRASS_FOOTSTEPS
    7: 0x804,  # CONTENT_MESE
    8: 0x805,  # CONTENT_MUD
    10: 0x806,  # CONTENT_CLOUD
    11: 0x807,  # CONTENT_COALSTONE
    12: 0x808,  # CONTENT_WOOD
    13: 0x809,  # CONTENT_SAND
    18: 0x80a,  # CONTENT_COBBLE
    19: 0x80b,  # CONTENT_STEEL
    20: 0x80c,  # CONTENT_GLASS
    22: 0x80d,  # CONTENT_MOSSYCOBBLE
    23: 0x80e,  # CONTENT_GRAVEL
    24: 0x80f,  # CONTENT_SANDSTONE
    25: 0x810,  # CONTENT_CACTUS
    26: 0x811,  # CONTENT_BRICK
    27: 0x812,  # CONTENT_CLAY
    28: 0x813,  # CONTENT_PAPYRUS
    29: 0x814}  # CONTENT_BOOKSHELF


class Map(object):
    def __init__(self, path):
        self.conn = sqlite3.connect(os.path.join(path, "map.sqlite"))

    def getCoordinates(self):
        result = []
        cur = self.conn.cursor()
        cur.execute("SELECT `pos` FROM `blocks`")
        while True:
            r = cur.fetchone()
            if not r:
                break
            x, y, z = getIntegerAsBlock(r[0])
            result.append((x, y, z))
        return result

    def getCoordinatesToDraw(self):
        result = set()
        raw = self.getCoordinates()
        for coord in raw:
            result.add(coordsToGrid(coord[0], coord[1]))
        return result

    def getBlock(self, x, y, z):
        cur = self.conn.cursor()
        cur.execute("SELECT `data` FROM `blocks` WHERE `pos`==? LIMIT 1", (getBlockAsInteger(x, y, z), ))
        r = cur.fetchone()
        if not r:
            return DummyMapBlock()
        return MapBlock(r[0])


class MapBlock(object):
    def __init__(self, data):
        f = cStringIO.StringIO(data)
        version = readU8(f)
        flags = f.read(1)

        # Check flags
        is_underground = ((ord(flags) & 1) != 0)
        day_night_differs = ((ord(flags) & 2) != 0)
        lighting_expired = ((ord(flags) & 4) != 0)
        generated = ((ord(flags) & 8) != 0)

        if version >= 22:
            content_width = readU8(f)
            params_width = readU8(f)

        # Node data
        dec_o = zlib.decompressobj()
        try:
            mapdata = array.array("B", dec_o.decompress(f.read()))
        except:
            mapdata = []

        # Reuse the unused tail of the file
        f.close()
        f = cStringIO.StringIO(dec_o.unused_data)

        # zlib-compressed node metadata list
        dec_o = zlib.decompressobj()
        try:
            metaliststr = array.array("B", dec_o.decompress(f.read()))
            # And do nothing with it
        except:
            metaliststr = []

        # Reuse the unused tail of the file
        f.close()
        f = cStringIO.StringIO(dec_o.unused_data)
        data_after_node_metadata = dec_o.unused_data

        if version <= 21:
            # mapblockobject_count
            readU16(f)

        if version == 23:
            readU8(f)  # Unused node timer version (always 0)
        if version == 24:
            ver = readU8(f)
            if ver == 1:
                num = readU16(f)
                for i in range(0, num):
                    readU16(f)
                    readS32(f)
                    readS32(f)

        static_object_version = readU8(f)
        static_object_count = readU16(f)
        for i in range(0, static_object_count):
            # u8 type (object type-id)
            object_type = readU8(f)
            # s32 pos_x_nodes * 10000
            pos_x_nodes = readS32(f) / 10000
            # s32 pos_y_nodes * 10000
            pos_y_nodes = readS32(f) / 10000
            # s32 pos_z_nodes * 10000
            pos_z_nodes = readS32(f) / 10000
            # u16 data_size
            data_size = readU16(f)
            # u8[data_size] data
            data = f.read(data_size)

        timestamp = readU32(f)

        id_to_name = {}
        if version >= 22:
            name_id_mapping_version = readU8(f)
            num_name_id_mappings = readU16(f)
            for i in range(0, num_name_id_mappings):
                node_id = readU16(f)
                name_len = readU16(f)
                name = f.read(name_len)
                id_to_name[node_id] = name

        # Node timers
        if version >= 25:
            timer_size = readU8(f)
            num = readU16(f)
            for i in range(0, num):
                readU16(f)
                readS32(f)
                readS32(f)

        self.id_to_name = id_to_name
        self.mapdata = mapdata
        self.version = version
        self.timestamp = timestamp

    def get(self, x, y, z):
        datapos = x + y * 16 + z * 256
        return self.id_to_name[(self.mapdata[datapos * 2] << 8) | (self.mapdata[datapos * 2 + 1])]
        # TODO: v
        return (self.mapdata[datapos*2] << 8) | (self.mapdata[datapos*2 + 1])
        if self.version >= 24:
            return (self.mapdata[datapos*2] << 8) | (self.mapdata[datapos*2 + 1])
        elif self.version >= 20:
            if self.mapdata[datapos] < 0x80:
                return self.mapdata[datapos]
            else:
                return (self.mapdata[datapos] << 4) | (self.mapdata[datapos + 0x2000] >> 4)
        elif 16 <= self.version < 20:
            return TRANSLATION_TABLE.get(self.mapdata[datapos], self.mapdata[datapos])
        else:
            raise Exception("Unsupported map format: " + str(self.version))


class DummyMapBlock(object):
    def get(self, x, y, z):
        return "default:air"
