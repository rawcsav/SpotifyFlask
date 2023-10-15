import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import pandas as pd


async def get_related_genres(session, genre):
    try:
        genre_url = genre.replace(" ", "%20")
        url = f"http://everynoise.com/everynoise1d.cgi?root={genre_url}&scope=all"

        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')

        # Extract the sub-genres from the table body
        genres = [a.text for a in soup.find_all("a", class_=False)[2:77]]
        related_genres = [genre for genre in genres]

        return genre, related_genres

    except Exception as e:
        print(f"An error occurred with genre {genre}: {e}")
        return genre, []


# Initialize an empty list outside the loop
data = []


async def main(genres):
    async with aiohttp.ClientSession() as session:
        tasks = [get_related_genres(session, genre) for genre in genres]

        for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            genre, related_genres = await task
            # Add the results to the data list
            for related_genre in related_genres:
                data.append([related_genre, genre])

    # Convert the data to a pandas DataFrame and write it to a CSV file
    df = pd.DataFrame(data, columns=['Related Genre', 'Parent Genre'])
    df.to_csv('/Users/gavinmason/PycharmProjects/BotifyStats/app/static/data/related_genres.csv', index=False)


# List of parent genres
parent_genres = ["pop", "rap", "rock",
                 "techno", "classical",
                 "focus", "jazz", "folk",
                 "pop rock", "metal", "funk"]

# Run the main function
with ThreadPoolExecutor() as executor:
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main(parent_genres))
    loop.run_until_complete(future)
