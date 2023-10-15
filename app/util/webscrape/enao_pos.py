import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def get_soup_from_url(url):
    """Fetch content from URL and return BeautifulSoup object."""
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'lxml')
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None


def extract_style_attributes(style_str):
    """Extract attributes from style string using regular expressions."""
    font_size = re.search(r"font-size:([^;]+)", style_str).group(1).strip()
    color_str = re.search(r"color:([^;]+)", style_str).group(1).strip()
    r, g, b = tuple(int(color_str[i:i + 2], 16) for i in (1, 3, 5))
    top = re.search(r"top:([^;]+)", style_str).group(1).strip()
    left = re.search(r"left:([^;]+)", style_str).group(1).strip()

    return font_size, color_str, (r, g, b), top, left


def parse_genres(soup):
    """Parse genres from BeautifulSoup object."""
    genres_elems = soup.find_all("div", class_="genre")
    genres_objs = []

    for genre in tqdm(genres_elems, desc="Parsing genres"):
        font_size, color_str, (r, g, b), top, left = extract_style_attributes(genre['style'])
        genre_obj = {
            "genre": genre.text.replace("»", "").strip(),
            "font_size": font_size,
            "color": color_str,
            "colors_rgb": f"rgb({r}, {g}, {b})",
            "top": top,
            "left": left
        }
        genres_objs.append(genre_obj)

    return genres_objs


async def scrape_genres_async(url):
    """Main function to scrape genres asynchronously."""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        soup = await loop.run_in_executor(pool, get_soup_from_url, url)
        if soup:
            return pd.DataFrame(parse_genres(soup))
        else:
            return None


url = "https://everynoise.com/engenremap.html"

# Start asynchronous scraping
loop = asyncio.get_event_loop()
genres_df = loop.run_until_complete(scrape_genres_async(url))

if genres_df is not None:
    genres_df.to_csv("/Users/gavinmason/PycharmProjects/BotifyStats/app/static/data/enao_pos.csv", index=False)

genres_df.head()
