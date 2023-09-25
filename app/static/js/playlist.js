// Assuming playlistData is already defined and imported
// Assuming playlistData is already defined and imported
document.addEventListener('DOMContentLoaded', function () {
  const playlistContainer = document.getElementById('playlist-container');

  playlistData.forEach(function (playlist) {
    const collaborativeLabel = playlist.collaborative ? 'Collaborative' : '';

    const securityLabel = playlist.public ? 'Public' : 'Private';

    playlistContainer.innerHTML += `
      <a href="#" class="playlist-option" data-playlistid="${playlist.id}">
        <div class="playlist-item">
          <img src="${playlist.cover_art}" alt="${playlist.name}" class="playlist-image">
          <span class="playlist-name">${playlist.name}</span>
          <p>Created by ${playlist.owner}</p>
          <p>${playlist.total_tracks} Tracks</p>
          <p>Security: ${securityLabel} ${collaborativeLabel}</p>
        </div>
      </a>`;
  });
});
