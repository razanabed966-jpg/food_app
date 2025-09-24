import os
from PIL import Image, ImageOps

DIR = r'D:\Hsoub\AI_Course\food_app\data'

def resize_images(path):
    for sub_path in os.listdir(path):
        full_sub_path = os.path.join(path, sub_path)
        if os.path.isdir(full_sub_path):
            resize_images(full_sub_path)
            continue

        filename, file_extension = os.path.splitext(full_sub_path)
        if file_extension == '.jpg':
            try:
                img = Image.open(full_sub_path)
            except:
                os.remove(full_sub_path)
                continue
            new_img = ImageOps.fit(img, (224, 224))
            try:
                new_img.save(full_sub_path)
            except:
                os.remove(full_sub_path)

resize_images(DIR)
