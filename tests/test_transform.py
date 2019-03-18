import PILasOPENCV as Image
# from PIL import Image

im = Image.open("lena.jpg")
im.show()

out = im.resize((128, 128))
out.show()

out = im.rotate(45) # degrees counter-clockwise
out.show()

im.show()

out = im.transpose(Image.FLIP_LEFT_RIGHT)
out.show()
out = im.transpose(Image.FLIP_TOP_BOTTOM)
out.show()
out = im.transpose(Image.ROTATE_90)
out.show()
out = im.transpose(Image.ROTATE_180)
out.show()
out = im.transpose(Image.ROTATE_270)
out.show()