# SpotifyFlask: Music Recommendation Tool

SpotifyFlask is a web-based tool leveraging the Spotify API to offer both personalized music recommendations and insights into user listening habits. This was coded primarily to host onto my [website](https://webstats.rawcsav.com/), however it could be run independently on a Flask development server.

## Features

- **Recommendation Generator**: Get song recommendations based on selected tracks, artists, or genres.
- **Dynamic Search**: Search for tracks, artists, or genres to set as seeds.
- **Tunable Preferences**: Adjust audio features like popularity, energy, tempo, and more.
- **In-Page Track Preview**: Some tracks offer previews directly within the tool.
- **Spotify Stats**: View top tracks, artists, and genres over varying time periods.


## Installation

1. Clone the repository:
```
git clone https://github.com/rawcsav/SpotifyFlask.git
```

2. Navigate to the project directory:
```
cd SpotifyFlask
```

3. Install required packages:
```
pip install -r requirements.txt
```

4. Set environment variables using `.env-template`. Ensure you've created an app through Spotify's developer console and that Spotify API credentials (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`) are set.

## Usage

### Recommendation Generator

1. Start the Flask application:
```
python run.py
```

2. Navigate to `http://localhost:8080` in a web browser.
3. Login and access the `Recommendations` sectio` through the main profile portal.
4. Use the search function to select tracks, artists, or genres as seeds.
5. Adjust preferences using the provided sliders.
6. Click "Get Recommendations" to receive a list of songs tailored to your inputs.

### Spotify Stats

- Access the `Stats` section through the main profile portal.
- View top tracks, artists, and genres based on short-term, medium-term, and long-term listening habits.

## License

Project is under the GNU License. Refer to `LICENSE` file for details.

## Acknowledgements

- Spotify Web API
- Flask
- Spotipy Python Library