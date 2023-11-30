function toTitleCase(str) {
  return str.replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

function showGenreDetails(period, genre) {
  const topArtists = window.genreData[period][genre].top_artists;
  const topTracks = window.genreData[period][genre].top_tracks;

  document.getElementById('overlayGenreTitle').innerText = toTitleCase(genre);
  document.getElementById('overlayTimePeriod').innerText = `In ${toTitleCase(
    period.replace('_', ' '),
  )}`;

  const artistsUl = document.getElementById('overlayTopArtists');
  artistsUl.innerHTML = topArtists
    .map((artist) => `<li>${artist.name}</li>`)
    .join('');

  const tracksUl = document.getElementById('overlayTopTracks');
  tracksUl.innerHTML = topTracks
    .map((track) => `<li>${track.name} by ${track.artists[0].name}</li>`)
    .join('');

  document.getElementById('genreOverlay').style.display = 'flex';
}
function closeGenreOverlay() {
  document.getElementById('genreOverlay').style.display = 'none';
}

function updateSvgContainerHeight() {
  const bodyHeight = document.body.scrollHeight; // Get the full scroll height of the body
  const svgContainer = document.querySelector('.svg-container');
  svgContainer.style.height = `${bodyHeight}px`; // Update the container height
}

document.addEventListener('DOMContentLoaded', function () {
  const svgUrls = [
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/3673dcf5-01e4-43d2-ac71-ed04a7b56b34',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/amp',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/cd',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/clarinet',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/domra',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/drums_jsuiqf',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/f9cca628-b87a-4880-b2b3-a38e94b48d6f',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/grammy-svgrepo-com',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/gramophone',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/guitar_vqh6f4',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/headphone_xshl0v',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/headphones_mmy6gf',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_1',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_2',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_3',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_30',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_33',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_35',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_36',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_4',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_5',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_6',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano_hzttv3',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/radio-svgrepo-com',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/shape',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/speaker',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/trombone',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/vinyl_z1naey',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/wave_anpgln',
    'http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/xylophone',
  ];

  const svgPositions = [
    { class: 'svg1', x: '15%', y: '2%' },
    { class: 'svg2', x: '80%', y: '0%' },
    { class: 'svg3', x: '60%', y: '6%' },
    { class: 'svg4', x: '1%', y: '27%' },
    { class: 'svg5', x: '95%', y: '30%' },
    { class: 'svg6', x: '3%', y: '53%' },
    { class: 'svg7', x: '93%', y: '60%' },
    { class: 'svg8', x: '26%', y: '88%' },
    { class: 'svg9', x: '50%', y: '89%' },
    { class: 'svg10', x: '39%', y: '1%' },
    { class: 'svg11', x: '92%', y: '87%' },
    { class: 'svg12', x: '15%', y: '87%' },
  ];

  const selectedPositions = svgPositions
    .sort(() => 0.5 - Math.random())
    .slice(0, 12);

  // Create a container for the SVG images
  const svgContainer = document.createElement('div');
  svgContainer.classList.add('svg-container'); // Add the class for the query selector
  svgContainer.style.position = 'absolute'; // Change to absolute to scroll with content
  svgContainer.style.width = '100%';
  // Initial height will be set by updateSvgContainerHeight function
  svgContainer.style.top = '0';
  svgContainer.style.left = '0';
  svgContainer.style.zIndex = '-1'; // Ensure it's behind all other content
  svgContainer.style.overflow = 'hidden'; // Prevent scrollbars if SVGs overflow
  document.body.prepend(svgContainer); // Insert it as the first child of body

  svgContainer
    .querySelectorAll('.svg-placeholder')
    .forEach((el) => el.remove());

  // Create and append SVG images to the svgContainer
  selectedPositions.forEach((position, index) => {
    const svgImage = document.createElement('img');
    svgImage.src = svgUrls[index % svgUrls.length]; // Cycle through SVG URLs
    svgImage.classList.add('svg-placeholder', position.class);
    svgImage.style.position = 'absolute';
    svgImage.style.left = position.x;
    svgImage.style.top = position.y;
    svgContainer.appendChild(svgImage);
  });
  updateSvgContainerHeight();
  window.addEventListener('resize', updateSvgContainerHeight);
});
