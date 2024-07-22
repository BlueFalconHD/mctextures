import requests
from bs4 import BeautifulSoup
import re
import json


class Texture:
    def __init__(self, path, name):
        self.assetpath = path
        self.name = name

    def to_json(self):
        return {"name": self.name, "path": self.assetpath}


class Category:
    def __init__(self, title):
        self.title = title
        self.items = []

    def add_item(self, texture):
        self.items.append(texture)

    def to_json(self):
        return {self.title: [texture.to_json() for texture in self.items]}


def get_previous_heading(element):
    while element:
        element = element.find_previous()
        if element and element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            return element
    return None


def transform_image_url(url):
    url = "https://minecraft.wiki" + url
    thumb_index = url.find("/thumb")
    if thumb_index > -1:
        first_part = url[:thumb_index]
        second_part = url[thumb_index + 6 :]
        last_slash_index = second_part.rfind("/")
        if last_slash_index > -1:
            second_part = second_part[last_slash_index + 1 :]
        url = first_part + "/" + second_part
    return re.sub(r"\d+px-", "", url)


def merge_and_deduplicate_categories(categories):
    merged = {}
    items_names = set()

    for category in categories:
        if category.title not in merged:
            merged[category.title] = Category(category.title)
        for item in category.items:
            if item.name not in items_names:
                items_names.add(item.name)
                merged[category.title].add_item(item)

    return list(merged.values())


def my_print(t, scope):
    print(("    " * scope) + t)


def scrape_textures(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    category_elements = soup.select(".gallery")
    categories = []

    scope = 0
    my_print("=== GALLERIES ===", scope)
    scope += 1

    for e in category_elements:
        item_elements = e.select(".gallerybox")
        section_title_element = get_previous_heading(e)
        section_title = (
            section_title_element.select_one(".mw-headline").text.strip()
            if section_title_element
            else ""
        )

        my_print(f"# {section_title}", scope)
        scope += 1

        category = Category(section_title)
        for elem in item_elements:
            texture_name_elem = elem.select_one(".gallerytext > p > a")
            texture_src_elem = elem.select_one(".thumb > span > a > img")
            if texture_name_elem and texture_src_elem:
                texture_name = (
                    texture_name_elem.text.strip()
                    if texture_name_elem.text
                    else "Unnamed"
                )
                texture_url = transform_image_url(texture_src_elem["src"])
                my_print(f"{texture_name}    ->    ({texture_url})", scope)
                category.add_item(Texture(texture_url, texture_name))
            else:
                if texture_name_elem is None or texture_name_elem.text is None:
                    my_print(
                        f"One element in section {section_title} has no name.", scope
                    )
                if texture_src_elem is None:
                    my_print(
                        f"One element in section {section_title} has no src url.", scope
                    )
        categories.append(category)
        scope -= 1

    scope -= 1

    my_print("=== MERGING DUPLICATE GALLERIES ===", scope)
    scope += 1

    categories = merge_and_deduplicate_categories(categories)

    for cat in categories:
        my_print(f"# {cat.title}", scope)
        scope += 1
        for texture in cat.items:
            my_print(f"{texture.name}    ->    ({texture.assetpath})", scope)
        scope -= 1

    scope -= 1

    return categories


def save_categories_to_json(categories, file_name):
    categories_json = {
        cat.title: [texture.to_json() for texture in cat.items] for cat in categories
    }
    with open(file_name, "w") as file:
        json.dump(categories_json, file, indent=2)


if __name__ == "__main__":
    url = "https://minecraft.wiki/w/List_of_block_textures"
    categories = scrape_textures(url)
    save_categories_to_json(categories, "textures.json")
