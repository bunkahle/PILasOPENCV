import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
import cv2
# from PIL import Image
# from PIL import ImageDraw

im = Image.open("lena.jpg")
im.show("test")
try:
    cv2.destroyWindow("test")
except:
    pass

draw = ImageDraw.Draw(im)
draw.line((0, 0) + im.size, fill=128)
draw.line((0, im.size[1], im.size[0], 0), fill=128)
draw.line((im.size[0]//2, im.size[1]//2+100, im.size[0]//2, im.size[1]//2-100), fill=(255, 0, 0), width=3)
draw.rectangle((10,10,200,100), fill=(96,96,96),outline=(255,255,255))
im.show("test")
try:
    cv2.destroyWindow("test")
except:
    pass

image = Image.new('RGB',(91,91),'blue')
draw = ImageDraw.Draw(image)
draw.ellipse((0,0,90,90),'yellow','blue') # face
draw.ellipse((25,20,35,30),'yellow','blue') # left eye
draw.ellipse((28,25,32,30),'blue','blue') # left ...
draw.ellipse((50,20,60,30),'yellow','blue') # right eye
draw.ellipse((53,25,58,30),'blue','blue') # right ...
draw.arc((40,50,50,55), 0, 360, 0) # nose
draw.chord((20,40,70,70), 0, 90, 0) # smile
draw.chord((20,40,70,70), 90, 180, None, 0) # smile
draw.pieslice((30,50,60,60), 90, 180, (128, 128, 128))
draw.pieslice((30,50,60,60), 0, 90, None, (128, 128, 128))
image.show("test")
try:
    cv2.destroyWindow("test")
except:
    pass

img = Image.new('RGB', (500, 300), color = (200, 200, 200))
d = ImageDraw.Draw(img)
d.text((10,10), "Hello World\nnext line in the text", fill=(255, 128, 0))
point_loc = d.textsize("Hello World\nnext line in the text")
x, y = point_loc
point_loc0 = (x+20, y+20)
d.point(point_loc0, fill="red")
for i in range(10):
    point_loc = (point_loc0[0]+i*10, point_loc0[1]+i*10)
    try:
        d.point(point_loc, fill="red", width=i*2)
    except:
        point_loc = (point_loc0[0]+i*10-i, point_loc0[1]+i*10-i, point_loc0[0]+i*10+i, point_loc0[1]+i*10+i)
        d.arc(point_loc, 0, 360, fill="red")
d.polygon(((400,100),(300,200),(400,150)), fill="blue")
d.polygon(((50,160),(130,120),(40,150)), outline="green")
img.show("test")
try:
    cv2.destroyWindow("test")
except:
    pass
