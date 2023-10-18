document.getElementById('start-game').addEventListener('click', function () {
  fetch('/start', { method: 'POST' })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById('song-clip').src = `/clip/${data.song_id}`;
      document.getElementById('game-status').innerText = '';
    });
});

document.getElementById('submit-guess').addEventListener('click', function () {
  const guess = document.getElementById('song-guess').value;
  fetch('/guess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `song_guess=${guess}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === 'correct') {
        // Load next song
        fetch('/start', { method: 'POST' })
          .then((response) => response.json())
          .then((data) => {
            document.getElementById('song-clip').src = `/clip/${data.song_id}`;
          });
      } else if (data.status === 'wrong') {
        // Reload the audio clip with the wrong guess
        document.getElementById('song-clip').src = `/clip/${data.song_id}`;
        // Display the actual guess and guesses left
        document.getElementById('actual-guess').innerText =
          'Your guess: ' + guess;
        document.getElementById('guesses-left').innerText =
          'Guesses left: ' + data.guesses_left;
      } else if (data.status === 'win') {
        document.getElementById('game-status').innerText =
          'Congratulations, you won!';
      } else if (data.status === 'lose') {
        document.getElementById('game-status').innerText =
          'Game over, you lost.';
      }
    });
});
