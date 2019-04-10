import PILasOPENCV as Image
# from PIL import Image

def create_default_image(image_width, image_height, do_gradient=True):
    image_bytes = bytearray([0x70, 0x70, 0x70]) * image_width * image_height
    if do_gradient:
        i = 0
        for y in range(image_height):
            for x in range(image_width):
                image_bytes[i] = int(255.0 * (float(x) / image_width))   # R
                image_bytes[i+1] = int(255.0 * (float(y) / image_height))  # G
                image_bytes[i+2] = 0                                # B
                i += 3
    image = Image.frombytes('RGB', (image_width, image_height), bytes(image_bytes))
    # image = Image.fromstring('RGB', (image_width, image_height), bytes(image_bytes))
    return image 

im = create_default_image(300, 300)
im.show()