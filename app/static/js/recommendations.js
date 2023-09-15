$(document).ready(function () {
  // Get the modal and close button
  var modal = $("#instructionsModal");
  var closeBtn = $(".close");

  // Show the modal when the button is clicked
  $("#showInstructions").click(function () {
    modal.css("display", "block");
  });

  // Hide the modal when the close button (×) is clicked
  closeBtn.click(function () {
    modal.css("display", "none");
  });

  $(window).click(function (event) {
    if ($(event.target).is(modal)) {
      modal.css("display", "none");
    }
  });
});

$(document).ready(function () {
  // Modal behavior
  $("#showInstructions").on("click", function () {
    $("#instructionsModal").fadeIn();
    $("body").css("overflow", "hidden"); // Prevent background scrolling
  });

  $(".close").on("click", function () {
    $("#instructionsModal").fadeOut();
    $("body").css("overflow", "auto"); // Allow scrolling again
  });

  $(window).on("click", function (event) {
    if ($(event.target).is("#instructionsModal")) {
      $("#instructionsModal").fadeOut();
      $("body").css("overflow", "auto"); // Allow scrolling again
    }
  });

  // Genre search behavior
  $("#genre_search").click(function () {
    let query = $("#genre_input").val();
    searchGenres(query);
  });

  function searchGenres(query) {
    $("#genre_search_results").empty(); // Clear the previous search results
    $("#genre_loading").show(); // Show the loading message
    $("#genre_error").hide(); // Hide any previous error message
    $.ajax({
      url: "/genres", // Update the endpoint URL as per your Flask route
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ query: query }),
      success: function (data) {
        $("#genre_loading").hide(); // Hide the loading message when data is received

        let results = JSON.parse(data)["genres"];
        $("#genre_search_results").empty();

        results.forEach((genre) => {
          $("#genre_search_results").append(
            `<div class="clickable-genre">${genre}</div>`,
          );
        });
      },
      fail: function (jqXHR, textStatus, errorThrown) {
        $("#genre_error").show(); // Show the error message
        $("#genre_loading").hide(); // Hide the loading message
        console.error("Error:", textStatus, errorThrown);
      },
    });
  }

  $("#genre_input").on("keypress", function (e) {
    if (e.which == 13) {
      let query = $(this).val();
      searchGenres(query);
    }
  });

  // Track Search with error handling and template literals
  $("#track_search").click(function () {
    let query = $("#track_input").val();
    $("#track_search_results").empty(); // Clear the previous search results
    $("#track_loading").show(); // Show the loading message
    $("#track_error").hide(); // Hide any previous error message
    $.ajax({
      url: "/search",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        query: query,
        type: "track",
      }),
      success: function (data) {
        $("#track_loading").hide(); // Hide the loading message when data is received

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
      fail: function (jqXHR, textStatus, errorThrown) {
        $("#track_error").show(); // Show the error message
        $("#track_loading").hide(); // Hide the loading message
        console.error("Error:", textStatus, errorThrown);
      },
    });
  });

  $("#track_input").on("keypress", function (e) {
    if (e.which == 13) {
      let query = $(this).val();
      // Trigger the click event for the track search button to initiate the search
      $("#track_search").trigger("click");
    }
  });

  // Artist Search with error handling and template literals
  $("#artist_search").click(function () {
    let query = $("#artist_input").val();
    $("#artist_search_results").empty(); // Clear the previous search results
    $("#artist_loading").show(); // Show the loading message
    $("#artist_error").hide(); // Hide any previous error message
    $.ajax({
      url: "/search",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        query: query,
        type: "artist",
      }),
      success: function (data) {
        $("#artist_loading").hide(); // Hide the loading message when data is received

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
      fail: function (jqXHR, textStatus, errorThrown) {
        $("#artist_error").show(); // Show the error message
        $("#artist_loading").hide(); // Hide the loading message
        console.error("Error:", textStatus, errorThrown);
      },
    });
  });

  $("#artist_input").on("keypress", function (e) {
    if (e.which == 13) {
      let query = $(this).val();
      // Trigger the click event for the artist search button to initiate the search
      $("#artist_search").trigger("click");
    }
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

  // Submit form
  $("form").submit(function (event) {
    event.preventDefault();
    getRecommendations();
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

  $(document).on("click", ".add-seed", function () {
    let trackId = $(this).attr("data-trackid");
    if (getTotalSeeds() < 5) {
      let trackElement = $(`
            <div class="clickable-result" data-id="${trackId}">
                <img src="${$(this)
                  .closest(".result-item")
                  .find(".result-cover-art-container img")
                  .attr("src")}" alt="Cover Art" class="result-image">
                <div class="result-info">
                    <h2>${$(this)
                      .siblings(".result-text")
                      .find("a")
                      .text()}</h2>
                    <p>Artist: ${$(this)
                      .siblings(".result-text")
                      .find("p:first")
                      .text()
                      .replace("Artist: ", "")}</p>
                </div>
            </div>
        `);
      $("#track_seeds_container").append(trackElement);
      updateSeedsInput("track_seeds");
    } else {
      alert("You can select no more than 5 combined seeds.");
    }
  });

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
                        <div class="result-info-container">
                          <div class="result-text">
                            <h2>
                                <a href="${trackInfo["trackUrl"]}" target="_blank">${trackInfo["trackName"]}</a>
                            </h2>
                            <p>Artist: ${trackInfo["artist"]}</p>
                            <p>Album: ${trackInfo["albumName"]}</p>
                          </div>
                          <button class="add-seed" data-trackid="${trackInfo["trackid"]}">+</button>
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
