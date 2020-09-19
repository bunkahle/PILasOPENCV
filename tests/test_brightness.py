# from PIL import Image, ImageEnhance
import PILasOPENCV as Image
import PILasOPENCV as ImageEnhance

img = Image.open('lena.jpg')
#
enhancer = ImageEnhance.Brightness(img)
enhancer.enhance(0.0).save(
    "ImageEnhance_Brightness_000.jpg")
enhancer.enhance(0.25).save(
    "ImageEnhance_Brightness_025.jpg")
enhancer.enhance(0.5).save(
    "ImageEnhance_Brightness_050.jpg")
enhancer.enhance(0.75).save(
    "ImageEnhance_Brightness_075.jpg")
enhancer.enhance(1.0).save(
    "ImageEnhance_Brightness_100.jpg")