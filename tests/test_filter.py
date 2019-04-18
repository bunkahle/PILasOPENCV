from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageFilter
import cv2
# from PIL import Image
# from PIL import ImageFilter

im0 = Image.open("Images/plane.jpg")
print("ORIGINAL")
im0.show("test")

im = im0.filter(ImageFilter.BLUR)
print("BLUR")
im.show("test")

im = im0.filter(ImageFilter.CONTOUR)
print("CONTOUR")
im.show("test")

im = im0.filter(ImageFilter.DETAIL)
print("DETAIL")
im.show("test")

im = im0.filter(ImageFilter.EDGE_ENHANCE)
print("EDGE_ENHANCE")
im.show("test")

im = im0.filter(ImageFilter.EDGE_ENHANCE_MORE)
print("EDGE_ENHANCE_MORE")
im.show("test")

im = im0.filter(ImageFilter.EMBOSS)
print("EMBOSS")
im.show("test")

im = im0.filter(ImageFilter.FIND_EDGES)
print("FIND_EDGES")
im.show("test")

im = im0.filter(ImageFilter.SHARPEN)
print("SHARPEN")
im.show("test")

im = im0.filter(ImageFilter.SMOOTH)
print("SMOOTH")
im.show("test")

im = im0.filter(ImageFilter.SMOOTH_MORE)
print("SMOOTH_MORE")
im.show("test")

im = im0.filter(ImageFilter.GaussianBlur(radius=10))
print("GaussianBlur")
im.show("test")
