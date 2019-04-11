# PILasOPENCV
Wrapper for Image functions which are used and called in the manner of the famous PIL module but work internally with OpenCV. Since there is no truetype font support for Python in OpenCV (it exists for the OpenCV C libraries) this module might be useful since it supports all kind of truetype fonts to be integrated in images. It depends on the library freetype-py. See below for more details on this.

This library can be used to migrate old PIL projects to OPENCV.

You install this module with

    pip install PILasOPENCV
    
or you donwload the module and install it with:

    python setup.py install
    
and then you change the import command at the beginning of your project files from

    from PIL import Image
    
or 

    import PIL.Image as Image
    
to

    import PILasOPENCV as Image
    
Internally no PIL or Pillow library is used anymore but the opencv and numpy module for doing all the graphical work.

Sample script:

    from __future__ import print_function
    import PILasOPENCV as Image
    # was: from PIL import Image

    im = Image.new("RGB", (512, 512), "red")
    im.show()

    testfile = "lena.jpg"
    im = Image.open(testfile)
    print (type(im))
    # JPEG (512, 512) RGB
    im.save("lena.bmp")
    im.show()
    small = im.copy()
    thsize = (128, 128)
    small.thumbnail(thsize)
    small.show()
    box = (100, 100, 400, 400)
    region = im.crop(box)
    print("region",region.format, region.size, region.mode)
    # region = region.transpose(Image.ROTATE_180)
    region = region.transpose(Image.ROTATE_180)
    region.show()
    im.paste(region, box)
    im.show()
     
# Export and import CV2/Numpy images
You can export the cv2/numpy image from an Image instance with the command getim():
    
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
    new_im.setim(numpy_image)
    new_im.show()
    
# Usage of truetype fonts in PILasOPENCV
PILasOPENCV supports the use of truetype fonts with Python. The python module freetype-py needs to be installed for this. To import and use truetype fonts you can do the following:

	from __future__ import print_function
	import PILasOPENCV as Image
	import PILasOPENCV as ImageDraw
	import PILasOPENCV as ImageFont
	import cv2
	# was: from PIL import Image, ImageDraw, ImageFont

	font = ImageFont.truetype("arial.ttf", 18)
	print(font)
	im = Image.open("lena.jpg")
	draw = ImageDraw.Draw(im)
	text = "Lena's image"
	draw.text((249,455), text, font=font, fill=(0, 0, 0))
	print(ImageFont.getsize(text, font))
	mask = ImageFont.getmask(text, font)
	# in PIL this code is written differently:
	# print(font.getsize(text))
	# mask = font.getmask(text)
	print(type(mask))
	cv2.imshow("mask", mask)
	im.show()
    
# Attention:
This is a very unstable development version. Use with care. Not much testing has been done to it though tests have been done which can be found in the tests directory.

# TO DO:
The most used classes and methods like ImageMode, ImageColor, ImageChops are implemented but have not been fully tested. Image, ImageFont, ImageDraw, ImageGrab and ImageFilter have been tested with several testcases.
Some functions/methods of these classes are missing and are not implemented though. 
If you want to import them, import them with:

    import PILasOPENCV as ImageMode
    import PILasOPENCV as ImageColor
    import PILasOPENCV as ImageDraw
    import PILasOPENCV as ImageFilter
    import PILasOPENCV as ImageChops
    import PILasOPENCV as ImageFont
    import PILasOPENCV as ImageGrab
    
The PIL classes ImageEnhance, ImageFile, ImageFileIO, ImageMath, ImageOps, ImagePath, ImageQt, ImageSequence, ImageStat, ImageTk, ImageWin, ImageGL have not been implemented.
    
If you want to use the methods getsize and getmask from ImageFont you have to use them differently:

	from __future__ import print_function
	import PILasOPENCV as Image
	import PILasOPENCV as ImageDraw
	import PILasOPENCV as ImageFont
	import cv2
	# from PIL import Image, ImageDraw, ImageFont
    
	font = ImageFont.truetype("ARIAL.ttf".lower(), 18)
	im = Image.open("lena.jpg")
	draw = ImageDraw.Draw(im)
	text = "Lena's image"
	draw.text((249,455), text, font=font, fill=(0, 0, 0))
	# in PIL:
	# print(font.getsize(text))
	# mask = font.getmask(text)
	print(ImageFont.getsize(text, font))
	mask = ImageFont.getmask(text, font)
	print(type(mask))
	cv2.imshow("mask", mask)
	im.show()

If you want to fork this project, feel free to do so. Give me a message in case you are forking and improving the code.
abunkahle@t-online.de

# Dependencies:
You need to have numpy, opencv freetype and mss installed to run the module completely.
Install it with 

     pip install numpy opencv-python freetype-py mss

# Version history:

1.8: ImageGrab.grab() and ImageGrab.grabclipboard() implemented with dependency on mss

1.7: fixed fromarray

1.6: fixed frombytes, getdata, putdata and caught exception in case freetype-py is not installed or dll is missing 

# Licence
MIT
