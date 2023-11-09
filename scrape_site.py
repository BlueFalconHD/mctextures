from bs4 import BeautifulSoup
import requests
import re
import json

# Classes for Texture and Category
class Texture:
    def __init__(self, path, name):
        self.assetpath = path
        self.name = name

    def to_json(self):
        return {
             'name': self.name,
             'path': self.assetpath
        }

class Category:
    def __init__(self, title, items):
        self.title = title
        self.items = items

    def to_json(self):
        return {
    self.title: [texture.to_json() for texture in self.items]
    }

# Function to get the previous heading element
def get_previous_heading_element(element):
    prev_element = element.find_previous()
    while prev_element:
        if prev_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return prev_element
        prev_element = prev_element.find_previous()
    return None

# Function to merge categories
def merge_categories(categories):
    merged = {}
    for category in categories:
        if category.title not in merged:
            merged[category.title] = []
        merged[category.title].extend(category.items)
    return [Category(title, items) for title, items in merged.items()]

# Function to transform image URLs
def transform_image_url(url):
    # Find the '/thumb' part in the URL and remove it
    thumb_index = url.find('/thumb')
    if thumb_index > -1:
        # Split the URL at the point of '/thumb'
        first_part = url[:thumb_index]
        second_part = url[thumb_index + 6:]  # 6 is the length of '/thumb'

        # Find the last slash '/' after '/thumb' which is before the actual file name starts
        last_slash_index = second_part.rfind('/')
        if last_slash_index > -1:
            # Remove everything between '/thumb' and the last slash '/'
            second_part = second_part[last_slash_index + 1:]

        # Concatenate the first and second part to form the new URL
        url = first_part + '/' + second_part

    # Remove <any number>px-
    url = re.sub(r'\d+px-', '', url)

    return url

# Request the URL and scrape the content
url = 'https://minecraft.wiki/w/List_of_block_textures'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all gallery elements
category_elements = soup.select(".gallery")
categories = []

# Extract information and create Texture and Category objects
for e in category_elements:
    if len(e.contents) > 0:
        item_elements = e.select(".gallerybox > div")
        section_title_element = get_previous_heading_element(e)
        if section_title_element and section_title_element.select(".mw-headline"):
            section_title = section_title_element.select(".mw-headline")[0].text.strip()
        else:
            section_title = section_title_element.text.strip() if section_title_element else ""

        if item_elements:
            items = []
            for elem in item_elements:
                cmg = elem.select_one(".thumb > div > a.image > img")
                if cmg:
                    name = cmg['alt']
                    path = "https://minecraft.wiki" + cmg['src']
                    path = transform_image_url(path)
                    items.append(Texture(path, name))
            if items:
                category = Category(section_title, items)
                categories.append(category)

# Merge categories with the same title
categories = merge_categories(categories)

# Convert categories to JSON
categories_json = {cat.title: [texture.to_json() for texture in cat.items] for cat in categories}

# Write the JSON to a file named 'textures.json'
with open('textures.json', 'w') as file:
    json.dump(categories_json, file, indent=2)    