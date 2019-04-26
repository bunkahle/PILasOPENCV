import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
# from PIL import Image
# from PIL import ImageDraw

im = Image.open("lena.jpg")
im.show()
im2 = Image.open("Images/mask3.jpg")
draw = ImageDraw.Draw(im)
draw.bitmap((10,10), im2, fill="red")
im.show()
