$(document).ready(function () {
  $('#playlistOptions').empty();
  playlistData.forEach(function (playlist) {
    $('#playlistOptions')
      .append(`<a href="#" class="playlist-option" data-playlistid="${playlist.id}">
                  <div class="playlist-item">
                    <img src="${playlist.cover_art}" alt="${playlist.name}" class="playlist-image">
                    <span class="playlist-name">${playlist.name}</span>
                  </div>
                </a>`);
  });

  // Get the modal and close button
  var modal = $('#instructionsModal');
  var closeBtn = $('.close');

  // Show the modal when the button is clicked
  $('#showInstructions').click(function () {
    modal.css('display', 'block');
  });

  // Hide the modal when the close button (×) is clicked
  closeBtn.click(function () {
    modal.css('display', 'none');
  });

  $(window).click(function (event) {
    if ($(event.target).is(modal)) {
      modal.css('display', 'none');
    }
  });
});

$(document).ready(function () {
  // Modal behavior
  $('#showInstructions').on('click', function () {
    $('#instructionsModal').fadeIn();
    $('body').css('overflow', 'hidden'); // Prevent background scrolling
  });

  $('.close').on('click', function () {
    $('#instructionsModal').fadeOut();
    $('body').css('overflow', 'auto'); // Allow scrolling again
  });

  $(window).on('click', function (event) {
    if ($(event.target).is('#instructionsModal')) {
      $('#instructionsModal').fadeOut();
      $('body').css('overflow', 'auto'); // Allow scrolling again
    }
  });

  $('#universal_search').click(function () {
    let query = $('#universal_input').val();
    $('#universal_search_results').empty(); // Clear the previous search results
    $('#universal_loading').show(); // Show the loading message
    $('#universal_error').hide(); // Hide any previous error message

    $.ajax({
      url: '/search',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        query: query,
        type: 'track,artist', // Search for both tracks and artists
      }),
      success: function (data) {
        $('#universal_loading').hide(); // Hide the loading message when data is received

        let trackResults = JSON.parse(data)['tracks']['items'];
        let artistResults = JSON.parse(data)['artists']['items'];
        $('#universal_search_results').empty();

        trackResults.forEach((result) => {
          $('#universal_search_results').append(`
                  <div class="clickable-result track" data-id="${result['id']}">
                      <img src="${result['album']['images'][0]['url']}" alt="Cover Art" class="result-image">
                      <div class="result-info">
                          <h2>${result['name']}</h2>
                          <p>${result['artists'][0]['name']}</p>
                      </div>
                  </div>
              `);
        });
        // Append artist results
        artistResults.forEach((result) => {
          $('#universal_search_results').append(`
                  <div class="clickable-result artist" data-id="${result['id']}">
                      <img src="${result['images'][0]['url']}" alt="${result['name']}" class="result-image">
                      <div class="result-info">
                          <h2>${result['name']}</h2>
                      </div>
                  </div>
              `);
        });
      },
      fail: function (jqXHR, textStatus, errorThrown) {
        $('#universal_error').show(); // Show the error message
        $('#universal_loading').hide(); // Hide the loading message
        console.error('Error:', textStatus, errorThrown);
      },
    });
  });
  function updateSeedsInput(inputId) {
    let ids = [];
    let trackIds = [];
    let artistIds = [];

    $(`#${inputId} .clickable-result`).each(function () {
      ids.push($(this).attr('data-id'));
      if ($(this).hasClass('track')) {
        trackIds.push($(this).attr('data-id'));
      } else if ($(this).hasClass('artist')) {
        artistIds.push($(this).attr('data-id'));
      }
    });

    $(`#${inputId}`).val(ids.join(','));
    $('#track_seeds').val(trackIds.join(','));
    $('#artist_seeds').val(artistIds.join(','));
  }

  $('#universal_input').on('keypress', function (e) {
    if (e.which == 13) {
      let query = $(this).val();
      $('#universal_search').trigger('click');
    }
  });

  function getTotalSeeds() {
    return $('#universal_seeds_container .clickable-result').length;
  }

  $('#universal_search_results').on('click', '.clickable-result', function () {
    if (getTotalSeeds() < 5) {
      let seedType = $(this).hasClass('track') ? 'track' : 'artist'; // Determine the seed type
      $('#universal_seeds_container').append(
        $(this).clone().addClass(seedType),
      ); // Add the seed type as a class
      updateSeedsInput('universal_seeds_container');
    } else {
      alert('You can select no more than 5 combined seeds.');
    }
  });

  $(document).on('click', function (event) {
    if ($('#universal_search_results').children().length > 0) {
      if (!$(event.target).closest('#universal_search_results').length) {
        $('#universal_search_results').fadeOut(1000, function () {
          $(this).empty().show();
        });
      }
    }
  });

  // For removing track seeds:
  $('#universal_seeds_container').on('click', '.clickable-result', function () {
    let seedType = $(this).hasClass('track') ? 'track' : 'artist'; // Determine the seed type
    $(this).remove();
    updateSeedsInput('universal_seeds_container'); // Update the appropriate seeds input
  });

  // Submit form
  $('form').submit(function (event) {
    event.preventDefault();
    getRecommendations();
  });

  $('#popularity_slider')
    .slider({
      range: true,
      min: 0,
      max: 100,
      values: [0, 100],
      slide: function (event, ui) {
        $('#popularity_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', "🤷 Who's that?")
    .attr('data-max', '🌟 Superstar!');

  $('#energy_slider')
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $('#energy_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', '🐢 Chill vibes')
    .attr('data-max', '🚀 Blast off!');

  $('#instrumentalness_slider')
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $('#instrumentalness_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', '🎤 Vocal party')
    .attr('data-max', '🎸 All instruments');

  $('#tempo_slider')
    .slider({
      range: true,
      min: 24,
      max: 208,
      values: [24, 208],
      slide: function (event, ui) {
        $('#tempo_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', '🚶 Strolling pace')
    .attr('data-max', '🏃 Sprint mode');

  $('#danceability_slider')
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $('#danceability_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', '🪑 Seat groove')
    .attr('data-max', '💃 Dance fever!');

  $('#valence_slider')
    .slider({
      range: true,
      min: 0,
      max: 1,
      step: 0.01,
      values: [0, 1],
      slide: function (event, ui) {
        $('#valence_input').val(ui.values[0] + ',' + ui.values[1]);
      },
    })
    .attr('data-min', '☁️ Moody blues')
    .attr('data-max', '☀️ Sunshine joy');

  let currentPlayingAudio = null; // To keep track of the current playing audio element
  let currentPlayingButton = null; // To keep track of the current playing button

  $(document).on('click', '.add-to-seeds', function (event) {
    event.preventDefault();
    if (getTotalSeeds() < 5) {
      let trackId, trackName, artistName, artistId;
      let seedType = $(this).hasClass('track') ? 'track' : 'artist';
      let imgSrc = $(this)
        .closest('.result-item')
        .find('.result-cover-art-container img')
        .attr('src');

      if (seedType === 'track') {
        let trackId = $(this).attr('data-trackid');
        let trackName = $(this).attr('data-name'); // Get name from data attribute
        let artistName = $(this).attr('data-artist');
        seedElement = $(`
                <div class="clickable-result track" data-id="${trackId}">
                    <img src="${imgSrc}" alt="Cover Art" class="result-image">
                    <div class="result-info">
                        <h2>${trackName}</h2>
                        <p>${artistName}</p>
                    </div>
                </div>
            `);
      } else {
        let artistName = $(this).attr('data-artist'); // Get artist name from data attribute
        let artistId = $(this).attr('data-artistid'); // Get artist ID from data attribute
        seedElement = $(`
                <div class="clickable-result artist" data-id="${artistId}">
                    <img src="${imgSrc}" alt="Cover Art" class="result-image">
                    <div class="result-info">
                        <h2>${artistName}</h2>
                    </div>
                </div>
            `);
      }

      $('#universal_seeds_container').append(seedElement);
      updateSeedsInput('universal_seeds_container');
    } else {
      alert('You can select no more than 5 combined seeds.');
    }
  });

  function getRecommendations() {
    $.post('/get_recommendations', $('form').serialize(), function (data) {
      console.log($('form').serialize());

      let recommendations = data['recommendations'];
      $('#results').empty();
      recommendations.forEach((trackInfo) => {
        let audioElement = new Audio(trackInfo['preview']);
        $('#results').append(`
                  <div class="result-item">
                    <div class="result-cover-art-container">
                      <img src="${trackInfo['cover_art']}" alt="Cover Art" class="result-cover-art" id="cover_${trackInfo['trackid']}">
                      <div class="caption">
                        <h2>${trackInfo['trackName']}</h2>
                        <p>${trackInfo['artist']}</p>
                      </div>
                      <div class="play-button" id="play_${trackInfo['trackid']}">&#9654;</div>
                    </div>
                          <div class="dropdown-content">
                            <a href="#" class="add-to-saved" data-trackid="${trackInfo['trackid']}">Add to Liked</a>
                            <a href="#" class="add-to-playlist" data-trackid="${trackInfo['trackid']}">Add to Playlist</a>
                            <a href="#" class="add-to-seeds track" data-trackid="${trackInfo['trackid']}" data-name="${trackInfo['trackName']}" data-artist="${trackInfo['artist']}">Add Track to Seeds</a>
                            <a href="#" class="add-to-seeds artist" data-artistid="${trackInfo['artistid']}" data-artist="${trackInfo['artist']}">Add Artist to Seeds</a>
                          </div>
                      </div>
                      <audio controls>
                          <source src="${trackInfo['preview']}" type="audio/mpeg">
                          Your browser does not support the audio element.
                      </audio>
                  </div> 
                `);
        let playButton = $(`#play_${trackInfo['trackid']}`);
        playButton.addClass('noselect');

        audioElement.addEventListener('play', function () {
          if (currentPlayingAudio && currentPlayingAudio !== audioElement) {
            currentPlayingAudio.pause();
            currentPlayingButton.html('&#9654;'); // Set previous button to play symbol
          }
          currentPlayingAudio = audioElement;
          currentPlayingButton = playButton;
          playButton.html('&#9616;&#9616;'); // Set to pause symbol
        });
        audioElement.addEventListener('pause', function () {
          playButton.html('&#9654;'); // Set to play symbol
        });
        playButton.click(function () {
          if (audioElement.paused) {
            audioElement.play();
          } else {
            audioElement.pause();
          }
        });
      });
      document.querySelector('.results-container').scrollTop = 0;
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error('Error:', textStatus, errorThrown);
    });
  }
});

function showToast(button, message) {
  let toast = $('#toast');

  // Position the toast next to the button
  let buttonOffset = button.offset();
  toast.css({
    top: buttonOffset.top,
    left: buttonOffset.left,
  });

  toast.text(message).fadeIn(400).delay(2000).fadeOut(1000); // Show the toast
}
$(document).on('click', '.add-to-saved', function (event) {
  event.preventDefault();

  let button = $(this);

  let trackId = $(this).attr('data-trackid');
  $.ajax({
    url: '/save_track', // Update the endpoint URL as per your Flask route
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ track_id: trackId }),
    success: function (data) {
      showToast(button, 'Saved Sucessfully!');
    },
    fail: function (jqXHR, textStatus, errorThrown) {
      console.error('Error:', textStatus, errorThrown);
    },
  });
});

$(document).on('click', '.add-to-playlist', function (event) {
  event.preventDefault();

  let button = $(this);
  let trackId = $(this).attr('data-trackid');

  $('#playlistModal')
    .data('trackid', trackId)
    .data('button', button)
    .css('display', 'block');
});

$(document).on('click', '.playlist-option', function (event) {
  event.preventDefault();

  let playlistId = $(this).attr('data-playlistid');
  let modal = $('#playlistModal');
  let trackId = modal.data('trackid');

  // Retrieve the button element from the modal data
  let button = modal.data('button');

  $.ajax({
    url: '/add_to_playlist',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ track_id: trackId, playlist_id: playlistId }),
    success: function (data) {
      showToast(button, 'Added to Playlist!');
      modal.css('display', 'none');
    },
    fail: function (jqXHR, textStatus, errorThrown) {
      console.error('Error:', textStatus, errorThrown);
    },
  });
});

$('.close').click(function () {
  $('#playlistModal').css('display', 'none');
});

$(window).click(function (event) {
  if ($(event.target).is($('#playlistModal'))) {
    $('#playlistModal').css('display', 'none');
  }
});
