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

  var modal = $('#instructionsModal');
  var closeBtn = $('.close');

  $('#showInstructions').click(function () {
    modal.css('display', 'block');
  });

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
  $('#showInstructions').on('click', function () {
    $('#instructionsModal').fadeIn();
    $('body').css('overflow', 'hidden');
  });

  $('.close').on('click', function () {
    $('#instructionsModal').fadeOut();
    $('body').css('overflow', 'auto');
  });

  $(window).on('click', function (event) {
    if ($(event.target).is('#instructionsModal')) {
      $('#instructionsModal').fadeOut();
      $('body').css('overflow', 'auto');
    }
  });

  $('#universal_search').click(function () {
    let query = $('#universal_input').val();
    $('#universal_search_results').empty();
    $('#universal_loading').show();
    $('#universal_error').hide();
    $.ajax({
      url: '/search',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        query: query,
        type: 'track,artist',
      }),
      success: function (data) {
        $('#universal_loading').hide();
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
        $('#universal_error').show();
        $('#universal_loading').hide();
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
      let seedType = $(this).hasClass('track') ? 'track' : 'artist';
      $('#universal_seeds_container').append(
        $(this).clone().addClass(seedType),
      );
      updateSeedsInput('universal_seeds_container');
    } else {
      alert('You can select no more than 5 combined seeds.');
    }
  });

  $('#universal_seeds_container').on('click', '.clickable-result', function () {
    let seedType = $(this).hasClass('track') ? 'track' : 'artist';
    $(this).remove();
    updateSeedsInput('universal_seeds_container');
  });

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

  let currentPlayingAudio = null;
  let currentPlayingButton = null;
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
        let trackName = $(this).attr('data-name');
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
        let artistName = $(this).attr('data-artist');
        let artistId = $(this).attr('data-artistid');
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
                            <a href="#" class="add-to-saved" data-trackid="${trackInfo['trackid']}">
                                <i class="far fa-heart heart-icon"></i>
                            </a>
                            <a href="#" class="add-to-playlist" data-trackid="${trackInfo['trackid']}">
                                <i class="plus-icon fas fa-plus plus-icon-grey"></i>
                            </a>
                            <div class="add-to-seeds-dropdown">
                              <a href="#" class="add-to-seeds-toggle" data-trackid="${trackInfo['trackid']}" data-artistid="${trackInfo['artistid']}">
                                <i class="fas fa-seedling seed-icon"></i>
                              </a>
                              <div class="seeds-options">
                                <a href="#" class="add-to-seeds track" data-trackid="${trackInfo['trackid']}" data-name="${trackInfo['trackName']}" data-artist="${trackInfo['artist']}">Add Track to Seeds</a>
                                <a href="#" class="add-to-seeds artist" data-artistid="${trackInfo['artistid']}" data-artist="${trackInfo['artist']}">Add Artist to Seeds</a>
                              </div>
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
            currentPlayingButton.html('&#9654;');
          }
          currentPlayingAudio = audioElement;
          currentPlayingButton = playButton;
          playButton.html('&#9616;&#9616;');
        });
        audioElement.addEventListener('pause', function () {
          playButton.html('&#9654;');
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

  let buttonOffset = button.offset();
  toast.css({
    top: buttonOffset.top,
    left: buttonOffset.left,
  });

  toast.text(message).fadeIn(400).delay(2000).fadeOut(1000);
}

$(document).on('click', '.add-to-saved', function (event) {
  event.preventDefault();

  let heartIcon = $(this).find('.heart-icon');
  let trackId = $(this).attr('data-trackid');
  let button = $(this);

  if (heartIcon.hasClass('fas fa-heart')) {
    $.ajax({
      url: '/unsave_track',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ track_id: trackId }),
      success: function (data) {
        showToast(button, 'Track unsaved successfully!');

        heartIcon.removeClass('fas fa-heart liked').addClass('far fa-heart');
      },
      error: function (jqXHR, textStatus, errorThrown) {
        showToast(
          button,
          'An error occurred while unsaving the track.',
          'error',
        );
        console.error('Error:', textStatus, errorThrown);
      },
    });
  } else {
    $.ajax({
      url: '/save_track',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ track_id: trackId }),
      success: function (data) {
        showToast(button, 'Track saved successfully!');

        heartIcon.removeClass('far fa-heart').addClass('fas fa-heart liked');
      },
      error: function (jqXHR, textStatus, errorThrown) {
        showToast(button, 'An error occurred while saving the track.');
        console.error('Error:', textStatus, errorThrown);
      },
    });
  }
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

  let plusIcon = $(this).find('.plus-icon');
  let playlistId = $(this).attr('data-playlistid');
  let modal = $('#playlistModal');
  let trackId = modal.data('trackid');

  let button = modal.data('button');

  $.ajax({
    url: '/add_to_playlist',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ track_id: trackId, playlist_id: playlistId }),
    success: function (data) {
      showToast(button, 'Added to Playlist!');
      modal.css('display', 'none');
      plusIcon.removeClass('plus-icon-grey').addClass('plus-icon-green');
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

$(document).on('click', '.add-to-seeds-toggle', function (event) {
  event.preventDefault();
  $(this).next('.seeds-options').toggle();
});

$(window).click(function (event) {
  if (!$(event.target).closest('.add-to-seeds-dropdown').length) {
    $('.seeds-options').hide();
  }
});

function updateSvgContainerHeight() {
  const bodyHeight = document.body.scrollHeight; // Get the full scroll height of the body
  const svgContainer = document.querySelector('.svg-container');
  svgContainer.style.height = `${bodyHeight}px`; // Update the container height
}

document.addEventListener('DOMContentLoaded', function () {
  var toggleButton = document.getElementById('toggleButton');
  var formContainer = document.querySelector('.form-container');
  var searchContainer = document.querySelector('.search-container');
  var seedsContainer = document.querySelector('.seed-container'); // Add this line

  var isFormVisible = false; // The form is not visible by default
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
    { class: 'svg1', x: '10%', y: '4%' },
    { class: 'svg2', x: '80%', y: '10%' },
    { class: 'svg3', x: '65%', y: '1%' },
    { class: 'svg4', x: '1%', y: '27%' },
    { class: 'svg5', x: '91%', y: '30%' },
    { class: 'svg6', x: '3%', y: '53%' },
    { class: 'svg7', x: '85%', y: '60%' },
    { class: 'svg8', x: '30%', y: '70%' },
    { class: 'svg9', x: '50%', y: '75%' },
    { class: 'svg10', x: '39%', y: '6%' },
    { class: 'svg11', x: '73%', y: '81%' },
    { class: 'svg12', x: '15%', y: '80%' },
  ];

  const selectedPositions = svgPositions
    .sort(() => 0.5 - Math.random())
    .slice(0, 12);

  document.body.style.position = 'relative';
  document.body.style.overflowX = 'hidden'; // Prevent horizontal scrolling
  document.body.style.margin = '0'; // Remove default margin

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

  toggleButton.addEventListener('click', function () {
    // Check if the viewport width is less than or equal to 620px
    if (window.innerWidth <= 1024) {
      if (isFormVisible) {
        formContainer.style.display = 'none';
        searchContainer.style.display = 'flex'; // Adjust according to your layout
        seedsContainer.style.display = 'flex'; // Show seeds container - adjust if needed
      } else {
        formContainer.style.display = 'flex'; // Adjust according to your layout
        searchContainer.style.display = 'none';
        seedsContainer.style.display = 'none'; // Hide seeds container
      }
      isFormVisible = !isFormVisible;
    }
  });

  // Optional: Add a resize event listener to handle cases when the window is resized across the 620px threshold
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1024) {
      // If the viewport is wider than 620px, ensure both containers are visible
      formContainer.style.display = 'flex';
      searchContainer.style.display = 'flex';
      seedsContainer.style.display = 'flex'; // Show seeds container - adjust if needed
    } else {
      // If the viewport is 620px or less, apply the visibility based on the isFormVisible flag
      if (isFormVisible) {
        formContainer.style.display = 'flex';
        searchContainer.style.display = 'none';
        seedsContainer.style.display = 'none'; // Hide seeds container
      } else {
        formContainer.style.display = 'none';
        searchContainer.style.display = 'flex';
        seedsContainer.style.display = 'flex'; // Show seeds container - adjust if needed
      }
    }
  });
});
