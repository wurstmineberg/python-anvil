import gzip
import io
import nbt.nbt
import pathlib
import re
import zlib

class Region:
    def __init__(self, path):
        if isinstance(path, str):
            path = pathlib.Path(path)
        with path.open('rb') as f:
            data = f.read()
            self.locations = data[:4096]
            self.timestamps = data[4096:8192]
            self.data = data[8192:]
        match = re.search('r\.(-?[0-9]+)\.(-?[0-9]+)\.mca$', path.name)
        if match:
            self.x = int(match.group(1))
            self.z = int(match.group(2))
        else:
            self.x = None
            self.z = None

    def chunk_column(self, x, z):
        x_offset = x & 31
        z_offset = z & 31
        meta_offset = 4 * (x_offset + z_offset * 32)
        chunk_location = self.locations[meta_offset:meta_offset + 4]
        offset = chunk_location[0] * (256 ** 2) + chunk_location[1] * 256 + chunk_location[2]
        if offset == 0:
            return ChunkColumn(None, x=x, z=z)
        else:
            offset -= 2
        sector_count = chunk_location[3]
        return ChunkColumn(self.data[4096 * offset:4096 * (offset + sector_count)], x=x, z=z)

class ChunkColumn:
    def __init__(self, data, *, x=None, z=None):
        self.x = x
        self.z = z
        if data is None:
            self.data = None
            return
        length = data[0] * (256 ** 3) + data[1] * (256 ** 2) + data[2] * 256 + data[3]
        compression = data[4]
        compressed_data = data[5:4 + length]
        if compression == 1: # gzip
            decompress = gzip.decompress
        elif compression == 2: # zlib
            decompress = zlib.decompress
        else:
            raise ValueError('Unknown compression method: {}'.format(compression))
        self.data = nbt.nbt.NBTFile(buffer=io.BytesIO(decompress(compressed_data)))
