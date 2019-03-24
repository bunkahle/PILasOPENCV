from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
import cv2

font = ImageFont.truetype("arial.ttf", 18)
print(font)
im = Image.open("lena.jpg")
draw = ImageDraw.Draw(im)
text = "Lena's image"
draw.text((249,455), text, font=font, fill=(0, 0, 0))
# in PIL:
# print(font.getsize(text))
# mask = font.getmask(text)
print(ImageFont.getsize(text, font))
mask = ImageFont.getmask(text, font)
print(type(mask))
cv2.imshow("mask", mask)
im.show()