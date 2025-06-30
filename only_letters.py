from PIL import Image

def only_letters(image_in, highlight_color=(0, 0, 0), background=(255,255,255), threshold=120, inc=20):
    image = image_in.convert("RGB")
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            # Detect near-black
            if r < threshold and g < threshold and b < threshold:
                pixels[x, y] = highlight_color
            elif r < threshold+round(inc/2) and g < threshold+round(inc/2) and b < threshold+round(inc/2):
                new_color = tuple(min(c+180,255) for c in highlight_color)
                pixels[x,y] = new_color
            elif r < threshold+inc and g < threshold+inc and b < threshold+inc:
                new_color = tuple(min(c+220,255) for c in highlight_color)
                pixels[x,y] = new_color
            else:
                pixels[x, y] = background
    return image