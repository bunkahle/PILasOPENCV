import PILasOPENCV as Image
# from PIL import Image

im = Image.open("lena.jpg")
im.show()

r, g, b = im.split()

im = Image.merge("RGB", (b, g, r))
im.show()