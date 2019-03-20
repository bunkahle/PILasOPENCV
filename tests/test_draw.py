import PILasOPENCV as Image
import PILasOPENCV as ImageDraw
# from PIL import Image
# from PIL import ImageDraw

im = Image.open("lena.jpg")
im.show()

draw = ImageDraw.Draw(im)
draw.line((0, 0) + im.size, fill=128)
draw.line((0, im.size[1], im.size[0], 0), fill=128)
draw.line((im.size[0]//2, im.size[1]//2+100, im.size[0]//2, im.size[1]//2-100), fill=(255, 0, 0), width=3)
draw.rectangle((10,10,100,100), fill=(96,96,96),outline=(255,255,255))
im.show()

image = Image.new('RGB',(91,91),'blue')
draw = ImageDraw.Draw(image)
draw.ellipse((0,0,90,90),'yellow','blue') # face
draw.ellipse((25,20,35,30),'yellow','blue') # left eye
draw.ellipse((28,25,32,30),'blue','blue') # left ...
draw.ellipse((50,20,60,30),'yellow','blue') # right eye
draw.ellipse((53,25,58,30),'blue','blue') # right ...
draw.arc((40,50,50,55), 0, 360, 0) # nose
draw.chord((20,40,70,70), 0, 90, 0) # smile
image.show()