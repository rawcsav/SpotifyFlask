import asyncio
import aiohttp
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = 1  # in seconds
CONCURRENT_REQUESTS = 5


class GenreProcessingError(Exception):
    def __init__(self, message, genre, *args, **kwargs):
        super(GenreProcessingError, self).__init__(message, *args, **kwargs)
        self.genre = genre


async def fetch_genre_page(session, subgenre):
    try:
        genre_page_url = f"http://everynoise.com/engenremap-{subgenre}.html"
        async with session.get(genre_page_url) as response:
            return BeautifulSoup(await response.text(), "lxml")
    except aiohttp.ClientError as client_err:
        raise GenreProcessingError("Error fetching genre page.", subgenre) from client_err


async def process_genre(session, genre_div):
    genre = re.sub("[:'+»&\s-]", '', genre_div.text)
    soup2 = await fetch_genre_page(session, genre)

    spotify_link = soup2.find_all("a", text='playlist')
    playlist = spotify_link[0]['href'] if len(spotify_link) > 0 else None

    all_artist_divs = set(soup2.find_all("div", "genre scanme"))
    all_genres_related = set(soup2.find_all("div", "genre")) - all_artist_divs

    artist_weights = [
        artist['style'].split()[-1].replace('%', '') for artist in all_artist_divs
    ]
    artists = [
        artist.text.strip().replace("»", "") for artist in all_artist_divs
        if not artist.text.strip().replace("»", "").isspace()
    ]

    sim_weights = [
        weight['style'].split()[-1].replace('%', '')
        for weight in all_genres_related if 'nearby' in weight['id']
    ]
    opp_weights = [
        weight['style'].split()[-1].replace('%', '')
        for weight in all_genres_related if 'mirror' in weight['id']
    ]

    sim_genres = [
        other_genre.text.strip().replace("»", "")
        for other_genre in all_genres_related if 'nearby' in other_genre['id']
    ]
    opp_genres = [
        other_genre.text.strip().replace("»", "")
        for other_genre in all_genres_related if 'mirror' in other_genre['id']
    ]

    return {
        'genre': genre,
        'playlist': playlist,
        'artist_weights': artist_weights,
        'artists': artists,
        'sim_weights': sim_weights,
        'opp_weights': opp_weights,
        'sim_genres': sim_genres,
        'opp_genres': opp_genres,
    }


async def process_genres_and_create_csv(output_filename):
    results = []
    progress_bar = tqdm(total=len(all_genre_divs), desc="Processing genres", dynamic_ncols=True)

    async with aiohttp.ClientSession() as session:
        tasks = [process_genre(session, genre_div) for genre_div in all_genre_divs]

        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                results.append(result)
            except Exception as e:
                genre_text = "Unknown genre"
            finally:
                progress_bar.update(1)

    df = pd.DataFrame(results)
    df.to_csv(output_filename, index=False)
    progress_bar.close()


response = requests.get("http://everynoise.com/engenremap.html")
soup = BeautifulSoup(response.text, "lxml")
all_genre_divs = soup.find_all("div", "genre scanme")
output_filename = "/Users/gavinmason/PycharmProjects/BotifyStats/app/static/data/all_genres1.csv"
asyncio.run(process_genres_and_create_csv(output_filename))
