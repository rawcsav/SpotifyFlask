# SpotifyFlask: Music Recommendation Tool

SpotifyFlask is a web-based tool leveraging the Spotify API to offer both personalized music recommendations and insights into user listening habits. This was coded primarily to host onto my [website](https://webstats.rawcsav.com/). However, if really desired, it could be run independently on a local Flask development server.

## Features

- **Recommendation Generator**: Get song recommendations based on selected tracks, artists, or genres.
- **Dynamic Search**: Search for tracks, artists, or genres to set as seeds.
- **Tunable Preferences**: Adjust audio features like popularity, energy, tempo, and more.
- **In-Page Track Preview**: Some tracks offer previews directly within the tool.
- **Spotify Stats**: View top tracks, artists, and genres over varying time periods.

## Usage

### Recommendation Generator

- Use the search function to select tracks, artists, or genres as seeds.
- Adjust preferences using the provided sliders.
- Click "Get Recommendations" to receive a list of songs tailored to your inputs.

### Spotify Stats

- Access the `Stats` section through the main profile portal.
- View top tracks, artists, and genres based on short-term, medium-term, and long-term listening habits.

## License

Project is under the GNU License. Refer to `LICENSE` file for details.

## Acknowledgements

- Spotify Web API
- Flask
- Spotipy Python Library
