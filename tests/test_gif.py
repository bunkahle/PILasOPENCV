from __future__ import print_function
import PILasOPENCV as Image
# from PIL import Image

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum

if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Gif(KaitaiStruct):
    """GIF (Graphics Interchange Format) is an image file format, developed
    in 1987. It became popular in 1990s as one of the main image formats
    used in World Wide Web.
    
    GIF format allows encoding of palette-based images up to 256 colors
    (each of the colors can be chosen from a 24-bit RGB
    colorspace). Image data stream uses LZW (Lempel–Ziv–Welch) lossless
    compression.
    
    Over the years, several version of the format were published and
    several extensions to it were made, namely, a popular Netscape
    extension that allows to store several images in one file, switching
    between them, which produces crude form of animation.
    
    Structurally, format consists of several mandatory headers and then
    a stream of blocks follows. Blocks can carry additional
    metainformation or image data.
    """

    class BlockType(Enum):
        extension = 33
        local_image_descriptor = 44
        end_of_file = 59

    class ExtensionLabel(Enum):
        graphic_control = 249
        comment = 254
        application = 255
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.hdr = self._root.Header(self._io, self, self._root)
        self.logical_screen_descriptor = self._root.LogicalScreenDescriptorStruct(self._io, self, self._root)
        if self.logical_screen_descriptor.has_color_table:
            self._raw_global_color_table = self._io.read_bytes((self.logical_screen_descriptor.color_table_size * 3))
            io = KaitaiStream(BytesIO(self._raw_global_color_table))
            self.global_color_table = self._root.ColorTable(io, self, self._root)

        self.blocks = []
        i = 0
        while True:
            _ = self._root.Block(self._io, self, self._root)
            self.blocks.append(_)
            if  ((self._io.is_eof()) or (_.block_type == self._root.BlockType.end_of_file)) :
                break
            i += 1

    class ImageData(KaitaiStruct):
        """
        .. seealso::
           - section 22 - https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lzw_min_code_size = self._io.read_u1()
            self.subblocks = self._root.Subblocks(self._io, self, self._root)


    class ColorTableEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.red = self._io.read_u1()
            self.green = self._io.read_u1()
            self.blue = self._io.read_u1()


    class LogicalScreenDescriptorStruct(KaitaiStruct):
        """
        .. seealso::
           - section 18 - https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.screen_width = self._io.read_u2le()
            self.screen_height = self._io.read_u2le()
            self.flags = self._io.read_u1()
            self.bg_color_index = self._io.read_u1()
            self.pixel_aspect_ratio = self._io.read_u1()

        @property
        def has_color_table(self):
            if hasattr(self, '_m_has_color_table'):
                return self._m_has_color_table if hasattr(self, '_m_has_color_table') else None

            self._m_has_color_table = (self.flags & 128) != 0
            return self._m_has_color_table if hasattr(self, '_m_has_color_table') else None

        @property
        def color_table_size(self):
            if hasattr(self, '_m_color_table_size'):
                return self._m_color_table_size if hasattr(self, '_m_color_table_size') else None

            self._m_color_table_size = (2 << (self.flags & 7))
            return self._m_color_table_size if hasattr(self, '_m_color_table_size') else None


    class LocalImageDescriptor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.left = self._io.read_u2le()
            self.top = self._io.read_u2le()
            self.width = self._io.read_u2le()
            self.height = self._io.read_u2le()
            self.flags = self._io.read_u1()
            if self.has_color_table:
                self._raw_local_color_table = self._io.read_bytes((self.color_table_size * 3))
                io = KaitaiStream(BytesIO(self._raw_local_color_table))
                self.local_color_table = self._root.ColorTable(io, self, self._root)

            self.image_data = self._root.ImageData(self._io, self, self._root)

        @property
        def has_color_table(self):
            if hasattr(self, '_m_has_color_table'):
                return self._m_has_color_table if hasattr(self, '_m_has_color_table') else None

            self._m_has_color_table = (self.flags & 128) != 0
            return self._m_has_color_table if hasattr(self, '_m_has_color_table') else None

        @property
        def has_interlace(self):
            if hasattr(self, '_m_has_interlace'):
                return self._m_has_interlace if hasattr(self, '_m_has_interlace') else None

            self._m_has_interlace = (self.flags & 64) != 0
            return self._m_has_interlace if hasattr(self, '_m_has_interlace') else None

        @property
        def has_sorted_color_table(self):
            if hasattr(self, '_m_has_sorted_color_table'):
                return self._m_has_sorted_color_table if hasattr(self, '_m_has_sorted_color_table') else None

            self._m_has_sorted_color_table = (self.flags & 32) != 0
            return self._m_has_sorted_color_table if hasattr(self, '_m_has_sorted_color_table') else None

        @property
        def color_table_size(self):
            if hasattr(self, '_m_color_table_size'):
                return self._m_color_table_size if hasattr(self, '_m_color_table_size') else None

            self._m_color_table_size = (2 << (self.flags & 7))
            return self._m_color_table_size if hasattr(self, '_m_color_table_size') else None


    class Block(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.block_type = self._root.BlockType(self._io.read_u1())
            _on = self.block_type
            if _on == self._root.BlockType.extension:
                self.body = self._root.Extension(self._io, self, self._root)
            elif _on == self._root.BlockType.local_image_descriptor:
                self.body = self._root.LocalImageDescriptor(self._io, self, self._root)


    class ColorTable(KaitaiStruct):
        """
        .. seealso::
           - section 19 - https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while not self._io.is_eof():
                self.entries.append(self._root.ColorTableEntry(self._io, self, self._root))
                i += 1



    class Header(KaitaiStruct):
        """
        .. seealso::
           - section 17 - https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\x47\x49\x46")
            self.version = (self._io.read_bytes(3)).decode(u"ASCII")


    class ExtGraphicControl(KaitaiStruct):
        """
        .. seealso::
           - section 23 - https://www.w3.org/Graphics/GIF/spec-gif89a.txt
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.block_size = self._io.ensure_fixed_contents(b"\x04")
            self.flags = self._io.read_u1()
            self.delay_time = self._io.read_u2le()
            self.transparent_idx = self._io.read_u1()
            self.terminator = self._io.ensure_fixed_contents(b"\x00")

        @property
        def transparent_color_flag(self):
            if hasattr(self, '_m_transparent_color_flag'):
                return self._m_transparent_color_flag if hasattr(self, '_m_transparent_color_flag') else None

            self._m_transparent_color_flag = (self.flags & 1) != 0
            return self._m_transparent_color_flag if hasattr(self, '_m_transparent_color_flag') else None

        @property
        def user_input_flag(self):
            if hasattr(self, '_m_user_input_flag'):
                return self._m_user_input_flag if hasattr(self, '_m_user_input_flag') else None

            self._m_user_input_flag = (self.flags & 2) != 0
            return self._m_user_input_flag if hasattr(self, '_m_user_input_flag') else None


    class Subblock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_bytes = self._io.read_u1()
            self.bytes = self._io.read_bytes(self.num_bytes)


    class ExtApplication(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.application_id = self._root.Subblock(self._io, self, self._root)
            self.subblocks = []
            i = 0
            while True:
                _ = self._root.Subblock(self._io, self, self._root)
                self.subblocks.append(_)
                if _.num_bytes == 0:
                    break
                i += 1


    class Subblocks(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while True:
                _ = self._root.Subblock(self._io, self, self._root)
                self.entries.append(_)
                if _.num_bytes == 0:
                    break
                i += 1


    class Extension(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.label = self._root.ExtensionLabel(self._io.read_u1())
            _on = self.label
            if _on == self._root.ExtensionLabel.application:
                self.body = self._root.ExtApplication(self._io, self, self._root)
            elif _on == self._root.ExtensionLabel.comment:
                self.body = self._root.Subblocks(self._io, self, self._root)
            elif _on == self._root.ExtensionLabel.graphic_control:
                self.body = self._root.ExtGraphicControl(self._io, self, self._root)
            else:
                self.body = self._root.Subblocks(self._io, self, self._root)


from kaitaistruct import KaitaiStream, BytesIO

images = "Images/hopper.gif", "Images/testcolors.gif"

gifread = open(images[0], "rb")
raw = gifread.read()
gifread.close()
print(len(raw))
data = Gif(KaitaiStream(BytesIO(raw)))
print("Header", data.hdr.magic, data.hdr.version)
lsd = data.logical_screen_descriptor
print("Color table size", repr(lsd.color_table_size), "Has color table", lsd.has_color_table, "Image width", lsd.screen_width, "image height", lsd.screen_height, "Flags", lsd.flags, "Background color", lsd.bg_color_index, "Pixel aspect ratio", lsd.pixel_aspect_ratio)
print("Length color table", len(data.global_color_table.entries))
gcte = data.global_color_table.entries
color_table = []
for i in range(len(gcte)):
	color_table.append((gcte[i].red, gcte[i].green, gcte[i].blue))
print("Color table values", color_table)
print(len(data.blocks))
idesc = -1
for i in range(len(data.blocks)):
	print(data.blocks[i].block_type)
	if data.blocks[i].block_type == Gif.BlockType.local_image_descriptor:
		idesc = i
	try:
		print(data.blocks[i].body)
	except:
		pass
print("ImageData block in idesc", idesc)
imgdata = data.blocks[idesc].body.image_data
print(type(imgdata), imgdata.lzw_min_code_size, len(imgdata.subblocks.entries))
alle = 0
for i in range(len(imgdata.subblocks.entries)):
	print(imgdata.subblocks.entries[i].num_bytes)
	block_len = imgdata.subblocks.entries[i].num_bytes
	alle = alle + block_len
	print(len(imgdata.subblocks.entries[i].bytes), repr(imgdata.subblocks.entries[i].bytes))
print("alle", alle)
