document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('start-game').addEventListener('click', function () {
    fetch('/start', { method: 'POST' })
      .then((response) => response.json())
      .then((data) => {
        console.log(data); // Log the entire response data

        document.getElementById('song-clip').src = `/clip/${data.song_id}`;
        document.getElementById('current-genre').innerText = data.current_genre;
      });
  });
  let playButton = document.getElementById('play-clip');
  let audioPlayer = document.getElementById('song-clip');

  let isPlaying = false;
  const maxAttempts = 6;
  let attempts = 0;
  let durations = [0.5, 1, 3, 5, 10, 30];
  let durationIndex = 0;
  let clipDuration = durations[durationIndex];
  audioPlayer.addEventListener('playing', () => {
    isPlaying = true;
  });
  let trackIds = {};

  playButton.addEventListener('click', function () {
    playClip(clipDuration);
  });

  function playClip(clipDuration) {
    audioPlayer.currentTime = 0;
    audioPlayer.play();

    setTimeout(() => {
      if (isPlaying) {
        audioPlayer.pause();
      }
      playButton.disabled = false; // Enable the play button after the clip is paused
    }, clipDuration * 1000);
  }

  document
    .getElementById('submit-guess')
    .addEventListener('click', function () {
      const guess = document.getElementById('searchInput').value;

      const emptyGuessDiv = Array.from(
        document
          .getElementById('guesses')
          .getElementsByClassName('guess-input'),
      ).find((div) => !div.textContent);

      if (emptyGuessDiv) {
        emptyGuessDiv.textContent += guess;
      }

      fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `song_guess=${guess}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === 'correct') {
            playClip(audioPlayer.duration);
            document.getElementById('bonus-questions').style.display = 'block';
            emptyGuessDiv.style.backgroundColor = 'green';
          } else {
            attempts++;
            if (attempts < maxAttempts) {
              if (durationIndex < durations.length - 1) {
                durationIndex++;
              }
              clipDuration = durations[durationIndex];
              emptyGuessDiv.style.backgroundColor = 'red';
            }
            if (attempts === maxAttempts) {
              // Reset attempts count and duration index for the next genre
              attempts = 0;
              durationIndex = 0;
              // Refresh the game column
              document.getElementById('searchInput').value = '';
              let guessRows = document.querySelectorAll('.guess-input');
              for (let row of guessRows) {
                row.textContent = '';
              }
              // Fetch the next song for the new genre
              fetch('/start', { method: 'POST' })
                .then((response) => response.json())
                .then((data) => {
                  document.getElementById(
                    'song-clip',
                  ).src = `/clip/${data.song_id}`;
                  document.getElementById('current-genre').innerText =
                    data.current_genre;
                });
            }
          }
        });
    });

  function debounce(func, delay) {
    let timeout;
    return function (...args) {
      const context = this;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), delay);
    };
  }

  const debouncedSearch = debounce(function () {
    const query = this.value;
    if (!query) {
      document.getElementById('results').innerHTML = '';
      return;
    }

    fetch(`/songfull_search?query=${query}`)
      .then((response) => response.json())
      .then((data) => {
        let htmlResults = '';
        for (let song of data) {
          htmlResults += `<button class="song-btn">${song.title} - ${song.artist}</button>`;
          trackIds[`${song.title} - ${song.artist}`] = song.track_id;
        }
        document.getElementById('results').innerHTML = htmlResults;
        document.querySelectorAll('.song-btn').forEach((btn) => {
          btn.addEventListener('click', function () {
            document.getElementById('searchInput').value = this.textContent;
            selectedTrackId = trackIds[this.textContent];
          });
        });
      })
      .catch((err) => {
        console.error('Error fetching data:', err);
        document.getElementById('results').innerHTML =
          'Error fetching results.';
      });
  }, 750);

  document
    .getElementById('searchInput')
    .addEventListener('input', debouncedSearch);

  document.getElementById('start-game').addEventListener('click', function () {
    document.querySelector('.start-screen').style.display = 'none';
    document.querySelector('.game-column').style.display = 'block';
  });

  document.getElementById('skip-bonus').addEventListener('click', function () {
    document.getElementById('album-guess').value = '';
    document.getElementById('release-year-guess').value = '';

    // Make a POST request to the '/bonus' route with empty bonus answers
    fetch('/bonus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `album_guess=&release_year_guess=`,
    })
      .then((response) => response.json())
      .then((data) => {
        // Refresh the game column
        document.getElementById('searchInput').value = '';
        document.getElementById('selectedTrackId').value = '';

        // Clear the guess rows
        let guessRows = document.querySelectorAll('.guess-input');
        for (let row of guessRows) {
          row.textContent = '';
        }

        // Fetch the next song for the new genre
        fetch('/start', { method: 'POST' })
          .then((response) => response.json())
          .then((data) => {
            document.getElementById('song-clip').src = `/clip/${data.song_id}`;
            document.getElementById('current-genre').innerText =
              data.current_genre;
            document.getElementById('bonus-questions').style.display = 'none';
          });
      });
  });
});
