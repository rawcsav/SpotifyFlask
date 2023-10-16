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
    unformatted_genre = genre_div.text.strip().replace("»", "")  # Store unformatted genre
    genre = re.sub("[:'+»&\s-]", '', unformatted_genre)  # Continue with your existing code
    soup2 = await fetch_genre_page(session, genre)

    spotify_link = soup2.find_all("a", text='playlist')
    playlist = spotify_link[0]['href'] if len(spotify_link) > 0 else None

    all_artist_divs = set(soup2.find_all("div", "genre scanme"))
    all_genres_related = set(soup2.find_all("div", "genre")) - all_artist_divs

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

    sim_weights = ', '.join(
        [weight['style'].split()[-1].replace('%', '') for weight in all_genres_related if 'nearby' in weight['id']])
    opp_weights = ', '.join(
        [weight['style'].split()[-1].replace('%', '') for weight in all_genres_related if 'mirror' in weight['id']])
    sim_genres = ', '.join([other_genre.text.strip().replace("»", "") for other_genre in all_genres_related if
                            'nearby' in other_genre['id']])
    opp_genres = ', '.join([other_genre.text.strip().replace("»", "") for other_genre in all_genres_related if
                            'mirror' in other_genre['id']])

    return {
        'genre': unformatted_genre,
        'sim_genres': sim_genres,
        'sim_weights': sim_weights,
        'opp_genres': opp_genres,
        'opp_weights': opp_weights,
        'spotify_url': playlist,
        'color_hex': None,
        'color_rgb': None,
        'x': None,
        'y': None,
    }


async def process_genres_and_create_csv(output_filename, genres_to_process=None):
    results = []

    if genres_to_process:
        # Filter the all_genre_divs based on the provided genres_to_process list
        genre_divs_to_process = [div for div in all_genre_divs if
                                 div.text.strip().replace("»", "") in genres_to_process]
    else:
        # If no specific genres provided, process all genres
        genre_divs_to_process = all_genre_divs

    progress_bar = tqdm(total=len(genre_divs_to_process), desc="Processing genres", dynamic_ncols=True)

    async with aiohttp.ClientSession() as session:
        tasks = [process_genre(session, genre_div) for genre_div in genre_divs_to_process]

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


def load_genres_from_file(filename):
    """
    Load genres from a .txt file. One genre per line.
    """
    with open(filename, 'r') as file:
        # Read the lines, strip whitespace, and filter out empty lines
        genres = [line.strip() for line in file if line.strip()]
    return genres


response = requests.get("http://everynoise.com/engenremap.html")
soup = BeautifulSoup(response.text, "lxml")
all_genre_divs = soup.find_all("div", "genre scanme")
genres_to_process_list = ["country road", "german hip hop", "houston rap", "indian indie", "musica sonorense",
                          "swedish trap", "minimal techno", "instrumental worship", "spanish new wave",
                          "rock urbano mexicano", "nu disco", "detroit trap", "rebel blues", "alabama rap"]
output_filename = "/Users/gavinmason/PycharmProjects/BotifyStats/app/data/missing_genres1.csv"
asyncio.run(process_genres_and_create_csv(output_filename, genres_to_process=genres_to_process_list))
