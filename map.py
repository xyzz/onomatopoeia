import sqlite3
import cStringIO
import zlib
import array
import os.path
from util import *


def getBlockAsInteger(x, y, z):
    return z * 16777216 + y * 4096 + x


class Map(object):
    def __init__(self, path):
        self.conn = sqlite3.connect(os.path.join(path, "map.sqlite"))

    def getBlock(self, x, y, z):
        cur = self.conn.cursor()
        cur.execute("SELECT `data` FROM `blocks` WHERE `pos`==? LIMIT 1", (getBlockAsInteger(x, y, z), ))
        r = cur.fetchone()
        if not r:
            return DummyMapBlock()
        f = cStringIO.StringIO(r[0])
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

        #print(id_to_name)
        #print(mapdata)
        return MapBlock(id_to_name, mapdata)


class MapBlock(object):
    def __init__(self, id_to_name, mapdata, version=99):
        self.id_to_name = id_to_name
        self.mapdata = mapdata
        self.version = version

    def get(self, x, y, z):
        datapos = x + y * 16 + z * 256
        return self.id_to_name[(self.mapdata[datapos * 2] << 8) | (self.mapdata[datapos * 2 + 1])]


class DummyMapBlock(object):
    def get(self, x, y, z):
        return "default:air"
