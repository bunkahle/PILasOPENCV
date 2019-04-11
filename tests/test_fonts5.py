from __future__ import print_function
import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
# from PIL import ImageFont, ImageDraw, Image  
import cv2  
import numpy as np  

text_to_show = "The quick brown fox jumps over the lazy dog"  

# Load image in OpenCV  
image = cv2.imread("lena.jpg")  

# Convert the image to RGB (OpenCV uses BGR)  
cv2_im_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)  

# Pass the image to PIL  
pil_im = Image.fromarray(cv2_im_rgb)  

draw = ImageDraw.Draw(pil_im)  
# use a truetype font  
font = ImageFont.truetype("times.ttf", 25)  

# Draw the text  
draw.text((10, 10), text_to_show, fill="white", font=font)  

pil_im.show()
cv2.destroyAllWindows()  