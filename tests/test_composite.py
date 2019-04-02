import PILasOPENCV as Image
# from PIL import Image
#
img1 = Image.open('Images/cat.jpg')
img2 = Image.open('Images/landscape.jpg').resize(img1.size)
mask = Image.open('Images/mask1.jpg')
mask = mask.resize(img1.size)
#
im_new1 = Image.composite(img1, img2, mask)
im_new1.show()

img1 = Image.open('Images/cat.jpg')
img2 = Image.open('Images/landscape.jpg').resize(img1.size)
mask = Image.open('Images/mask2.jpg')
mask = mask.resize(img1.size)
#
im_new2 = Image.composite(img1, img2, mask)
im_new2.show()

img1 = Image.open('Images/cat.jpg')
img2 = Image.open('Images/landscape.jpg').resize(img1.size)
mask = Image.open('Images/mask3.jpg')
mask = mask.resize(img1.size)
#
im_new3 = Image.composite(img1, img2, mask)
im_new3.show()