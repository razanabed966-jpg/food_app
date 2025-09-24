import os
import requests, re, json
from bs4 import BeautifulSoup


ingredient = input('enter ingredient name: ')

if not os.path.exists(ingredient):
    os.mkdir(ingredient)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
}

params = {
    "q": ingredient,
    "tbm": "isch",
    "hl": "en",
    "ijn": "0",
    "tbs": "sur:publicdomain"
}

html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)

soup = BeautifulSoup(html.text, "lxml")

def get_original_images():
    all_script_tags = soup.select('script')

    matched_images_data = "".join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

    matched_images_data_fix = json.dumps(matched_images_data)

    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_image_data = re.findall(r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)

    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
        '',
        str(matched_google_image_data)
    )

    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails
    )

    full_res_images = [
        bytes(bytes(img, "ascii").decode("unicode-escape"), "ascii").decode("unicode-escape")
        for img in matched_google_full_resolution_images
    ]

    return full_res_images

images = get_original_images()

id = 0

for img in images:
    try:
        data = requests.get(img, timeout=5)
    except:
        data = None
    
    if data:
        data = data.content
        with open(f'{ingredient}{os.path.sep}{id}.jpg', 'wb') as f:
            f.write(data)
        
        id += 1

