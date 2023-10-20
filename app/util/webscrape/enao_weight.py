import asyncio
import os
from datetime import date

import aiohttp
import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time
from fake_useragent import UserAgent

ua = UserAgent(browsers=['edge', 'chrome', 'safari', 'firefox'])

headers = {
    'User-Agent': ua.random,
}
MAX_RETRIES = 5
DELAY_BETWEEN_REQUESTS = 10  # in seconds
CONCURRENT_REQUESTS = 2


class GenreProcessingError(Exception):
    def __init__(self, message, genre, *args, **kwargs):
        super(GenreProcessingError, self).__init__(message, *args, **kwargs)
        self.genre = genre


def exponential_backoff_wait(attempt, base_delay=2, max_delay=60):
    delay = min(base_delay * (2 ** attempt), max_delay)
    time.sleep(delay)


async def fetch_genre_page(session, subgenre):
    try:
        genre_page_url = f"http://everynoise.com/engenremap-{subgenre}.html"
        async with session.get(genre_page_url, headers=headers) as response:
            return BeautifulSoup(await response.text(), "lxml")
    except aiohttp.ClientError as client_err:
        raise GenreProcessingError("Error fetching genre page.", subgenre) from client_err


async def process_genre(session, genre_div, semaphore):
    async with semaphore:
        unformatted_genre = genre_div.text.strip().replace("»", "")  # Store unformatted genre
        genre = re.sub("[:'+»&\s-]", '', unformatted_genre)  # Continue with your existing code
        try:
            soup2 = await fetch_genre_page(session, genre)

            spotify_link = soup2.find_all("a", text='playlist')
            playlist = spotify_link[0]['href'] if len(spotify_link) > 0 else None

            all_artist_divs = set(soup2.find_all("div", "genre scanme"))
            all_genres_related = set(soup2.find_all("div", "genre")) - all_artist_divs

            sim_weights = ', '.join(
                [weight['style'].split()[-1].replace('%', '') for weight in all_genres_related if
                 'nearby' in weight['id']])
            opp_weights = ', '.join(
                [weight['style'].split()[-1].replace('%', '') for weight in all_genres_related if
                 'mirror' in weight['id']])
            sim_genres_list = [other_genre.text.strip().replace("»", "") for other_genre in all_genres_related if
                               'nearby' in other_genre['id']]
            opp_genres_list = [other_genre.text.strip().replace("»", "") for other_genre in all_genres_related if
                               'mirror' in other_genre['id']]

            sim_genres = ', '.join(sim_genres_list)
            opp_genres = ', '.join(opp_genres_list)

            if not (sim_genres and opp_genres):
                raise ValueError(f"Insufficient data for genre '{unformatted_genre}'")

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
        except Exception as e:
            print(f"Error processing genre '{unformatted_genre}': {str(e)}")  # Print the error
            return unformatted_genre


processed_genres_set = set()  # Set to keep track of processed genres


async def process_genres_and_create_csv(output_filename, genres_to_process=None):
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)  # Add this line here
    results = []
    failed_genres = []

    if genres_to_process:
        genre_divs_to_process = [div for div in all_genre_divs if
                                 div.text.strip().replace("»", "") in genres_to_process]
    else:
        genre_divs_to_process = all_genre_divs

    progress_bar = tqdm(total=len(genre_divs_to_process), desc="Processing genres", dynamic_ncols=True)

    async with aiohttp.ClientSession() as session:
        tasks = [process_genre(session, genre_div, semaphore) for genre_div in genre_divs_to_process]

        for future in asyncio.as_completed(tasks):
            try:
                result = await future
                if isinstance(result, dict):
                    genre_name = result['genre']
                    if genre_name not in processed_genres_set:
                        results.append(result)
                        processed_genres_set.add(genre_name)
                else:
                    failed_genres.append(result)
            finally:
                progress_bar.update(1)

    df = pd.DataFrame(results)
    if os.path.exists(output_filename):
        df.to_csv(output_filename, mode='a', header=False, index=False)
    else:
        df.to_csv(output_filename, index=False)
    progress_bar.close()

    return failed_genres


# Updated part at the end of your script:

response = requests.get("http://everynoise.com/engenremap.html")
soup = BeautifulSoup(response.text, "lxml")
all_genre_divs = soup.find_all("div", "genre scanme")

today_str = date.today().strftime("%Y-%m-%d")
output_filename = f"../../data/enao_genres{today_str}.csv"

# Initialize genres_to_process_list to cover all the genres before entering the loop
genres_to_process_list = [div.text.strip().replace("»", "") for div in all_genre_divs]
failed_genres = []
retries = 0

while genres_to_process_list and retries < MAX_RETRIES:
    failed_genres = asyncio.run(
        process_genres_and_create_csv(output_filename, genres_to_process=genres_to_process_list))
    genres_to_process_list = failed_genres

    if failed_genres:
        exponential_backoff_wait(retries)
        retries += 1

if failed_genres:
    print(f"Failed to process {len(failed_genres)} genres after {MAX_RETRIES} retries.")
    print("Errored genres:", ', '.join(failed_genres))
