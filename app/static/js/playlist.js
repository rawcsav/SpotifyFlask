document.addEventListener('DOMContentLoaded', function () {
  const playlistContainer = document.getElementById('playlist-container');

  playlistData.forEach(function (playlist) {
    const collaborativeLabel = playlist.collaborative ? 'Collaborative' : '';

    const securityLabel = playlist.public ? 'Public' : 'Private';

    playlistContainer.innerHTML += `
  <div class="playlist-item">
    <a href="#" class="playlist-option" data-playlistid="${playlist.id}"> <!-- Moved anchor tag -->
      <div class="image-container">  
        <img src="${playlist.cover_art}" alt="${playlist.name}" class="playlist-image">
        <div class="overlay-text">${playlist.name}</div>
      </div>
    </a>
    <p>${playlist.owner}</p>
    <p>${playlist.total_tracks} Tracks</p>
    <p>${securityLabel} ${collaborativeLabel}</p>
  </div>`;
  });
});
