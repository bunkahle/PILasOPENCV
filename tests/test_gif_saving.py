from __future__ import print_function
import PILasOPENCV as Image
# from PIL import Image

image = "Images/audrey.png"
pilimage = Image.open(image)
pilimage.show()
np_image = pilimage.getim()
print(type(np_image), np_image.shape)
r, g, b, a = pilimage.split()
new_image = Image.merge("RGB", (r, g, b))
new_image.save("audrey.gif")