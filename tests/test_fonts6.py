import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import PILasOPENCV as ImageFont
# from PIL import ImageFont, ImageDraw, Image
import numpy as np
import cv2

image = cv2.imread("lena.jpg")

# Convert to PIL Image
cv2_im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_im = Image.fromarray(cv2_im_rgb)

draw = ImageDraw.Draw(pil_im)

# Choose a font
font = ImageFont.truetype("Roboto-Regular.ttf", 40)

# Draw the text
draw.text((0, 0), "Your Text Here", font=font)

# Save the image
cv2_im_processed = pil_im.getim()
cv2.imshow("cv2_im_processed", cv2_im_processed)
cv2.waitKey()