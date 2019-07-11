from __future__ import print_function
import PILasOPENCV as Image
# from PIL import Image

images = "Images/hopper.gif", "Images/audrey.gif", "Images/Rotating_earth.gif", "Images/testcolors.gif"
for image in images:
    print(image)
    pilimage = Image.open(image)
    pilimage.show()
    if pilimage.is_animated:
        print("Image has", pilimage.n_frames, "frames")
        for i in range(pilimage.n_frames):
        	pilimage.seek(i)
        	pilimage.show(wait=66, destroyWindow=False)