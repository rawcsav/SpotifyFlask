document.addEventListener('DOMContentLoaded', function () {
  let isPlaying = false;
  const audioPlayer = document.getElementById('song-clip');

  audioPlayer.addEventListener('playing', () => {
    isPlaying = true;
  });

  let currentClipLength = 0;

  document.getElementById('start-game').addEventListener('click', function () {
    document.querySelector('.start-screen').style.display = 'none';
    document.querySelector('.game-column').style.display = 'block';

    fetch('/start', { method: 'POST' })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById('song-clip').src = `/clip/${data.song_id}`;
        document.getElementById('current-genre').innerText = data.current_genre;
        currentClipLength = data.clip_length;
      });
  });

  document.getElementById('play-clip').addEventListener('click', function () {
    playClip(currentClipLength);
  });

  function playClip(clipDuration) {
    audioPlayer.currentTime = 0;
    audioPlayer.play();

    setTimeout(() => {
      if (isPlaying) {
        audioPlayer.pause();
        isPlaying = false;
      }
    }, clipDuration * 1000);
  }

  document
    .getElementById('submit-guess')
    .addEventListener('click', function () {
      const guess = document.getElementById('searchInput').value;

      fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `song_guess=${guess}`,
      })
        .then((response) => response.json())
        .then((data) => {
          let li = document.createElement('li');
          if (data.status === 'game_over') {
            displayEndResults(data);
            return;
          }

          if (data.status === 'correct_game_over') {
            li.textContent = `${guess} - Correct`;
            li.className = 'correct';
            document.getElementById('bonus-questions').style.display = 'block';
            displayEndResults(data);
            return;
          }

          if (data.status === 'correct') {
            li.textContent = `${guess} - Correct`;
            li.className = 'correct';
            document.getElementById('bonus-questions').style.display = 'block';
          } else if (data.status === 'wrong') {
            li.textContent = `${guess} - Wrong`;
            li.className = 'wrong';
            currentClipLength = data.clip_length;

            document.getElementById('guess-list').appendChild(li);
            if (data.guesses_left > 0) {
              loadNextSong();
            }
          } else if (data.status === 'lose') {
            displayEndResults(data);
          }
          // Add the guess to the list
          document.getElementById('guess-list').appendChild(li);
        });
    });

  function loadNextSong() {
    const currentGenre = document.getElementById('current-genre').innerText;

    fetch('/start', { method: 'POST' })
      .then((response) => response.json())
      .then((data) => {
        // Check if the game is over
        if (data.status === 'game_over') {
          displayEndResults(data);
          return;
        }

        // Check if the genre has changed
        if (currentGenre !== data.current_genre) {
          document.getElementById('guess-list').innerHTML = '';
        }

        // Update song source and current genre
        document.getElementById('song-clip').src = `/clip/${data.song_id}`;
        document.getElementById('current-genre').innerText = data.current_genre;
        document.getElementById('bonus-questions').style.display = 'none';

        currentClipLength = data.clip_length;
        playClip(currentClipLength);
      });
  }

  function displayEndResults(data) {
    const correctGuesses =
      (data.correct_guess_general ? 1 : 0) +
      (data.correct_guess_rock ? 1 : 0) +
      (data.correct_guess_hiphop ? 1 : 0);
    const totalGuesses =
      data.attempts_made_general +
      data.attempts_made_rock +
      data.attempts_made_hiphop;
    alert(
      `You guessed ${correctGuesses} out of 3 songs correctly in ${totalGuesses} total guesses.`,
    );
  }

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
        }
        document.getElementById('results').innerHTML = htmlResults;
        document.querySelectorAll('.song-btn').forEach((btn) => {
          btn.addEventListener('click', function () {
            document.getElementById('searchInput').value = this.textContent;
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

  document.getElementById('skip-bonus').addEventListener('click', function () {
    fetch('/bonus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `album_guess=&release_year_guess=`,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'correct') {
          alert('Your bonus answers are correct!');
          loadNextSong();
        } else {
          alert(
            `Incorrect bonus answers! Correct album: ${data.correct_album}. Correct release year: ${data.correct_release_year}`,
          );
          loadNextSong();
        }
      });
  });
});
