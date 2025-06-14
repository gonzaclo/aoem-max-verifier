from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from only_letters import only_letters

# Download image

image = Image.open('Google Chrome 2025-06-14 13.33.38.png').convert(
    "L")  # Convert to grayscale
image = ImageOps.invert(image)
# Crop the image
wd, hg = image.size
rect_crop = (
    int(wd * 0.65), int(hg * 0.15),
    int(wd * 0.85), int(hg * 0.30)
)
image = image.crop(rect_crop)

image = only_letters(image_in=image, threshold=160)

# Change contrast
# image = ImageEnhance.Contrast(image).enhance(2.0)
# image = ImageEnhance.Sharpness(image).enhance(2.0)
image = image.resize((image.width * 5, image.height * 5))
image.show()

string = pytesseract.image_to_string(image=image)

print(string)