document.addEventListener('DOMContentLoaded', function () {
  const colorThief = new ColorThief();
  const playlistContainer = document.getElementById('playlist-container');

  playlistData.forEach(function (playlist) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = playlist.cover_art;

    img.onload = function () {
      const palette = colorThief.getPalette(img, 3); // Get the 3 most dominant colors

      // If there are less than 3 dominant colors, fill the remaining spaces with grey
      while (palette.length < 3) {
        palette.push([128, 128, 128]); // RGB for grey
      }

      // Convert each color to RGB format and create a box-shadow for each
      const boxShadow = palette
        .map(
          (color, index) =>
            `${10 * (index + 1)}px ${10 * (index + 1)}px 20px rgb(${
              color[0]
            }, ${color[1]}, ${color[2]})`,
        )
        .join(', ');

      const collaborativeLabel = playlist.collaborative
        ? '& Collaborative'
        : '';
      const securityLabel = playlist.public ? 'Public' : 'Private';

      playlistContainer.innerHTML += `
        <div class="playlist-item">
          <a href="/playlist/${playlist.id}?playlist_name=${encodeURIComponent(
            playlist.name,
          )}" class="playlist-option">
            <div class="image-container" style="box-shadow: ${boxShadow};">
              <img src="${playlist.cover_art}" alt="${
                playlist.name
              }" class="playlist-image">
              <div class="overlay-text">${playlist.name}</div>
            </div>
          </a>
        </div>`;
    };
  });
});
