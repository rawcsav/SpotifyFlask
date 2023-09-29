document.addEventListener('DOMContentLoaded', function () {
  const playlistContainer = document.getElementById('playlist-container');

  playlistData.forEach(function (playlist) {
    const collaborativeLabel = playlist.collaborative ? '& Collaborative' : '';

    const securityLabel = playlist.public ? 'Public' : 'Private';

    playlistContainer.innerHTML += `
  <div class="playlist-item">
    <a href="/playlist/${playlist.id}?playlist_name=${encodeURIComponent(
      playlist.name,
    )}"class="playlist-option">
      <div class="image-container">  
        <img src="${playlist.cover_art}" alt="${
          playlist.name
        }" class="playlist-image">
        <div class="overlay-text">${playlist.name}</div>
      </div>
    </a>
  </div>`;
  });
});
