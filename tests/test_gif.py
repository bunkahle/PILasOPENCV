from __future__ import print_function
import PILasOPENCV as Image
import cv2

images = "Images/hopper.gif", "Images/audrey.gif", "Images/testcolors.gif"
for image in images:
    pilimage = Image.open(image)
    pilimage.show()