# -*- coding: utf-8 -*-

from __future__ import print_function
import numpy as np
import cv2
import math, re, os, sys, tempfile

__author__ = 'imressed, bunkus'
# Constants (also defined in _imagingmodule.c!)

if sys.version[0] == "2":
    py3 = False
else:
    py3 = True
NONE = 0
MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 // 4 // 3)

# transpose
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1
ROTATE_90 = 2
ROTATE_180 = 3
ROTATE_270 = 4
TRANSPOSE = 5
TRANSVERSE = 6

# transforms
AFFINE = 0
EXTENT = 1
PERSPECTIVE = 2
QUAD = 3
MESH = 4

# resampling filters
NEAREST = NONE = 0
BOX = 4
BILINEAR = LINEAR = 2
HAMMING = 5
BICUBIC = CUBIC = 3
LANCZOS = ANTIALIAS = 1

# dithers
NEAREST = NONE = 0
ORDERED = 1  # Not yet implemented
RASTERIZE = 2  # Not yet implemented
FLOYDSTEINBERG = 3  # default

# palettes/quantizers
WEB = 0
ADAPTIVE = 1

MEDIANCUT = 0
MAXCOVERAGE = 1
FASTOCTREE = 2
LIBIMAGEQUANT = 3

# categories
NORMAL = 0
SEQUENCE = 1
CONTAINER = 2

NEAREST = cv2.INTER_NEAREST
BILINEAR = INTER_LINEAR = cv2.INTER_LINEAR
BICUBIC = cv2.INTER_CUBIC
LANCZOS = cv2.INTER_LANCZOS4
INTERAREA = cv2.INTER_AREA

# --------------------------------------------------------------------
# Registries

ID = []
OPEN = {}
MIME = {}
SAVE = {}
SAVE_ALL = {}
EXTENSION = {".bmp": "BMP", ".dib": "DIB", ".jpeg": "JPEG", ".jpg": "JPEG", ".jpe": "JPEG", ".jp2": "JPEG2000", ".png": "PNG",
             ".webp": "WEBP", ".pbm": "PBM", ".pgm": "PGM", ".ppm": "PPM", ".sr": "SR", ".ras": "RAS", ".tif": "TIFF", ".tiff": "TIFF"}
DECODERS = {}
ENCODERS = {}

# --------------------------------------------------------------------
# Modes supported by this version

_MODEINFO = {
    # NOTE: this table will be removed in future versions.  use
    # getmode* functions or ImageMode descriptors instead.

    # official modes
    "1": ("L", "L", ("1",)),
    "L": ("L", "L", ("L",)),
    "I": ("L", "I", ("I",)),
    "F": ("L", "F", ("F",)),
    "P": ("RGB", "L", ("P",)),
    "RGB": ("RGB", "L", ("R", "G", "B")),
    "RGBX": ("RGB", "L", ("R", "G", "B", "X")),
    "RGBA": ("RGB", "L", ("R", "G", "B", "A")),
    "CMYK": ("RGB", "L", ("C", "M", "Y", "K")),
    "YCbCr": ("RGB", "L", ("Y", "Cb", "Cr")),
    "LAB": ("RGB", "L", ("L", "A", "B")),
    "HSV": ("RGB", "L", ("H", "S", "V")),

    # Experimental modes include I;16, I;16L, I;16B, RGBa, BGR;15, and
    # BGR;24.  Use these modes only if you know exactly what you're
    # doing...

}

if sys.byteorder == 'little':
    _ENDIAN = '<'
else:
    _ENDIAN = '>'

_MODE_CONV = {
    # official modes
    "1": ('|b1', None),  # Bits need to be extended to bytes
    "L": ('|u1', None),
    "LA": ('|u1', 2),
    "I": (_ENDIAN + 'i4', None),
    "F": (_ENDIAN + 'f4', None),
    "P": ('|u1', None),
    "RGB": ('|u1', 3),
    "RGBX": ('|u1', 4),
    "RGBA": ('|u1', 4),
    "CMYK": ('|u1', 4),
    "YCbCr": ('|u1', 3),
    "LAB": ('|u1', 3),  # UNDONE - unsigned |u1i1i1
    "HSV": ('|u1', 3),
    # I;16 == I;16L, and I;32 == I;32L
    "I;16": ('<u2', None),
    "I;16B": ('>u2', None),
    "I;16L": ('<u2', None),
    "I;16S": ('<i2', None),
    "I;16BS": ('>i2', None),
    "I;16LS": ('<i2', None),
    "I;32": ('<u4', None),
    "I;32B": ('>u4', None),
    "I;32L": ('<u4', None),
    "I;32S": ('<i4', None),
    "I;32BS": ('>i4', None),
    "I;32LS": ('<i4', None),
}

def _conv_type_shape(im):
    typ, extra = _MODE_CONV[im.mode]
    if extra is None:
        return (im.size[1], im.size[0]), typ
    else:
        return (im.size[1], im.size[0], extra), typ

MODES = sorted(_MODEINFO)
# raw modes that may be memory mapped.  NOTE: if you change this, you
# may have to modify the stride calculation in map.c too!
_MAPMODES = ("L", "P", "RGBX", "RGBA", "CMYK", "I;16", "I;16L", "I;16B")

def getmodebase(mode):
    """
    Gets the "base" mode for given mode.  This function returns "L" for
    images that contain grayscale data, and "RGB" for images that
    contain color data.

    :param mode: Input mode.
    :returns: "L" or "RGB".
    :exception KeyError: If the input mode was not a standard mode.
    """
    return ImageMode().getmode(mode).basemode

def getmodetype(mode):
    """
    Gets the storage type mode.  Given a mode, this function returns a
    single-layer mode suitable for storing individual bands.

    :param mode: Input mode.
    :returns: "L", "I", or "F".
    :exception KeyError: If the input mode was not a standard mode.
    """
    return ImageMode().getmode(mode).basetype

def getmodebandnames(mode):
    """
    Gets a list of individual band names.  Given a mode, this function returns
    a tuple containing the names of individual bands (use
    :py:method:`~PIL.Image.getmodetype` to get the mode used to store each
    individual band.

    :param mode: Input mode.
    :returns: A tuple containing band names.  The length of the tuple
        gives the number of bands in an image of the given mode.
    :exception KeyError: If the input mode was not a standard mode.
    """
    return ImageMode().getmode(mode).bands

def getmodebands(mode):
    """
    Gets the number of individual bands for this mode.

    :param mode: Input mode.
    :returns: The number of bands in this mode.
    :exception KeyError: If the input mode was not a standard mode.
    """
    return len(ImageMode().getmode(mode).bands)

colormap = {
    # X11 colour table from https://drafts.csswg.org/css-color-4/, with
    # gray/grey spelling issues fixed.  This is a superset of HTML 4.0
    # colour names used in CSS 1.
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "darkgreen": "#006400",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "fuchsia": "#ff00ff",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "gray": "#808080",
    "grey": "#808080",
    "green": "#008000",
    "greenyellow": "#adff2f",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lavenderblush": "#fff0f5",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgreen": "#90ee90",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "olivedrab": "#6b8e23",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#ff0000",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32",
}

class Image(object):
    
    def __init__(self, image=None, filename=None, format=None):
        self._instance = image
        self.filename = filename
        self.format = format
        self._mode = None
        if image is not None or filename is not None:
            if self.filename is not None:
                ext = os.path.splitext(self.filename)[1]
                self.format = EXTENSION[ext]
            if self._instance is not None:
                self.size = (self._instance.shape[1], self._instance.shape[0])
                self.dtype = self._instance.dtype
                self._mode = self._get_mode(self._instance.shape, self.dtype)
        else:
            self._mode = None
            self.size = (0, 0)
            self.dtype = None
        self.mode = self._mode

    # @property
    # def size(self):
    #     return self._instance.shape[:2][::-1]

    # @property
    # def width(self):
    #     return self._instance.shape[1]

    # @property
    # def height(self):
    #     return self._instance.size[0]

    # @property
    # def mode(self):
    #     if self._mode:
    #         return self._mode
    #     else:
    #         raise ValueError('No mode specified.')

    # @property
    # def shape(self):
    #     return self._instance.shape

    # @property
    # def get_instance(self):
    #     return self._instance

    def _get_channels_and_depth(self, mode):
        mode = str(mode).upper()
        if mode == '1':
            return 1 , np.bool
        if mode == 'L':
            return 1, np.uint8
        if mode == 'LA':
            return 2, np.uint8
        if mode == 'P':
            return 1, np.uint8
        if mode == 'RGB':
            return 3, np.uint8
        if mode == 'RGBA':
            return 4, np.uint8
        if mode == 'CMYK':
            return 4, np.uint8
        if mode == 'YCBCR':
            return 3, np.uint8
        if mode == 'LAB':
            return 3, np.uint8
        if mode == 'HSV':
            return 3, np.uint8
        if mode == 'I':
            return 1, np.int32
        if mode == 'F':
            return 1, np.float32

        raise ValueError('Your mode name is incorrect.')

    def _get_converting_flag(self, mode, inst=None):
        "returns the cv2 flag for color conversion from inst to mode, uses the mode of the image object by default"
        mode = mode.upper()
        if inst is None:
            inst = self._mode.upper()
        converting_table = {
            'L':{
                'RGB':cv2.COLOR_GRAY2BGR,
                'RGBA':cv2.COLOR_GRAY2BGRA
            },
            'RGB':{
                '1':cv2.COLOR_BGR2GRAY,
                'L':cv2.COLOR_BGR2GRAY,
                'LAB':cv2.COLOR_BGR2LAB,
                'HSV':cv2.COLOR_BGR2HSV,
                'YCBCR':cv2.COLOR_BGR2YCR_CB,
                'RGBA':cv2.COLOR_BGR2BGRA
            },
            'RGBA':{
                '1':cv2.COLOR_BGRA2GRAY,
                'L':cv2.COLOR_BGRA2GRAY,
                'RGB':cv2.COLOR_BGRA2BGR
            },
            'LAB':{
                'RGB':cv2.COLOR_LAB2BGR
            },
            'HSV':{
                'RGB':cv2.COLOR_HSV2BGR
            },
            'YCBCR':{
                'RGB':cv2.COLOR_YCR_CB2BGR
            }
        }
        if converting_table.has_key(inst):
            if converting_table[inst].has_key(mode):
                return converting_table[inst][mode]
            else:
                raise ValueError('You can not convert image to this type')
        else:
            raise ValueError('This image type can not be converted')

    def _get_mode(self, shape, depth):
        if len(shape) == 2:
            channels = 1
        else:
            channels = shape[2]
        if channels == 1 and depth == np.bool:
            return '1'
        if channels == 1 and depth == np.uint8:
            return 'L'
        if channels == 1 and depth == np.uint8:
            return 'P'
        if channels == 2 and depth == np.uint8:
            return 'LA'
        if channels == 3 and depth == np.uint8:
            return 'RGB'
        if channels == 4 and depth == np.uint8:
            return 'RGBA'
        if channels == 4 and depth == np.uint8:
            return 'CMYK'
        if channels == 3 and depth == np.uint8:
            return 'YCBCR'
        if channels == 3 and depth == np.uint8:
            return 'LAB'
        if channels == 3 and depth == np.uint8:
            return 'HSV'
        if channels == 1 and depth == np.int32:
            return 'I'
        if channels == 1 and depth == np.float32        :
            return 'F'

    def _new(self, mode, size, color=None):
        self._mode = mode
        channels, depth = self._get_channels_and_depth(mode)
        self._instance = np.zeros(size + (channels,), depth)
        if color is not None:
            self._instance[:, 0:] = color
        return self._instance

    def alpha_composite(self, im, dest=(0, 0), source=(0, 0)):
        """ 'In-place' analog of Image.alpha_composite. Composites an image
        onto this image.

        :param im: image to composite over this one
        :param dest: Optional 2 tuple (left, top) specifying the upper
          left corner in this (destination) image.
        :param source: Optional 2 (left, top) tuple for the upper left
          corner in the overlay source image, or 4 tuple (left, top, right,
          bottom) for the bounds of the source rectangle

        Performance Note: Not currently implemented in-place in the core layer.
        """

        if not isinstance(source, (list, tuple)):
            raise ValueError("Source must be a tuple")
        if not isinstance(dest, (list, tuple)):
            raise ValueError("Destination must be a tuple")
        if not len(source) in (2, 4):
            raise ValueError("Source must be a 2 or 4-tuple")
        if not len(dest) == 2:
            raise ValueError("Destination must be a 2-tuple")
        if min(source) < 0:
            raise ValueError("Source must be non-negative")
        if min(dest) < 0:
            raise ValueError("Destination must be non-negative")

        channels, depth = self._get_channels_and_depth(im)
        _mode = self._get_mode(im.shape, im.dtype)
        _im = self._new(_mode, (im.shape[1], im.shape[0]))
        if len(source) == 2:
            source = source + _im.size

        # over image, crop if it's not the whole thing.
        if source == (0, 0) + _im.size:
            overlay = _im
        else:
            overlay = _im.crop(source)

        # target for the paste
        box = dest + (dest[0] + overlay.width, dest[1] + overlay.height)

        # destination image. don't copy if we're using the whole image.
        if box == (0, 0) + self.size:
            background = self._instance
        else:
            background = self.crop(box)

        result = alpha_composite(background, overlay)
        self.paste(result, box)

    def crop(self, box, image=None):
        "crops the image to the box which is a tuple = left, upper, right, lower"
        if image is None:
            part = self._instance[box[1]:box[3], box[0]:box[2]]
            return Image(part)
        else:
            image = image[box[1]:box[3], box[0]:box[2]]
            return image

    def copy(self):
        "returns a deep copy of the original"
        return Image(self._instance.copy(), format=self.format)

    def close(self):
        "closes all opened windows"
        cv2.destroyAllWindows()
        return None

    def draft(self, mode, size):
        """
        Configures the image file loader so it returns a version of the
        image that as closely as possible matches the given mode and
        size.  For example, you can use this method to convert a color
        JPEG to greyscale while loading it, or to extract a 128x192
        version from a PCD file.

        Note that this method modifies the :py:class:`~PIL.Image.Image` object
        in place.  If the image has already been loaded, this method has no
        effect.

        Note: This method is not implemented for most images. It is
        currently implemented only for JPEG and PCD images.

        :param mode: The requested mode.
        :param size: The requested size.
        """
        pass

    def frombytes(self, mode, size, data, decoder_name="raw", *args):
        """
        Loads this image with pixel data from a bytes object.

        This method is similar to the :py:func:`~PIL.Image.frombytes` function,
        but loads data into this image instead of creating a new image object.
        """

        # may pass tuple instead of argument list
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]

        # default format
        if decoder_name == "raw" and args == ():
            args = self.mode

        # unpack data
        channels, depth = self._get_channels_and_depth(mode)
        try:
            self._instance = np.fromstring(data, dtype=depth)
        except:
            raise ValueError("cannot decode image data")
        try:
            self._instance = self._instance.reshape((size[1], size[0], channels))
        except:
            raise ValueError("not enough image data")

    def fromstring(self, mode, size, data, decoder_name="raw", *args):
        # raise NotImplementedError("fromstring() has been removed. "
        #                           "Please call frombytes() instead.")
        self.frombytes(mode, size, data, decoder_name, *args)

    def convert(self, mode):
        "converts an image to the given mode"
        if self._mode.upper() == mode.upper():
            return Image(self._instance.copy())
        if not mode and self.mode == "P":
            # determine default mode
            if self.palette:
                mode = self.palette.mode
            else:
                mode = "RGB"
        if not mode or (mode == self.mode):
            return Image(self._instance.copy())
        return Image(self._convert(mode))
        
    def _convert(self, mode, obj=None):
        if obj is None:
            obj = self._instance
            flag = self._get_converting_flag(mode)
        else:
            orig_mode = self._get_mode(obj.shape, obj.dtype)
            flag = self._get_converting_flag(mode, inst=orig_mode)
        if mode == "1":
            im_gray = cv2.cvtColor(obj, cv2.COLOR_BGR2GRAY)
            thresh, converted = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        else:
            converted = cv2.cvtColor(obj, flag)
        return converted

    def paste(self, img_color, box=None, mask=None):
        "pastes either an image or a color to a region of interest defined in box with a mask"
        if isinstance(img_color, Image): # pasting an image
            _img_color = img_color._instance
            if box is None:
                box = (0, 0)
            else:
                if len(box) == 4:
                    if not(box[2]-box[0]==_img_color.shape[1] and box[3]-box[1]==_img_color.shape[0]):
                        raise ValueError("images do not match")
            # convert modes
            if img_color._instance.shape[2] != self._instance.shape[2] or img_color._instance.dtype != self._instance.dtype:
                dest_mode = self._mode
                _img_color = self._convert(dest_mode, obj=_img_color)
        else: # pasting a colorbox 
            if box is None:
                raise ValueError("cannot determine region size; use 4-item box")
            img_dim = (box[3]-box[1]+1, box[2]-box[0]+1)
            channels, depth = self._get_channels_and_depth(self._mode)
            colorbox = np.zeros((img_dim[0], img_dim[1], channels), dtype=depth)
            colorbox[:] = img_color
            _img_color = colorbox.copy()
        if mask is None:
            self._instance = self._paste(self._instance, _img_color, box[0], box[1])
        else:
            # enlarge the image _img_color without resizing to the new_canvas
            new_canvas = np.zeros(self._instance.shape, dtype=self._instance.dtype)
            new_canvas = self._paste(new_canvas, _img_color, box[0], box[1])
            if mask.shape[2] == 4: # RGBA
                r, g, b, _mask = self.split(mask)
            elif mask.shape[2] == 1:
                _mask = mask.copy()
            self._instance = self.composite(self._instance, new_canvas, _mask)

    def _paste(self, mother, child, x, y):
        "Pastes the numpy image child into the numpy image mother at position (x, y)"
        size = mother.shape
        csize = child.shape
        if y+csize[0]<0 or x+csize[1]<0 or y>size[0] or x>size[1]: return mother
        sel = [int(y), int(x), csize[0], csize[1]]
        csel = [0, 0, csize[0], csize[1]]
        if y<0:
            sel[0] = 0
            sel[2] = csel[2] + y
            csel[0] = -y
        elif y+sel[2]>=size[0]:
            sel[2] = int(size[0])
            csel[2] = size[0]-y
        else:
            sel[2] = sel[0] + sel[2]
        if x<0:
            sel[1] = 0
            sel[3] = csel[3] + x
            csel[1] = -x
        elif x+sel[3]>=size[1]:
            sel[3] = int(size[1])
            csel[3] = size[1]-x
        else:
            sel[3] = sel[1] + sel[3]
        childpart = child[csel[0]:csel[2], csel[1]:csel[3]]
        mother[sel[0]:sel[2], sel[1]:sel[3]] = childpart
        return mother

    def getband(self, channel):
        channels, depth = self._get_channels_and_depth(self._mode)
        if channels == 1:
            return self._instance.copy()
        else:
            chs = self.split()
            return chs[channel]

    def getbands(self):
        return tuple([i for i in self._mode])

    def getbbox(self):
        """
        Calculates the bounding box of the non-zero regions in the
        image.

        :returns: The bounding box is returned as a 4-tuple defining the
           left, upper, right, and lower pixel coordinate. See
           :ref:`coordinate-system`. If the image is completely empty, this
           method returns None.
        """
        img_ = (self._instance > 0)
        rows = np.any(img_, axis=1)
        cols = np.any(img_, axis=0)
        rmin, rmax = np.argmax(rows), img_.shape[0] - 1 - np.argmax(np.flipud(rows))
        cmin, cmax = np.argmax(cols), img_.shape[1] - 1 - np.argmax(np.flipud(cols))
        return (rmin, rmax, cmin, cmax)

    def _getcolors(self):
        channels, depth = self._get_channels_and_depth(self._mode)
        if channels == 1:
            img = self._instance.copy()
            y = img.shape[0]
            x = img.shape[1]
            flattened = img.reshape((x*y, 1))
            uni, counts = np.unique(flattened, return_counts=True)
        else:
            if channels == 4:
                r ,g, b, a = self.split()
                colorband = (r, g, b)
                img = merge("RGB", colorband, image=True)
            else: # channels == 3
                img = self._instance.copy()
            y = img.shape[0]
            x = img.shape[1]
            flattened = img.reshape((x*y, 3))
            uni, counts = np.unique(flattened, axis=0, return_counts=True)
        return uni, counts

    def getcolors(self, maxcolors=256):
        """
        Returns a list of colors used in this image.

        :param maxcolors: Maximum number of colors.  If this number is
           exceeded, this method returns None.  The default limit is
           256 colors.
        :returns: An unsorted list of (count, pixel) values.
        """

        if self._mode in ("1", "L", "P"):
            h = self._instance.histogram()
            out = []
            for i in range(256):
                if h[i]:
                    out.append((h[i], i))
            if len(out) > maxcolors:
                return None
            return out
        uni, counts = self._getcolors()
        if c>maxcolors: return None
        colors = []
        for l in range(len(counts)):
            colors.append((counts[l], l))
        return colors

    def getdata(self):
        flattened = self._instance.reshape((x*y, 3))
        return flattened

    def getextrema(self):
        return (np.minimum(self._instance), np.maximum(self._instance))

    def getim(self):
        return self._instance

    def getpalette(self):
        uni, counts = self._getcolors()
        colors = list(np.ravel(uni))
        return colors

    def getpixel(self, xytup):
        return self._instance[y, x]

    def histogram(self, mask=None, extrema=None):
        """
        Returns a histogram for the image. The histogram is returned as
        a list of pixel counts, one for each pixel value in the source
        image. If the image has more than one band, the histograms for
        all bands are concatenated (for example, the histogram for an
        "RGB" image contains 768 values).

        A bilevel image (mode "1") is treated as a greyscale ("L") image
        by this method.

        If a mask is provided, the method returns a histogram for those
        parts of the image where the mask image is non-zero. The mask
        image must have the same size as the image, and be either a
        bi-level image (mode "1") or a greyscale image ("L").

        :param mask: An optional mask.
        :returns: A list containing pixel counts.
        """
        uni, counts = self._getcolors()
        return [l for l in counts]

    def offset(self, xoffset, yoffset=None):
        raise NotImplementedError("offset() has been removed. "
                                  "Please call ImageChops.offset() instead.")

    def point(self, lut, mode=None):
        raise NotImplementedError("point() has been not implemented in this library. ")

    def putpixel(self, xytup, color):
        self._instance[xytup[1], xytup[0]] = color

    def putalpha(self, alpha):
        """
        Adds or replaces the alpha layer in this image.  If the image
        does not have an alpha layer, it's converted to "LA" or "RGBA".
        The new layer must be either "L" or "1".

        :param alpha: The new alpha layer.  This can either be an "L" or "1"
           image having the same size as this image, or an integer or
           other color value.
        """
        channels, depth = self._get_channels_and_depth(self._mode)

        if isinstance(alpha, np.ndarray): 
            paste_image = True
        else:
            paste_image = False

        if channels==4:
            r, g, b, a = self.split()
            if not paste_image:
                a[:] = alpha
            else:
                a = alpha.copy()
            colorband = (r, g, b, a)
            self._instance = merge("RGBA", colorband, image=True)
        elif channels == 3:
            if not paste_image:
                sh = self._instance.shape
                sh = (sh[0], sh[1], 1)
                a = np.zeros(sh, dtype=depth)
                a[:] = alpha
            else:
                a = alpha.copy()
            r, g, b = self.split()
            colorband = (r, g, b, a)
            self._instance = merge("RGBA", colorband, image=True)
        elif channels < 2: # "L" or "LA"
            if not paste_image:
                sh = self._instance.shape
                sh = (sh[0], sh[1], 1)
                a = np.zeros(sh, dtype=depth)
                a[:] = alpha
            else:
                a = alpha.copy()
            if channels == 2:
                l, a_old = self.split()
                colorband = (l, a)
            else:
                colorband = (self._instance, a)
            self._instance = merge("LA", colorband, image=True)

    def putdata(self, data, scale=1.0, offset=0.0):
        """
        Copies pixel data to this image.  This method copies data from a
        sequence object into the image, starting at the upper left
        corner (0, 0), and continuing until either the image or the
        sequence ends.  The scale and offset values are used to adjust
        the sequence values: **pixel = value*scale + offset**.

        :param data: A sequence object.
        :param scale: An optional scale value.  The default is 1.0.
        :param offset: An optional offset value.  The default is 0.0.
        """
        data = data * scale + offset
        channels, depth = self._get_channels_and_depth(self._mode)
        siz = self.size
        _im = np.ravel(self._instance)
        data = data[:len(_im)]
        _im = _im[:len(data)] = data
        self._instance = _im.reshape((siz[1], size[0], channels), dtype=depth)

    def putpalette(self, data, rawmode="RGB"):
        raise NotImplementedError("putpalette() has been not implemented in this library. ")

    def quantize(self, colors=256, method=None, kmeans=0, palette=None):
        raise NotImplementedError("quantize() has been not implemented in this library. ")

    def remap_palette(self, dest_map, source_palette=None):
        raise NotImplementedError("remap_palette() has been not implemented in this library. ")

    def resize(self, size, filtermethod = cv2.INTER_LINEAR, image=None):
        "resizes an image according to the given filter/interpolation method NEAREST, BILINEAR/INTER_LINEAR, BICUBIC, LANCZOS, INTERAREA"
        if image is None:
            _im = cv2.resize(self._instance, size, interpolation = filtermethod)
            return Image(_im)
        else:
            return cv2.resize(image, size, interpolation = filtermethod)

    def rotate_bound(self, angle, fillcolor=None):
        # grab the dimensions of the image and then determine the
        # center
        h, w = self._instance.shape[:2]

        (cX, cY) = (w // 2, h // 2)
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # perform the actual rotation and return the image
        return cv2.warpAffine(self._instance, M, (nW, nH), borderValue=fillcolor)

    def translated(self, image, x, y):
        # define the translation matrix and perform the translation
        M = np.float32([[1, 0, x], [0, 1, y]])
        shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
        # return the translated image
        return shifted

    def rotate(self, angle, resample=NEAREST, expand=0, center=None,
               translate=None, fillcolor=None):
        """
        Returns a rotated copy of this image.  This method returns a
        copy of this image, rotated the given number of degrees counter
        clockwise around its centre.

        :param angle: In degrees counter clockwise.
        :param resample: An optional resampling filter.  This can be
           one of :py:attr:`PIL.Image.NEAREST` (use nearest neighbour),
           :py:attr:`PIL.Image.BILINEAR` (linear interpolation in a 2x2
           environment), or :py:attr:`PIL.Image.BICUBIC`
           (cubic spline interpolation in a 4x4 environment).
           If omitted, or if the image has mode "1" or "P", it is
           set :py:attr:`PIL.Image.NEAREST`. See :ref:`concept-filters`.
        :param expand: Optional expansion flag.  If true, expands the output
           image to make it large enough to hold the entire rotated image.
           If false or omitted, make the output image the same size as the
           input image.  Note that the expand flag assumes rotation around
           the center and no translation.
        :param center: Optional center of rotation (a 2-tuple).  Origin is
           the upper left corner.  Default is the center of the image.
        :param translate: An optional post-rotate translation (a 2-tuple).
        :param fillcolor: An optional color for area outside the rotated image.
        :returns: An :py:class:`~PIL.Image.Image` object.
        """
        angle = angle % 360.0
        if fillcolor is None:
            fillcolor = (0, 0, 0)
        if expand == 0:
            # grab the dimensions of the image
            h, w = self.size[1], self.size[0]

            # if the center is None, initialize it as the center of
            # the image
            if center is None:
                center = (w // 2, h // 2)
            scale = 1.0
            # perform the rotation
            M = cv2.getRotationMatrix2D(center, angle, scale)
            _im = cv2.warpAffine(self._instance, M, (w, h), borderValue=fillcolor)
        else:
            _im = self.rotate_bound(angle)
        if translate is not None:
            _im = self.translated(_im, translate[0], translate[0])
        return Image(_im)

    def save(self, fp, format=None, **params):
        """
        Saves this image under the given filename.  If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        Keyword options can be used to provide additional instructions
        to the writer. If a writer doesn't recognise an option, it is
        silently ignored. The available options are described in the
        :doc:`image format documentation
        <../handbook/image-file-formats>` for each writer.

        You can use a file object instead of a filename. In this case,
        you must always specify the format. The file object must
        implement the ``seek``, ``tell``, and ``write``
        methods, and be opened in binary mode.

        :param fp: A filename (string), pathlib.Path object or file object.
        :param format: Optional format override.  If omitted, the
           format to use is determined from the filename extension.
           If a file object was used instead of a filename, this
           parameter should always be used.
        :param params: Extra parameters to the image writer.
        :returns: None
        :exception ValueError: If the output format could not be determined
           from the file name.  Use the format option to solve this.
        :exception IOError: If the file could not be written.  The file
           may have been created, and may contain partial data.
        """
        if py3: 
            basstring = str
        else:
            basstring = basestring
        if isinstance(fp, basstring):
            cv2.imwrite(fp, self._instance)
            return None
        if isinstance(fp, file):
            fl = open(format, 'w')
            fl.write(fp.read())
            fl.close()
            return None
        return None

    def seek(self, frame):
        """
        Seeks to the given frame in this sequence file. If you seek
        beyond the end of the sequence, the method raises an
        **EOFError** exception. When a sequence file is opened, the
        library automatically seeks to frame 0.

        Note that in the current version of the library, most sequence
        formats only allows you to seek to the next frame.

        See :py:meth:`~PIL.Image.Image.tell`.

        :param frame: Frame number, starting at 0.
        :exception EOFError: If the call attempts to seek beyond the end
            of the sequence.
        """

        # overridden by file handlers
        if frame != 0:
            raise EOFError

    def show(self, title=None, command=None):
        "shows the image in a window"
        if title is None:
            title = ""
        if command is None:
            cv2.imshow(title, self._instance)
            cv2.waitKey(0)
        else:
            flag, fname = tempfile.mkstemp()
            cv2.imwrite(fname, self._instance)
            os.system(command+" "+fname)

    def split(self, image=None):
        "splits the image into its color bands"
        if image is None:
            if self._instance.shape[2] == 1:
                return self._instance.copy()
            elif self._instance.shape[2] == 2:
                l, a = cv2.split(self._instance)
                return l, a
            elif self._instance.shape[2] == 3:
                b, g, r = cv2.split(self._instance)
                return b, g, r
            else:
                b, g, r, a = cv2.split(self._instance)
                return b, g, r, a
        else:
            if image.shape[2] == 1:
                return image.copy()
            elif image.shape[2] == 2:
                l, a = cv2.split(image)
                return l, a
            elif image.shape[2] == 3:
                b, g, r = cv2.split(image)
                return b, g, r
            else:
                b, g, r, a = cv2.split(image)
                return b, g, r, a

    def getchannel(self, channel):
        """
        Returns an image containing a single channel of the source image.

        :param channel: What channel to return. Could be index
          (0 for "R" channel of "RGB") or channel name
          ("A" for alpha channel of "RGBA").
        :returns: An image in "L" mode.

        .. versionadded:: 4.3.0
        """
        if isStringType(channel):
            try:
                channel = self.getbands().index(channel)
            except ValueError:
                raise ValueError(
                    'The image has no channel "{}"'.format(channel))
        return self.getband(channel)

    def tell(self):
        """
        Returns the current frame number. See :py:meth:`~PIL.Image.Image.seek`.

        :returns: Frame number, starting with 0.
        """
        return 0

    def thumbnail(self, size, resample=BICUBIC):
        """
        Make this image into a thumbnail.  This method modifies the
        image to contain a thumbnail version of itself, no larger than
        the given size.  This method calculates an appropriate thumbnail
        size to preserve the aspect of the image, calls the
        :py:meth:`~PIL.Image.Image.draft` method to configure the file reader
        (where applicable), and finally resizes the image.

        Note that this function modifies the :py:class:`~PIL.Image.Image`
        object in place.  If you need to use the full resolution image as well,
        apply this method to a :py:meth:`~PIL.Image.Image.copy` of the original
        image.

        :param size: Requested size.
        :param resample: Optional resampling filter.  This can be one
           of :py:attr:`PIL.Image.NEAREST`, :py:attr:`PIL.Image.BILINEAR`,
           :py:attr:`PIL.Image.BICUBIC`, or :py:attr:`PIL.Image.LANCZOS`.
           If omitted, it defaults to :py:attr:`PIL.Image.BICUBIC`.
           (was :py:attr:`PIL.Image.NEAREST` prior to version 2.5.0)
        :returns: None
        """
        # preserve aspect ratio
        x, y = self.size
        if x > size[0]:
            y = int(max(y * size[0] / x, 1))
            x = int(size[0])
        if y > size[1]:
            x = int(max(x * size[1] / y, 1))
            y = int(size[1])
        size = x, y
        if size == self.size:
            return
        self.draft(None, size)
        self._instance = self.resize(size, resample, image=self._instance)
        self.readonly = 0
        self.pyaccess = None

    def transform(self, size, method, data=None, resample=NEAREST,
                  fill=1, fillcolor=None):
        """
        Transforms this image.  This method creates a new image with the
        given size, and the same mode as the original, and copies data
        to the new image using the given transform.

        :param size: The output size.
        :param method: The transformation method.  This is one of
          :py:attr:`PIL.Image.EXTENT` (cut out a rectangular subregion),
          :py:attr:`PIL.Image.AFFINE` (affine transform),
          :py:attr:`PIL.Image.PERSPECTIVE` (perspective transform),
          :py:attr:`PIL.Image.QUAD` (map a quadrilateral to a rectangle), or
          :py:attr:`PIL.Image.MESH` (map a number of source quadrilaterals
          in one operation).

          It may also be an :py:class:`~PIL.Image.ImageTransformHandler`
          object::
            class Example(Image.ImageTransformHandler):
                def transform(size, method, data, resample, fill=1):
                    # Return result

          It may also be an object with a :py:meth:`~method.getdata` method
          that returns a tuple supplying new **method** and **data** values::
            class Example(object):
                def getdata(self):
                    method = Image.EXTENT
                    data = (0, 0, 100, 100)
                    return method, data
        :param data: Extra data to the transformation method.
        :param resample: Optional resampling filter.  It can be one of
           :py:attr:`PIL.Image.NEAREST` (use nearest neighbour),
           :py:attr:`PIL.Image.BILINEAR` (linear interpolation in a 2x2
           environment), or :py:attr:`PIL.Image.BICUBIC` (cubic spline
           interpolation in a 4x4 environment). If omitted, or if the image
           has mode "1" or "P", it is set to :py:attr:`PIL.Image.NEAREST`.
        :param fill: If **method** is an
          :py:class:`~PIL.Image.ImageTransformHandler` object, this is one of
          the arguments passed to it. Otherwise, it is unused.
        :param fillcolor: Optional fill color for the area outside the
           transform in the output image.
        :returns: An :py:class:`~PIL.Image.Image` object.
        """
        if method == EXTENT:
            x0, y0, x1, y1 = data
            part = self._instance[y0:y1, x0:x1]
            _im = cv2.resize(part, size)
        elif method == AFFINE:
            x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = data
            pts1 = np.float32([[x0, y0], [x1, y1], [x2, y2]])
            pts2 = np.float32([[x3, y3], [x4, y4], [x5, y5]])
            M = cv2.getAffineTransform(pts1,pts2)
            _im = cv2.warpAffine(self._instance, M, size)
        elif method == PERSPECTIVE or method == QUAD:
            x0, y0, x1, y1, x2, y2, x3, y3 = data
            pts1 = np.float32([[x0, y0], [x1, y1], [x2, y2], [x3, y3]])
            pts2 = np.float32([[0,0],[size[0], 0], [0, size[1]], [size[0], size[1]]])
            M = cv2.getPerspectiveTransform(pts1, pts2)
            _im = cv2.warpPerspective(self._instance, M, size)
        elif method == MESH:
            _im = self._instance.copy()
            for elem in data:
                box, quad = elem
                x0, y0, x1, y1, x2, y2, x3, y3 = quad
                pts1 = np.float32([[x0, y0], [x1, y1], [x2, y2], [x3, y3]])
                pts2 = np.float32([[box[0], box[1]],[box[2], box[1]], [box[0], box[3]], [box[2], box[3]]])
                M = cv2.getPerspectiveTransform(pts1, pts2)
                _im = cv2.warpPerspective(_im, M, size)
        return Image(_im)

    def transpose(self, method):
        """
        Transpose image (flip or rotate in 90 degree steps)

        :param method: One of :py:attr:`PIL.Image.FLIP_LEFT_RIGHT`,
          :py:attr:`PIL.Image.FLIP_TOP_BOTTOM`, :py:attr:`PIL.Image.ROTATE_90`,
          :py:attr:`PIL.Image.ROTATE_180`, :py:attr:`PIL.Image.ROTATE_270`,
        :returns: Returns a flipped or rotated copy of this image.
        """
        w, h = self.size
        if method == FLIP_LEFT_RIGHT:
            _im = cv2.flip(self._instance, 1)
        elif method == FLIP_TOP_BOTTOM:
            _im = cv2.flip(self._instance, 0)
        elif method == ROTATE_90:
            _im = self.rotate_bound(270)
            x = self.size[0]//2-self.size[1]//2
            box = (0, x, self.size[0], x+self.size[1])
            _im = self.crop(box, _im)
        elif method == ROTATE_180:
            _im = self.rotate(180, self._instance)
        elif method == ROTATE_270:
            _im = self.rotate_bound(90)
            x = self.size[0]//2-self.size[1]//2
            box = (0, x, self.size[0], x+self.size[1])
            _im = self.crop(box, _im)
        if isinstance(_im, Image):
            return _im
        elif isinstance(_im, np.ndarray):
            return Image(_im)

    def verify(self):
        """
        Verifies the contents of a file. For data read from a file, this
        method attempts to determine if the file is broken, without
        actually decoding the image data.  If this method finds any
        problems, it raises suitable exceptions.  If you need to load
        the image after using this method, you must reopen the image
        file.
        """
        pass

class ImageDraw(object):
    _img_instance = None

    def __init__(self, img):
        self._img_instance = img

    def point(self, xy, fill, width=3):
        for elem in xy:
            cv2.line(self._img_instance,elem, elem, fill,width)

    def line(self, xy, color, width):
        cv2.line(self._img_instance,xy[0], xy[1], color, width)

    def rectangle(self, xy, fill=None, outline=None):
        if fill:
            cv2.rectangle(self._img_instance,xy[0], xy[1], fill, thickness=cv2.cv.CV_FILLED)
        if outline:
            cv2.rectangle(self._img_instance,xy[0], xy[1], outline, 3)

class ImageColor(object):

    def getcolor(self, color, mode):
        """
        Same as :py:func:`~PIL.ImageColor.getrgb`, but converts the RGB value to a
        greyscale value if the mode is not color or a palette image. If the string
        cannot be parsed, this function raises a :py:exc:`ValueError` exception.

        .. versionadded:: 1.1.4

        :param color: A color string
        :return: ``(graylevel [, alpha]) or (red, green, blue[, alpha])``
        """
        # same as getrgb, but converts the result to the given mode
        color, alpha = self.getrgb(color), 255
        if len(color) == 4:
            color, alpha = color[0:3], color[3]

        if getmodebase(mode) == "L":
            r, g, b = color
            color = (r*299 + g*587 + b*114)//1000
            if mode[-1] == 'A':
                return (color, alpha)
        else:
            if mode[-1] == 'A':
                return color + (alpha,)
        return color

    def getrgb(self, color):
        """
         Convert a color string to an RGB tuple. If the string cannot be parsed,
         this function raises a :py:exc:`ValueError` exception.

        .. versionadded:: 1.1.4

        :param color: A color string
        :return: ``(red, green, blue[, alpha])``
        """
        color = color.lower()

        rgb = colormap.get(color, None)
        if rgb:
            if isinstance(rgb, tuple):
                return rgb
            colormap[color] = rgb = self.getrgb(rgb)
            return rgb

        # check for known string formats
        if re.match('#[a-f0-9]{3}$', color):
            return (
                int(color[1]*2, 16),
                int(color[2]*2, 16),
                int(color[3]*2, 16),
                )

        if re.match('#[a-f0-9]{4}$', color):
            return (
                int(color[1]*2, 16),
                int(color[2]*2, 16),
                int(color[3]*2, 16),
                int(color[4]*2, 16),
                )

        if re.match('#[a-f0-9]{6}$', color):
            return (
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16),
                )

        if re.match('#[a-f0-9]{8}$', color):
            return (
                int(color[1:3], 16),
                int(color[3:5], 16),
                int(color[5:7], 16),
                int(color[7:9], 16),
                )

        m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", color)
        if m:
            return (
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3))
                )

        m = re.match(r"rgb\(\s*(\d+)%\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$", color)
        if m:
            return (
                int((int(m.group(1)) * 255) / 100.0 + 0.5),
                int((int(m.group(2)) * 255) / 100.0 + 0.5),
                int((int(m.group(3)) * 255) / 100.0 + 0.5)
                )

        m = re.match(
            r"hsl\(\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)%\s*,\s*(\d+\.?\d*)%\s*\)$",
            color,
        )
        if m:
            from colorsys import hls_to_rgb
            rgb = hls_to_rgb(
                float(m.group(1)) / 360.0,
                float(m.group(3)) / 100.0,
                float(m.group(2)) / 100.0,
                )
            return (
                int(rgb[0] * 255 + 0.5),
                int(rgb[1] * 255 + 0.5),
                int(rgb[2] * 255 + 0.5)
                )

        m = re.match(
            r"hs[bv]\(\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)%\s*,\s*(\d+\.?\d*)%\s*\)$",
            color,
        )
        if m:
            from colorsys import hsv_to_rgb
            rgb = hsv_to_rgb(
                float(m.group(1)) / 360.0,
                float(m.group(2)) / 100.0,
                float(m.group(3)) / 100.0,
                )
            return (
                int(rgb[0] * 255 + 0.5),
                int(rgb[1] * 255 + 0.5),
                int(rgb[2] * 255 + 0.5)
                )

        m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$",
                     color)
        if m:
            return (
                int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)),
                int(m.group(4))
                )
        raise ValueError("unknown color specifier: %r" % color)

class ModeDescriptor(object):
    """Wrapper for mode strings."""

    def __init__(self, mode, bands, basemode, basetype):
        self.mode = mode
        self.bands = bands
        self.basemode = basemode
        self.basetype = basetype

    def __str__(self):
        return self.mode

class ImageMode(object):
    def getmode(self, mode):
        """Gets a mode descriptor for the given mode."""
        modes = {}
        # core modes
        for m, (basemode, basetype, bands) in _MODEINFO.items():
            modes[m] = ModeDescriptor(m, bands, basemode, basetype)
        # extra experimental modes
        modes["RGBa"] = ModeDescriptor("RGBa",
                                       ("R", "G", "B", "a"), "RGB", "L")
        modes["LA"] = ModeDescriptor("LA", ("L", "A"), "L", "L")
        modes["La"] = ModeDescriptor("La", ("L", "a"), "L", "L")
        modes["PA"] = ModeDescriptor("PA", ("P", "A"), "RGB", "L")
        # mapping modes
        modes["I;16"] = ModeDescriptor("I;16", "I", "L", "L")
        modes["I;16L"] = ModeDescriptor("I;16L", "I", "L", "L")
        modes["I;16B"] = ModeDescriptor("I;16B", "I", "L", "L")
        # set global mode cache atomically
        _modes = modes
        return _modes[mode]    

class ImageFilter(object):
    pass



def _check_size(size):
    """
    Common check to enforce type and sanity check on size tuples

    :param size: Should be a 2 tuple of (width, height)
    :returns: True, or raises a ValueError
    """

    if not isinstance(size, (list, tuple)):
        raise ValueError("Size must be a tuple")
    if len(size) != 2:
        raise ValueError("Size must be a tuple of length 2")
    if size[0] < 0 or size[1] < 0:
        raise ValueError("Width and height must be >= 0")

    return True

def new(mode, size, color=0):
    """
    Creates a new image with the given mode and size.

    :param mode: The mode to use for the new image. See:
       :ref:`concept-modes`.
    :param size: A 2-tuple, containing (width, height) in pixels.
    :param color: What color to use for the image.  Default is black.
       If given, this should be a single integer or floating point value
       for single-band modes, and a tuple for multi-band modes (one value
       per band).  When creating RGB images, you can also use color
       strings as supported by the ImageColor module.  If the color is
       None, the image is not initialised.
    :returns: An :py:class:`~PIL.Image.Image` object.
    """

    _check_size(size)

    if color is None:
        # don't initialize
        _im = Image()._new(mode, size)
        return Image(_im)

    if type(color).__name__ == "str":
        # css3-style specifier
        color = ImageColor().getcolor(color, mode)

    _im = Image()._new(mode, size, color)
    return Image(_im)

def frombytes(mode, size, data, decoder_name="raw", *args):
    """
    Creates a copy of an image memory from pixel data in a buffer.

    In its simplest form, this function takes three arguments
    (mode, size, and unpacked pixel data).

    You can also use any pixel decoder supported by PIL.  For more
    information on available decoders, see the section
    :ref:`Writing Your Own File Decoder <file-decoders>`.

    Note that this function decodes pixel data only, not entire images.
    If you have an entire image in a string, wrap it in a
    :py:class:`~io.BytesIO` object, and use :py:func:`~PIL.Image.open` to load
    it.

    :param mode: The image mode. See: :ref:`concept-modes`.
    :param size: The image size.
    :param data: A byte buffer containing raw data for the given mode.
    :param decoder_name: What decoder to use.
    :param args: Additional parameters for the given decoder.
    :returns: An :py:class:`~PIL.Image.Image` object.
    """

    _check_size(size)

    # may pass tuple instead of argument list
    if len(args) == 1 and isinstance(args[0], tuple):
        args = args[0]

    if decoder_name == "raw" and args == ():
        args = mode

    im = new(mode, size)
    im.frombytes(data, decoder_name, args)
    return im

def fromstring(mode, size, data, decoder_name="raw", *args):
    # raise NotImplementedError("fromstring() has been removed. " +
    #                          "Please call frombytes() instead.")
    return frombytes(mode, size, data, decoder_name, *args)

def frombuffer(mode, size, data, decoder_name="raw", *args):
    """
    Creates an image memory referencing pixel data in a byte buffer.

    This function is similar to :py:func:`~PIL.Image.frombytes`, but uses data
    in the byte buffer, where possible.  This means that changes to the
    original buffer object are reflected in this image).  Not all modes can
    share memory; supported modes include "L", "RGBX", "RGBA", and "CMYK".

    Note that this function decodes pixel data only, not entire images.
    If you have an entire image file in a string, wrap it in a
    **BytesIO** object, and use :py:func:`~PIL.Image.open` to load it.

    In the current version, the default parameters used for the "raw" decoder
    differs from that used for :py:func:`~PIL.Image.frombytes`.  This is a
    bug, and will probably be fixed in a future release.  The current release
    issues a warning if you do this; to disable the warning, you should provide
    the full set of parameters.  See below for details.

    :param mode: The image mode. See: :ref:`concept-modes`.
    :param size: The image size.
    :param data: A bytes or other buffer object containing raw
        data for the given mode.
    :param decoder_name: What decoder to use.
    :param args: Additional parameters for the given decoder.  For the
        default encoder ("raw"), it's recommended that you provide the
        full set of parameters::

            frombuffer(mode, size, data, "raw", mode, 0, 1)

    :returns: An :py:class:`~PIL.Image.Image` object.

    .. versionadded:: 1.1.4
    """

    _check_size(size)

    # may pass tuple instead of argument list
    if len(args) == 1 and isinstance(args[0], tuple):
        args = args[0]

    if decoder_name == "raw":
        if args == ():
            args = mode, 0, -1  # may change to (mode, 0, 1) post-1.1.6
        if args[0] in _MAPMODES:
            channels, depth = Image()._get_channels_and_depth(mode)
            im = np.frombuffer(data)
            im = im.reshape((size[1], size[0], channels))
            im = im.astype(depth)
            im_ = new(mode, (1, 1))
            im_._instance = im
            im_.readonly = 1
            return im_

    return frombytes(mode, size, data, decoder_name, args)

def fromarray(obj, mode=None):
    """
    Creates an image memory from an object exporting the array interface
    (using the buffer protocol).

    If **obj** is not contiguous, then the tobytes method is called
    and :py:func:`~PIL.Image.frombuffer` is used.

    If you have an image in NumPy::

      from PIL import Image
      import numpy as np
      im = Image.open('hopper.jpg')
      a = np.asarray(im)

    Then this can be used to convert it to a Pillow image::

      im = Image.fromarray(a)

    :param obj: Object with array interface
    :param mode: Mode to use (will be determined from type if None)
      See: :ref:`concept-modes`.
    :returns: An image object.

    .. versionadded:: 1.1.6
    """
    if isinstance(obj, np.ndarray): 
        return obj.copy()
    else: 
        raise TypeError("Cannot handle this data type")

_fromarray_typemap = {
    # (shape, typestr) => mode, rawmode
    # first two members of shape are set to one
    ((1, 1), "|b1"): ("1", "1;8"),
    ((1, 1), "|u1"): ("L", "L"),
    ((1, 1), "|i1"): ("I", "I;8"),
    ((1, 1), "<u2"): ("I", "I;16"),
    ((1, 1), ">u2"): ("I", "I;16B"),
    ((1, 1), "<i2"): ("I", "I;16S"),
    ((1, 1), ">i2"): ("I", "I;16BS"),
    ((1, 1), "<u4"): ("I", "I;32"),
    ((1, 1), ">u4"): ("I", "I;32B"),
    ((1, 1), "<i4"): ("I", "I;32S"),
    ((1, 1), ">i4"): ("I", "I;32BS"),
    ((1, 1), "<f4"): ("F", "F;32F"),
    ((1, 1), ">f4"): ("F", "F;32BF"),
    ((1, 1), "<f8"): ("F", "F;64F"),
    ((1, 1), ">f8"): ("F", "F;64BF"),
    ((1, 1, 2), "|u1"): ("LA", "LA"),
    ((1, 1, 3), "|u1"): ("RGB", "RGB"),
    ((1, 1, 4), "|u1"): ("RGBA", "RGBA"),
    }

# shortcuts
_fromarray_typemap[((1, 1), _ENDIAN + "i4")] = ("I", "I")
_fromarray_typemap[((1, 1), _ENDIAN + "f4")] = ("F", "F")

def open(fl, mode='r'):
    _mode = None
    _format = None
    if py3: 
        basstring = str
    else:
        basstring = basestring
    if isinstance(fl, basstring):
        _instance = cv2.imread(fl,cv2.IMREAD_UNCHANGED)
        # _mode = Image()._get_mode(_instance.shape, _instance.dtype)
        img = Image(_instance, fl)
        return img
    if isinstance(fl, file):
        file_bytes = np.asarray(bytearray(fl.read()), dtype=np.uint8)
        _instance = cv2.imdecode(file_bytes, cv2.CV_LOAD_IMAGE_UNCHANGED)
        # _mode = Image()._get_mode(_instance.shape, _instance.dtype)
        img = Image(_instance, fl.name)
        return img
    if hasattr(fl, 'mode'):
        image = np.array(fl)
        _mode = fl.mode
        if _mode == 'RGB':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        _instance = image
        img = Image(_instance)
        return img

def blend(img1, img2, alpha):
    "blends 2 images using an alpha value>=0.0 and <=1.0"
    dst = cv2.addWeighted(img1, 1.0-alpha, img2, alpha, 0)
    return Image(dst)

def composite(background, foreground, mask):
    "pastes the foreground image into the background image using the mask"
    # Convert uint8 to float
    foreground = foreground.astype(float)
    background = background.astype(float)
    # Normalize the alpha mask to keep intensity between 0 and 1
    alphamask = alphamask.astype(float)/255
    # Multiply the foreground with the alpha mask
    foreground = cv2.multiply(alphamask, foreground)
    # Multiply the background with ( 1 - alpha )
    background = cv2.multiply(1.0 - alphamask, background)
    # Add the masked foreground and background
    outImage = cv2.add(foreground, background)
    outImage = outImage/255
    return Image(outImag)

def alpha_composite(im1, im2):
    """
    Alpha composite im2 over im1.

    :param im1: The first image. Must have mode RGBA.
    :param im2: The second image.  Must have mode RGBA, and the same size as
       the first image.
    :returns: An :py:class:`~PIL.Image.Image` object.
    """
    r1, g1, b1, a1 = Image().split(im1)
    r2, g2, b2, a2 = Image().split(im2)
    alphacomp = np.zeros(im1.shape, dtype=im1.dtype)
    im3 = composite(alphacomp, im1, a1)
    alphacomp = np.zeros(im2.shape, dtype=im2.dtype)
    im4 = composite(alphacomp, im2, a2)
    return blend(im3, im4, 0.5)

def merge(mode, colorbandtuple, image=False):
    "merges three channels to one band"
    if len(colorbandtuple) == 2:
        red, green = colorbandtuple
        blue = None
        alpha = None
    elif len(colorbandtuple) == 3:
        red, green, blue = colorbandtuple
        alpha = None
    elif len(colorbandtuple) == 4:
        red, green, blue, alpha = colorbandtuple
    channels, depth = Image()._get_channels_and_depth(mode)
    img_dim = red.shape
    img = np.zeros((img_dim[0], img_dim[1], channels), dtype=depth)
    img[:,:,0] = red
    img[:,:,1] = green
    if blue is not None:
        img[:,:,2] = blue
    if alpha is not None:
        img[:,:,3] = alpha
    if image:
        return img
    else:
        return Image(img)

def linear_gradient(mode, size=256):
    "Generate 256x256 linear gradient from black to white, top to bottom."
    channels, depth = Image()._get_channels_and_depth(mode)
    if channels == 1:
        y = np.linspace(0, size-1, size)
        gradient = np.tile(y, (size, 1)).T
        gradient = gradient.astype(depth)
        return gradient
    elif channels > 3:
        y = np.linspace(0, size-1, size)
        gradient = np.tile(y, (channels, size, 1)).T
        gradient = gradient.astype(depth)
        return gradient

def radial_gradient(mode, size=256):
    "Generate 256x256 radial gradient from black to white, centre to edge."
    channels, depth = Image()._get_channels_and_depth(mode)
    gradient = np.zeros((size, size, channels), dtype=depth)
    imgsize = gradient.shape[:2]
    innerColor = (0, 0, 0)
    outerColor = (255, 255, 255)
    if channels == 1:
        x_axis = np.linspace(-1, 1, 256)[:, None]
        y_axis = np.linspace(-1, 1, 256)[None, :]
        gradient = np.sqrt(x_axis ** 2 + y_axis ** 2)
        return gradient
    elif channels ==3:
        inner = np.array([0, 0, 0])[None, None, :]
        outer = np.array([1, 1, 1])[None, None, :]
        gradient /= gradient.max()
        gradient = gradient[:, :, None]
        gradient = gradient * outer + (1 - gradient) * inner
        return gradient
    else:
        for y in range(imgsize[1]):
            for x in range(imgsize[0]):
                #Find the distance to the center
                distanceToCenter = np.sqrt((x - imgsize[0]//2) ** 2 + (y - imgsize[1]//2) ** 2)
                #Make it on a scale from 0 to 1innerColor
                distanceToCenter = distanceToCenter / (np.sqrt(2) * imgsize[0]/2)
                #Calculate r, g, and b values
                r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
                g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
                b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)
                a = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)
                #Place the pixel
                gradient[y, x] = (int(r), int(g), int(b), int(a))
        return gradient


if __name__ == '__main__':

    # var init
    testfile = "lena.jpg"
    outfile1 = "lena1.bmp"
    outfile2 = "lena2.bmp"
    thsize = (128, 128)
    box = (100, 100, 400, 400)

    # the old style:
    # from PIL import Image as PILImage
    # pil_image = PILImage.open(testfile)
    # print(pil_image.format, pil_image.size, pil_image.mode)
    # pil_image.save(outfile1)
    # pil_image.show()
    # small_pil = pil_image.copy()
    # small_pil.thumbnail(thsize)
    # small_pil.show()
    # region_pil = pil_image.crop(box)    
    # region_pil = region_pil.transpose(PILImage.ROTATE_180)
    # pil_image.paste(region_pil, box)
    # pil_image.show()
    
    # the new style:

    # if you import the library from site-packages import like this:
    # import PILasOPENCV as Image
    # im = Image.new("RGB", (512, 512), "white")

    im = new("RGB", (512, 512), "white")
    im.show()
    print (type(im))
    print(im.format, im.size, im.mode)
    # None (512, 512) RGB
    # <class 'Image'>

    # im = Image.open(testfile)
    im = open(testfile)
    print(im.format, im.size, im.mode)
    # JPEG (512, 512) RGB
    im.save(outfile2)
    im.show()
    small = im.copy()
    small.thumbnail(thsize)
    small.show()

    region = im.crop(box)
    print("region",region.format, region.size, region.mode)
    # region = region.transpose(Image.ROTATE_180)
    region = region.transpose(ROTATE_180)
    region.show()
    im.paste(region, box)
    im.show()
    # with open(testfile, 'rb') as img:
    #     #a.save(img, 'text.jpg')
    #     b = a.open(img)

    # a.open(pil_image)
    # d = ImageDraw(a.get_instance)
    # b = a.copy()
    # d.rectangle([(10,10),(100,200)], fill=(255,255,0))
    # a.save('output.jpg')
    # a.show()