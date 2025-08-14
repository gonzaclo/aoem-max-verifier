from PIL import Image, ImageEnhance, ImageOps
import pytesseract
import os
from only_letters import only_letters

i = 0
# Load files from a folder
file = 'image.png'

image = Image.open(file).convert(
    "L")  # Convert to grayscale
image = ImageOps.invert(image)

# Change size
image = image.resize((image.width * 5, image.height * 5))

# Crop the image
wd, hg = image.size
rect_crop = (
    int(wd * 0.66), int(hg * 0.15),
    int(wd * 0.85), int(hg * 0.30)
)
image = image.crop(rect_crop)

# Change contrast
# image = ImageEnhance.Contrast(image).enhance(2.0)
# image = ImageEnhance.Sharpness(image).enhance(2.0)


image = only_letters(image_in=image, highlight_color=(255,255,255), background=(0,0,0), threshold=100, inc=60)
image.show()

custom_config = r'--oem 3 --psm 6'
string = pytesseract.image_to_string(image=image, config=custom_config, lang='eng+spa+tur+ind')

i = i+1

print(f'------------ {i} --- {file} -----------')
print(string)