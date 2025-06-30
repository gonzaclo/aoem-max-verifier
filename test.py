from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from only_letters import only_letters

# Download image

image = Image.open('images/Screenshot_20250629_171840_Age_of_Empires_Mobile.jpeg').convert(
    "L")  # Convert to grayscale
image = ImageOps.invert(image)
# Crop the image
wd, hg = image.size
rect_crop = (
    int(wd * 0.65), int(hg * 0.15),
    int(wd * 0.85), int(hg * 0.30)
)
image = image.crop(rect_crop)

# Change contrast
# image = ImageEnhance.Contrast(image).enhance(2.0)
# image = ImageEnhance.Sharpness(image).enhance(2.0)
image = image.resize((image.width * 3, image.height * 3))
image = only_letters(image_in=image, threshold=150)
image.show()

string = pytesseract.image_to_string(image=image)

print(string)