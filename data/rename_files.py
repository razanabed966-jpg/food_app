import os
from PIL import Image, ImageOps

DIR = r'D:\Hsoub\AI_Course\food_app\data'

id = 0

def resize_images(path):
    global id
    for sub_path in os.listdir(path):
        full_sub_path = os.path.join(path, sub_path)
        if os.path.isdir(full_sub_path):
            resize_images(full_sub_path)
            continue

        filename, file_extension = os.path.splitext(full_sub_path)
        if file_extension == '.jpg':
            new_file_path = os.path.join(path, f'img_{id}.jpg')
            os.rename(full_sub_path, new_file_path)
            id += 1
            

resize_images(DIR)
