function toTitleCase(str) {
  return str.replace(/\w\S*/g, function (txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

function showGenreDetails(period, genre) {
  const topArtists = window.genreData[period][genre].top_artists;
  const topTracks = window.genreData[period][genre].top_tracks;

  document.getElementById("overlayGenreTitle").innerText = toTitleCase(genre);
  document.getElementById("overlayTimePeriod").innerText = `In ${toTitleCase(
    period.replace("_", " "),
  )}`;

  const artistsUl = document.getElementById("overlayTopArtists");
  artistsUl.innerHTML = topArtists
    .map((artist) => `<li>${artist.name}</li>`)
    .join("");

  const tracksUl = document.getElementById("overlayTopTracks");
  tracksUl.innerHTML = topTracks
    .map((track) => `<li>${track.name} by ${track.artists[0].name}</li>`)
    .join("");

  document.getElementById("genreOverlay").style.display = "flex";
}
function closeGenreOverlay() {
  document.getElementById("genreOverlay").style.display = "none";
}
