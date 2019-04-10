import PILasOPENCV as Image
import PILasOPENCV as ImageFont
import PILasOPENCV as ImageDraw
pilimport = False

# from PIL import Image, ImageFont, ImageDraw
# pilimport = True

import numpy as np
import cv2

# Open image with OpenCV
im_o = cv2.imread('lena.jpg')
im_o = cv2.cvtColor(im_o, cv2.COLOR_RGB2BGR)
# Make into PIL Image
im_p = Image.fromarray(im_o)

# Get a drawing context
draw = ImageDraw.Draw(im_p)
monospace = ImageFont.truetype("cour.ttf", 32)
draw.text((40, 80),"Hopefully monospaced", (255,255,255), font=monospace)

# Convert back to OpenCV image and save
if not pilimport:
	result_o = im_p.getim()
	cv2.imshow('result_o', result_o)
	cv2.waitKey()
else:
	im_p.show()