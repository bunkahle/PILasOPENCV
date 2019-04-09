import PILasOPENCV as Image
# from PIL import Image

im = Image.open('Images/mask1.jpg')
pixels = list(im.getdata())
width, height = im.size
for i in range(height):
    pixels[i * width:(i + 1) * width] = width*[i]
new_im = Image.new("L", im.size, 0)
new_im.putdata(pixels)
new_im.show()