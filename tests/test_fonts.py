from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
# from PIL import Image, ImageDraw, ImageFont
try:
	font = ImageFont.truetype('ARIAL.TTF'.lower(), 18)
except:
	font = ImageFont.truetype('ARIAL.TTF', 18)
im = Image.open("lena.jpg")
im.show("test")
draw = ImageDraw.Draw(im)
text_to_show = "The quick brown fox jumps over the lazy dog"
# print(font.getsize(text_to_show))
# mask = font.getmask(text_to_show)
draw.text((100,456), text_to_show, font=font, fill=(255, 0, 0))
im.show("test")



