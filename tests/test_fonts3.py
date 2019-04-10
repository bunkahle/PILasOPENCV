from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
import cv2

# font = ImageFont.truetype("arial.ttf", 30)
size = 20
font = ImageFont.truetype("msgothic.ttc", 22+int(size/50), index=0, encoding="unic")
print(font)
im = Image.new("RGB", (512, 512), "grey")
draw = ImageDraw.Draw(im)
text = "Some text in arial"
draw.text((100, 250), text, font=font, fill=(0, 0, 0))
im = im.resize((256,256), Image.ANTIALIAS)
print(ImageFont.getsize(text, font))
mask = ImageFont.getmask(text, font)
print(type(mask))
cv2.imshow("mask", mask)
im.show()
im_numpy = im.getim()
print(type(im_numpy), im_numpy.shape, im_numpy.dtype)