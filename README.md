# PILasOPENCV
Wrapper for Image functions which are used and called in the manner of the famous PIL module but work internally with OpenCV.

This library can be used to migrate old PIL projects to OPENCV.

You install this module with

    pip install PILasOPENCV
    
or you donwload the module and install it with:

    python setup.py install
    
and you change the import command at the beginning of your project files from

    from PIL import Image
    
or 

    import PIL.Image
    
or 

    import PIL.Image as Image
    
to

    import PILasOPENCV as Image
    
Internally no PIL or Pillow library is used anymore but the opencv module for doing all the graphical work.

Sample script:

    import PILasOPENCV as Image
    # was: from PIL import Image
    
    im = new("RGB", (512, 512), "white")
    im.show()
    
    testfile = "lena.jpg"
    im = open(testfile)
    print (type(im))
    # JPEG (512, 512) RGB
    im.save("lena.bmp")
    im.show()
    small = im.copy()
    small.thumbnail(thsize)
    small.show()
    thsize = (128, 128)
    box = (100, 100, 400, 400)
    region = im.crop(box)
    print("region",region.format, region.size, region.mode)
    # region = region.transpose(Image.ROTATE_180)
    region = region.transpose(ROTATE_180)
    region.show()
    im.paste(region, box)
    im.show()
     
# Export CV2/Numpy images
You can export the cv2/numpy image from an Image instance with the command getim():
    
    from __future__ import print_function
    import PILasOPENCV as Image
    import cv2
    im = Image.open("lena.jpg")
    numpy_image = im.getim()
    print(type(numpy_image), numpy_image.shape)
    cv2.imshow("numpy_image", numpy_image)
    cv2.waitKey(0)
    
# Attention:
This is a very unstable development version. Use with care. Not much testing has been done to it.

# TO DO:
ImageFilter, ImageFont, ImageChops, ImageDraw are not implemented yet.

ImageMode, ImageColor are implemented but have not been fully tested.
If you want to import them, import them with:

    from PILasOPENCV import ImageMode, ImageColor

# Dependencies:
You need to have numpy and opencv installed to run the module.
Install it with 

     pip install numpy opencv-python
     
# Licence
MIT
