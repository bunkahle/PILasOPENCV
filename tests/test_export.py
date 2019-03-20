from __future__ import print_function
import PILasOPENCV as Image
import cv2

im = Image.open("lena.jpg")
numpy_image = im.getim()
print(type(numpy_image), numpy_image.shape)
cv2.imshow("numpy_image", numpy_image)
cv2.waitKey(0)
