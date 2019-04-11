from __future__ import print_function
import PILasOPENCV as Image
import cv2
im = Image.open("lena.jpg")
numpy_image = im.getim()
print(type(numpy_image), numpy_image.shape)
cv2.imshow("numpy_image", numpy_image)
cv2.waitKey(0)
# import numpy image
new_im = Image.new("RGB", (512, 512), "black")
new_im.show()
new_im.setim(numpy_image)
new_im.show()