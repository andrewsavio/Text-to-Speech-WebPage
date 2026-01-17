from PIL import Image
import os

img_path = r"frontend\public\andrew.png"
ico_path = r"frontend\public\andrew.ico"

try:
    img = Image.open(img_path)
    img.save(ico_path, format='ICO', sizes=[(256, 256)])
    print(f"Successfully converted {img_path} to {ico_path}")
except Exception as e:
    print(f"Failed to convert: {e}")
