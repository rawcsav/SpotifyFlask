$(document).ready(function () {
  // Load genres with error handling
  $.get("/genres", function (data) {
    let genres = JSON.parse(data)["genres"];
    let genreString = genres.join(", ");
    $("#genre_list").html(`<div class="genre-box">${genreString}</div>`);
  }).fail(function (jqXHR, textStatus, errorThrown) {
    console.error("Error:", textStatus, errorThrown);
  });

  // Submit form
  $("form").submit(function (event) {
    event.preventDefault();
    getRecommendations();
  });

  // Track Search with error handling and template literals
  $("#track_search").click(function () {
    let query = $("#track_input").val();
    $.ajax({
      url: "/search",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        query: query,
        type: "track",
      }),
      success: function (data) {
        let results = JSON.parse(data)["tracks"]["items"];
        $("#track_search_results").empty();
        results.forEach((result) => {
          $("#track_search_results").append(`
                        <div>
                            <h2>Track: ${result["name"]}</h2>
                            <p>Artist: ${result["artists"][0]["name"]}</p>
                            <p>Track ID: ${result["id"]}</p>
                        </div>
                    `);
        });
      },
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Error:", textStatus, errorThrown);
    });
  });

  // Artist Search with error handling and template literals
  $("#artist_search").click(function () {
    let query = $("#artist_input").val();
    $.ajax({
      url: "/search",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        query: query,
        type: "artist",
      }),
      success: function (data) {
        let results = JSON.parse(data)["artists"]["items"];
        $("#artist_search_results").empty();
        results.forEach((result) => {
          $("#artist_search_results").append(`
                        <div>
                            <h2>Artist: ${result["name"]}</h2>
                            <p>Artist ID: ${result["id"]}</p>
                        </div>
                    `);
        });
      },
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Error:", textStatus, errorThrown);
    });
  });

  // Initialize Sliders
  $("#popularity_slider")
    .slider({
      range: true,
      min: 0,
      max: 100,
      values: [0, 100],
      slide: function (event, ui) {
        $("#popularity_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "🤷 Who's that?")
    .attr("data-max", "🌟 Superstar!");

  $("#energy_slider")
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $("#energy_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "🐢 Chill vibes")
    .attr("data-max", "🚀 Blast off!");

  $("#instrumentalness_slider")
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $("#instrumentalness_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "🎤 Vocal party")
    .attr("data-max", "🎸 All instruments");

  $("#tempo_slider")
    .slider({
      range: true,
      min: 24,
      max: 208,
      values: [24, 208],
      slide: function (event, ui) {
        $("#tempo_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "🚶 Strolling pace")
    .attr("data-max", "🏃 Sprint mode");

  $("#danceability_slider")
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $("#danceability_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "🪑 Seat groove")
    .attr("data-max", "💃 Dance fever!");

  $("#valence_slider")
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $("#valence_input").val(ui.values[0] + "," + ui.values[1]);
      },
    })
    .attr("data-min", "☁️ Moody blues")
    .attr("data-max", "☀️ Sunshine joy");

  let currentPlayingAudio = null; // To keep track of the current playing audio element
  let currentPlayingButton = null; // To keep track of the current playing button
  function getRecommendations() {
    $.post("/get_recommendations", $("form").serialize(), function (data) {
      let recommendations = data["recommendations"];
      $("#results").empty();
      recommendations.forEach((trackInfo) => {
        let audioElement = new Audio(trackInfo["preview"]);
        $("#results").append(`



										<div class="result-item">
											<div class="result-cover-art-container">
												<img src="${trackInfo["cover_art"]}" alt="Cover Art" class="result-cover-art" id="cover_${trackInfo["trackid"]}">
													<div class="play-button" id="play_${trackInfo["trackid"]}">&#9654;</div>
												</div>
												<div class="result-text">
													<h2>
														<a href="${trackInfo["trackUrl"]}" target="_blank">${trackInfo["trackName"]}</a>
														<small>(${trackInfo["trackid"]})</small>
													</h2>
													<p>Artist: ${trackInfo["artist"]}


														<small>(${trackInfo["artistid"]})</small>
													</p>
													<p>Album: ${trackInfo["albumName"]}</p>
												</div>
												<audio controls>
													<source src="${trackInfo["preview"]}" type="audio/mpeg">
            Your browser does not support the audio element.



													</audio>
												</div>
      `);
        let playButton = $(`#play_${trackInfo["trackid"]}`);
        audioElement.addEventListener("play", function () {
          // Pause the current playing track, if any
          if (currentPlayingAudio && currentPlayingAudio !== audioElement) {
            currentPlayingAudio.pause();
            currentPlayingButton.html("&#9654;"); // Set previous button to play symbol
          }
          // Update the current playing audio and button
          currentPlayingAudio = audioElement;
          currentPlayingButton = playButton;
          playButton.html("&#9616;&#9616;"); // Set to pause symbol
        });
        audioElement.addEventListener("pause", function () {
          playButton.html("&#9654;"); // Set to play symbol
        });
        playButton.click(function () {
          if (audioElement.paused) {
            audioElement.play();
          } else {
            audioElement.pause();
          }
        });
      });
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Error:", textStatus, errorThrown);
    });
  }
});
