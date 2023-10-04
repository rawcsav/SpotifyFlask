document.addEventListener('DOMContentLoaded', function () {
  const colorThief = new ColorThief();
  const playlistContainer = document.getElementById('playlist-container');

  playlistData.forEach(function (playlist) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = playlist.cover_art;

    img.onload = function () {
      const palette = colorThief.getPalette(img, 4); // Get the 5 most dominant colors

      let dominantColor = palette[0];
      for (let i = 0; i < palette.length; i++) {
        // A simple way to check if a color is "dark" is to check if all its RGB components are less than 85
        if (
          dominantColor[0] < 85 &&
          dominantColor[1] < 85 &&
          dominantColor[2] < 85
        ) {
          dominantColor = palette[i];
        } else {
          break;
        }
      }

      // Calculate the complementary color
      const complementaryColor = [
        255 - dominantColor[0],
        255 - dominantColor[1],
        255 - dominantColor[2],
      ];

      // Apply the animation to your element
      img.style.animation = `dynamicShadow 2s infinite`;
      img.style.animation = `sparkle 1s infinite`;

      // Define a golden yellow color for the box shadow
      const boxShadowColor = `rgba(${complementaryColor[0]}, ${complementaryColor[1]}, ${complementaryColor[2]}, 0.6)`; // RGB for golden yellow

      // Create the box shadow
      const boxShadow = `0 0 60px 0 ${boxShadowColor}, inset -100px 10px 80px 20px #080707, 0 0 40px 10px ${boxShadowColor}, inset 0 0 10px 0 ${boxShadowColor}`;

      // Add the new element to the playlist container
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
