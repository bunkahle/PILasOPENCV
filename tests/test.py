from __future__ import print_function
import PILasOPENCV as Image
# from PIL import Image

im = Image.new("RGB", (512, 512), "red")
im.show()

testfile = "lena.jpg"
im = Image.open(testfile)
print (type(im))
# JPEG (512, 512) RGB
im.save("lena.bmp")
im.show()
small = im.copy()
thsize = (128, 128)
small.thumbnail(thsize)
small.show()
box = (100, 100, 400, 400)
region = im.crop(box)
print("region",region.format, region.size, region.mode)
# region = region.transpose(Image.ROTATE_180)
region = region.transpose(Image.ROTATE_180)
region.show()
im.paste(region, box)
im.show()