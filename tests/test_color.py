from __future__ import print_function
import PILasOPENCV as ImageColor
import PILasOPENCV as ImageMode

print(dir(ImageColor))
print(dir(ImageMode))

colors = ["black", "white", "red", "orange", "yellow", "green", "blue", "violet", "magenta"]
for color in colors:
	print("Color:", color, ImageColor.ImageColor().getrgb(color))
	print("Color:", color, ImageColor.ImageColor().getcolor(color, "L"))