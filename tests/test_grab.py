from __future__ import print_function
import PILasOPENCV as ImageGrab
#<from PIL import Image, ImageGrab

im = ImageGrab.grab(bbox=(100,120,200,250))
im.show()
im = ImageGrab.grab()
im.show()
im = ImageGrab.grabclipboard()
if im is None:
    print("No image saved in the clipboard")
else:
    im.show()