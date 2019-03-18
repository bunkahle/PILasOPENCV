import PILasOPENCV as Image
# from PIL import Image

im = Image.open("lena.jpg")
im.show()

im = Image.open("lena.jpg").convert("L")
im.show()
