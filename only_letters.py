from PIL import Image

def only_letters(image_in, highlight_color=(0, 0, 0), threshold=20):
    image = image_in.convert("RGB")
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            # Detect near-black
            if r < threshold and g < threshold and b < threshold:
                pixels[x, y] = highlight_color
            else:
                pixels[x, y] = (255,255,255)
    return image