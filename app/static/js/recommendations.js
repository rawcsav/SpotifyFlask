$(document).ready(function () {
  $("#genre_label_container").click(function () {
    $("#genre_list").toggle();
  });

  $.get("/genres", function (data) {
    let genres = JSON.parse(data)["genres"];
    let genreHTML = genres
      .map((genre) => `<span class="clickable-genre">${genre}</span>`)
      .join(", ");
    $("#genre_list").html(`<div class="genre-box">${genreHTML}</div>`);
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
                        <div class="clickable-result" data-id="${result["id"]}">
                            <img src="${result["album"]["images"][0]["url"]}" alt="Cover Art" class="result-image">
                            <div class="result-info">
                                <h2>${result["name"]}</h2>
                                <p>${result["artists"][0]["name"]}</p>
                            </div>
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
                        <div class="clickable-result" data-id="${result["id"]}">
                            <img src="${result["images"][0]["url"]}" alt="${result["name"]}" class="result-image">
                            <div class="result-info">
                                <h2>${result["name"]}</h2>
                            </div>
                        </div>
                    `);
        });
      },
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Error:", textStatus, errorThrown);
    });
  });

  function getTotalSeeds() {
    let trackSeeds = $("#track_seeds_container .clickable-result").length;
    let artistSeeds = $("#artist_seeds_container .clickable-result").length;
    let genreSeeds = $("#genre_seeds_container .genre-seed").length;
    return trackSeeds + artistSeeds + genreSeeds;
  }
  // For track selection:
  $("#track_search_results").on("click", ".clickable-result", function () {
    if (getTotalSeeds() < 5) {
      $("#track_seeds_container").append($(this).clone());
      updateSeedsInput("track_seeds");
    } else {
      alert("You can select no more than 5 combined seeds.");
    }
  });

  // For artist selection:
  $("#artist_search_results").on("click", ".clickable-result", function () {
    if (getTotalSeeds() < 5) {
      $("#artist_seeds_container").append($(this).clone());
      updateSeedsInput("artist_seeds");
    } else {
      alert("You can select no more than 5 combined seeds.");
    }
  });

  // For genre selection:
  $(document).on("click", ".clickable-genre", function () {
    if (getTotalSeeds() < 5) {
      let genre = $(this).text();
      let newGenreElement = $(`<div class="genre-seed">${genre}</div>`);
      $("#genre_seeds_container").append(newGenreElement);
      updateSeedsInput("genre_seeds");
    } else {
      alert("You can select no more than 5 combined seeds.");
    }
  });

  function updateSeedsInput(inputId) {
    let ids = [];
    if (inputId === "genre_seeds") {
      $(`#${inputId}_container .genre-seed`).each(function () {
        ids.push($(this).text());
      });
    } else {
      $(`#${inputId}_container .clickable-result`).each(function () {
        ids.push($(this).attr("data-id"));
      });
    }
    $(`#${inputId}`).val(ids.join(","));
  }

  // For removing track seeds:
  $("#track_seeds_container").on("click", ".clickable-result", function () {
    $(this).remove();
    updateSeedsInput("track_seeds");
  });

  // For removing artist seeds:
  $("#artist_seeds_container").on("click", ".clickable-result", function () {
    $(this).remove();
    updateSeedsInput("artist_seeds");
  });

  // For removing genre seeds:
  $("#genre_seeds_container").on("click", ".genre-seed", function () {
    $(this).remove();
    updateSeedsInput("genre_seeds");
  });

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
  // Function to fetch recommendations
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
                            <p>Artist: ${trackInfo["artist"]}<small>(${trackInfo["artistid"]})</small></p>
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
          if (currentPlayingAudio && currentPlayingAudio !== audioElement) {
            currentPlayingAudio.pause();
            currentPlayingButton.html("&#9654;"); // Set previous button to play symbol
          }
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
