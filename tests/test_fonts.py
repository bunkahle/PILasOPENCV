from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
import cv2
# from PIL import Image, ImageDraw, ImageFont
fontname = 'ARIAL.TTF'
try:
	font = ImageFont.truetype(fontname.lower(), 18)
except:
	font = ImageFont.truetype(fontname, 18)
fontname2 = "waltographUI.TTF"
try:
	font2 = ImageFont.truetype(fontname2.lower(), 25)
except:
	font2 = ImageFont.truetype(fontname2, 25)
im = Image.open("lena.jpg")
im.show("test")
draw = ImageDraw.Draw(im)
text = "Lena's image\nin two lines"
scaling = 1
draw.text((150, 50), text, font=cv2.FONT_HERSHEY_TRIPLEX, fill=(255, 255, 255), scale=scaling)
draw.text((350, 300), text[:text.find("'")], font=cv2.FONT_HERSHEY_DUPLEX, fill=(0, 255, 0), scale=2)
print("cv2.FONT_HERSHEY_TRIPLEX:"+text, draw.textsize(text, font=cv2.FONT_HERSHEY_TRIPLEX, scale=scaling))
text_to_show = "The quick brown fox jumps\nover the lazy dog"
# in PIL:
# print(font.getsize(text_to_show))
# mask = font.getmask(text_to_show)
# print(type(mask), dir(mask))

# new to get textsize:
print("'ARIAL.TTF': "+text_to_show, ImageFont.getsize(text_to_show, font)) # (356, 21, 4)
mask = ImageFont.getmask(text_to_show[:text_to_show.find("\n")], font)
# new to get textmask
print(type(mask))
cv2.imshow("mask", mask)

draw.text((249,455), text_to_show, font=font, fill=(0, 0, 0))
draw.text((250,456), text_to_show, font=font, fill=(255, 0, 0))
draw.text((50,106), text_to_show[:text_to_show.find("\n")], font=font2, fill=(0, 128, 255))
print("'ARIAL.TTF': "+text_to_show, draw.textsize(text_to_show, font))
im.show("test")



