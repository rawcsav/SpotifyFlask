let artGenFetched = false;
var myPieChart;

document.addEventListener('themeToggled', function () {
  if (typeof myPieChart !== 'undefined') {
    let isDarkMode = document.body.classList.contains('dark-mode');
    let legendLabelColor = isDarkMode ? '#e9705a' : '#1c1d21';
    myPieChart.options.plugins.legend.labels.color = legendLabelColor;
    myPieChart.update();
  }
});

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toastMessage');

  toastMessage.textContent = message;

  if (type === 'error') {
    toast.classList.add('error');
    toast.classList.remove('success');
  } else {
    toast.classList.add('success');
    toast.classList.remove('error');
  }

  toast.style.display = 'block';

  setTimeout(() => {
    toast.style.display = 'none';
  }, 5000);
}

document.querySelector('.close-toast').addEventListener('click', function () {
  this.parentElement.style.display = 'none';
});

$(document).ready(function () {
  let recommendationsFetched = false;

  const colorThief = new ColorThief();

  const playlistCover = $('.playlist-cover')[0];
  if (playlistCover) {
    playlistCover.crossOrigin = 'anonymous';
    playlistCover.onload = function () {
      const palette = colorThief.getPalette(playlistCover, 4);
      let dominantColor = palette[0];
      for (let i = 0; i < palette.length; i++) {
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

      const complementaryColor = [
        255 - dominantColor[0],
        255 - dominantColor[1],
        255 - dominantColor[2],
      ];

      const boxShadowColor = `rgba(${complementaryColor[0]}, ${complementaryColor[1]}, ${complementaryColor[2]}, 0.3)`;

      const boxShadow = `0 0 60px 0 ${boxShadowColor}, inset -100px 10px 80px 20px #080707, 0 0 40px 10px ${boxShadowColor}, inset 0 0 10px 0 ${boxShadowColor}`;

      playlistCover.style.boxShadow = boxShadow;
    };
    playlistCover.src = playlistCover.src;
  }

  const artistContainers = $('.artist-container');

  $('.artist-image').each(function (index, artistImage) {
    if (artistImage) {
      artistImage.crossOrigin = 'anonymous';
      const src = artistImage.src;
      artistImage.src = '';
      artistImage.onload = function () {
        const palette = colorThief.getPalette(artistImage, 4);
        const dominantColor = palette[0];
        const dominantColorObj = tinycolor({
          r: dominantColor[0],
          g: dominantColor[1],
          b: dominantColor[2],
        });

        const color1 = dominantColorObj.lighten(10).toRgbString();
        const color2 = dominantColorObj.darken(10).toRgbString();
        const color3 = dominantColorObj.saturate(10).toRgbString();
        const color4 = dominantColorObj.desaturate(10).toRgbString();

        const boxShadow = `0 0 60px 0 ${color1}, inset -100px 10px 80px 20px ${color2}, 0 0 40px 10px ${color3}, inset 0 0 10px 0 ${color4}`;

        artistImage.style.boxShadow = boxShadow;
      };
      artistImage.src = src;
    } else {
      console.log('No artist image found in container', container);
    }
  });

  function toggleDivVisibility(selector) {
    var el = $(selector);
    if (el.css('display') === 'none') {
      el.css('display', 'block');
    } else {
      el.css('display', 'none');
    }
  }

  $('.data-view-btn').click(function () {
    $('.data-view-btn').removeClass('active');
    $(this).addClass('active');
    var btnId = $(this).attr('id');
    var dataViewToShow = btnId.replace('-btn', '');
    $('.data-view').hide();
    $('#' + dataViewToShow).show();
  });

  let labels = Object.keys(yearCountData);
  let data = Object.values(yearCountData);

  var ctx = document.getElementById('YrPieChart').getContext('2d');
  myPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
          ],
        },
      ],
    },
    options: {
      cutoutPercentage: 5,
      responsive: true,
      plugins: {
        title: {
          display: false,
          text: 'Distribution of Track Release Dates',
          fontSize: 16,
          align: 'center',
          position: 'bottom',
        },
        legend: {
          position: 'left',
          labels: {
            boxWidth: 10,
            padding: 5,
          },
        },
      },
    },
  });

  $('#like-all-songs-btn').click(function () {
    $.get('/like_all_songs/' + playlistId, function (response) {
      showToast(response);
    }).fail(function (error) {
      showToast('An error occurred while liking all songs.', 'error');
    });
  });

  $('#unlike-all-songs-btn').click(function () {
    $.get('/unlike_all_songs/' + playlistId, function (response) {
      showToast(response);
    }).fail(function (error) {
      showToast('An error occurred while unliking all songs.', 'error');
    });
  });

  $('#remove-duplicates-btn').click(function () {
    $.get('/remove_duplicates/' + playlistId, function (response) {
      showToast('Successfully removed duplicates.');
    }).fail(function (error) {
      showToast('An error occurred while removing duplicates.', 'error');
    });
  });

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
      } else {
        entry.target.classList.remove('animate');
      }
    });
  });

  $('.data-view').each(function (index, element) {
    observer.observe(element);
  });

  function reorderPlaylist(criterion) {
    $.ajax({
      type: 'POST',
      url: `/playlist/${playlistId}/reorder`,
      contentType: 'application/json',
      data: JSON.stringify({ sorting_criterion: criterion }),
      success: function (response) {
        if (response.status === 'Playlist reordered successfully') {
          showToast('Playlist reordered successfully.');
        } else {
          showToast('Failed to reorder playlist.', 'error');
        }
      },
      error: function (error) {
        showToast('An error occurred while reordering the playlist.', 'error');
      },
    });
  }
  function showReorderModal(callback) {
    $('#reorderModal').fadeIn();

    $('#confirmReorder')
      .off()
      .click(function () {
        $('#reorderModal').fadeOut();
        callback();
      });

    $('#cancelReorder')
      .off()
      .click(function () {
        $('#reorderModal').fadeOut();
      });
  }

  $('#order-desc-btn').click(function () {
    showReorderModal(function () {
      reorderPlaylist('Date Added - Descending');
    });
  });

  $('#order-asc-btn').click(function () {
    showReorderModal(function () {
      reorderPlaylist('Date Added - Ascending');
    });
  });

  $('#rd-asc-btn').click(function () {
    showReorderModal(function () {
      reorderPlaylist('Release Date - Ascending');
    });
  });

  $('#rd-desc-btn').click(function () {
    showReorderModal(function () {
      reorderPlaylist('Release Date - Descending');
    });
  });

  $('#shuffle-btn').click(function () {
    showReorderModal(function () {
      reorderPlaylist('Shuffle');
    });
  });

  let currentPlayingAudio = null;
  let currentPlayingButton = null;

  $('#recommendations-btn').click(function (event) {
    event.preventDefault();
    if (!recommendationsFetched) {
      getPLRecommendations();
      recommendationsFetched = true;
    } else {
      toggleDivVisibility('.results-title-spot');
    }
  });

  function getPLRecommendations() {
    $.post(
      `/get_pl_recommendations/${playlistId}/recommendations`,
      function (data) {
        let recommendations = data['recommendations'];
        const customLine = '<div class="custom-line"></div>';
        const title = '<h2 id="recommendations-title">Recommendations</h2>';
        $('.results-title-spot').prepend(title); // Append the title to the results-title-spot div
        $('.results-title-spot').css('display', 'block'); // Display the results-title-spot div
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
                      <i class="fas fa-plus plus-icon"></i>
                  </a>
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

        // Append the custom line
        $('.results-title-spot').append(customLine);
      },
    ).fail(function () {
      console.log('An error occurred while getting the recommendations.');
    });
  }

  $(document).on('click', '.add-to-playlist', function (event) {
    event.preventDefault();

    let plusIcon = $(this).find('.plus-icon');
    let trackId = $(this).attr('data-trackid');

    if (plusIcon.hasClass('fas fa-minus')) {
      // The track is already added, remove it
      $.ajax({
        url: '/remove_from_playlist',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ playlist_id: playlistId, track_id: trackId }),
        success: function (data) {
          // Display the toast message on successful removal
          showToast('Track removed from playlist successfully!');

          // Change to plus icon
          plusIcon.removeClass('fas fa-minus added').addClass('fas fa-plus');
        },
        error: function (jqXHR, textStatus, errorThrown) {
          // Display error toast
          showToast(
            'An error occurred while removing the track from the playlist.',
            'error',
          );
          console.error('Error:', textStatus, errorThrown);
        },
      });
    } else {
      // The track is not added yet, add it
      $.ajax({
        url: '/add_to_playlist',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ playlist_id: playlistId, track_id: trackId }),
        success: function (data) {
          // Display the toast message on successful addition
          showToast('Track added to playlist successfully!');

          // Change to minus icon
          plusIcon.removeClass('fas fa-plus').addClass('fas fa-minus added');
        },
        error: function (jqXHR, textStatus, errorThrown) {
          // Display error toast
          showToast(
            'An error occurred while adding the track to the playlist.',
            'error',
          );
          console.error('Error:', textStatus, errorThrown);
        },
      });
    }
  });

  $(document).on('click', '.add-to-saved', function (event) {
    event.preventDefault();

    let heartIcon = $(this).find('.heart-icon');
    let trackId = $(this).attr('data-trackid');

    if (heartIcon.hasClass('fas fa-heart')) {
      $.ajax({
        url: '/unsave_track',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ track_id: trackId }),
        success: function (data) {
          // Display the toast message on successful unsave
          showToast('Track unsaved successfully!');

          // Change to empty heart
          heartIcon.removeClass('fas fa-heart liked').addClass('far fa-heart');
        },
        error: function (jqXHR, textStatus, errorThrown) {
          // Display error toast
          showToast('An error occurred while unsaving the track.', 'error');
          console.error('Error:', textStatus, errorThrown);
        },
      });
    } else {
      // The track is not saved yet, save it
      $.ajax({
        url: '/save_track',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ track_id: trackId }),
        success: function (data) {
          // Display the toast message on successful save
          showToast('Track saved successfully!');

          // Change to filled heart
          heartIcon.removeClass('far fa-heart').addClass('fas fa-heart liked');
        },
        error: function (jqXHR, textStatus, errorThrown) {
          // Display error toast
          showToast('An error occurred while saving the track.', 'error');
          console.error('Error:', textStatus, errorThrown);
        },
      });
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
  let genreItems = document.querySelectorAll('#genre-counts > ul > li');
  genreItems.forEach((item) => {
    item.addEventListener('click', function () {
      let artistList = item.querySelector('.artist-genre-list');
      if (
        artistList.style.display === 'none' ||
        artistList.style.display === ''
      ) {
        artistList.style.display = 'block';
      } else {
        artistList.style.display = 'none';
      }
    });
  });
});

document.getElementById('apiKeyForm').onsubmit = function (e) {
  e.preventDefault(); // Prevent form from being submitted normally
  var apiKey = document.getElementById('apiKey').value;
  console.log('API Key: ' + apiKey); // Just for testing
  document.getElementById('connect-button').style.display = 'block';
  document.getElementById('apiKeyForm').style.display = 'none';
};

function showArtGenContainer() {
  var artGenContainer = document.querySelector('.artist-gen-container');

  if (!artGenFetched) {
    const title =
      '<h2 id="art-gen-title" style="text-align: center;">Cover Art Gen</h2>';

    // Insert the title at the beginning of the art gen container
    artGenContainer.innerHTML = title + artGenContainer.innerHTML;

    artGenFetched = true;

    // Display the container
    artGenContainer.style.display = 'flex';

    // Check for the API key when the container is shown
    $.get('/check-api-key', function (response) {
      if (response.has_key) {
        // User has an existing API key, hide the connect-button and show the "Update API Key" text
        document.getElementById('connect-button').style.display = 'none';
        document.getElementById('update-button').style.display = 'block';
        document.getElementById('generate-art-btn').style.display = 'block';
        document.getElementById('gen-refresh-icon').style.display = 'block';
      } else {
        // User does not have an API key, show the connect-button and hide the "Update API Key" text
        document.getElementById('connect-button').style.display = 'block';
        document.getElementById('update-button').style.display = 'none';
      }
    }).fail(function (error) {
      console.error('Error checking API key:', error);
    });
  } else {
    // For subsequent clicks, simply toggle the visibility
    if (
      artGenContainer.style.display === 'none' ||
      artGenContainer.style.display === ''
    ) {
      artGenContainer.style.display = 'flex';
    } else {
      artGenContainer.style.display = 'none';
    }
  }
}

function handleApiKeySubmit(e) {
  e.preventDefault(); // Prevent form from being submitted normally

  var apiKey = document.getElementById('apiKey').value;

  $.ajax({
    url: '/save-api-key',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ api_key: apiKey }),
    success: function (response) {
      document.getElementById('update-button').style.display = 'block'; // Show the update-button
      document.getElementById('connect-button').style.display = 'none'; // Hide the connect-button
      document.getElementById('apiKeyForm').style.display = 'none';
      document.getElementById('generate-art-btn').style.display = 'block';
      document.getElementById('gen-refresh-icon').style.display = 'block';

      // Display a success toast
      showToast('API Key saved successfully!');
    },
    error: function (error) {
      console.error('Error saving API key:', error);

      // Display an error toast
      showToast('An error occurred while saving the API key.', 'error');
    },
  });
}

// Function to display Input Field
function displayInputField(event) {
  event.preventDefault(); // Prevent the default link behavior

  $.get('/check-api-key', function (response) {
    if (response.has_key) {
      // User has an existing API key, display the "Update API Key" text
      document.getElementById('connect-button').style.display = 'none';
      document.getElementById('update-button').style.display = 'block'; // This is the new "Update API Key" text
      document.getElementById('apiKeyForm').style.display = 'none';
      document.getElementById('generate-art-btn').style.display = 'block';
      document.getElementById('gen-refresh-icon').style.display = 'block';
    } else {
      // User does not have an API key, show the input form and hide the "Update API Key" text
      document.getElementById('connect-button').style.display = 'none';
      document.getElementById('update-button').style.display = 'none';
      document.getElementById('apiKeyForm').style.display = 'flex';
      document.getElementById('generate-art-btn').style.display = 'none';
      document.getElementById('gen-refresh-icon').style.display = 'none';
    }
  }).fail(function (error) {
    console.error('Error checking API key:', error);
  });
}

function showKeyFormAndHideUpdateButton() {
  // Hide the update-button
  document.getElementById('update-button').style.display = 'none';

  // Hide the Generate Art button
  document.getElementById('generate-art-btn').style.display = 'none';
  document.getElementById('gen-refresh-icon').style.display = 'none';

  // Display the API key form
  document.getElementById('apiKeyForm').style.display = 'flex';
}

function generateArtForPlaylist(input, isPrompt = false) {
  window.isArtGenerationRequest = true;

  // Show loading animation for 45 seconds
  window.showLoading(45000);

  // Define the data payload
  let dataPayload = {};
  if (isPrompt) {
    dataPayload = { prompt: input };
  } else if (input) {
    dataPayload = { genre_name: input };
  }

  console.log('Sending payload:', dataPayload); // Add this log

  $.ajax({
    url: `/generate_images/${playlistId}`,
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(dataPayload),
    success: function (response) {
      const images = response.images;
      const prompt = response.prompt;

      // Hide loading animation
      window.hideLoading();

      displayImages(response);

      // Reset the flag
      window.isArtGenerationRequest = false;

      showToast('Image generated successfully.');
    },
    error: function (error) {
      console.error('Error generating images:', error);

      // Hide loading animation
      window.hideLoading();

      // Reset the flag
      window.isArtGenerationRequest = false;

      // Show error toast
      showToast('An error occurred while generating the image.', 'error');
    },
  });
}

function refreshArt() {
  if (lastPromptUsed) {
    generateArtForPlaylist(lastPromptUsed, true); // Assuming you've made changes to accept a prompt as mentioned in the previous answer
  } else {
    console.warn('No last prompt found. Cannot refresh images.');
  }
}

let lastPromptUsed = null;

function displayImages(response) {
  const artInfoContainer = document.getElementById('art-info-container');
  const imageContainer = document.getElementById('art-gen-results');
  const images = response.images;
  const promptText = response.prompt;

  lastPromptUsed = promptText;
  console.log('Saved prompt:', lastPromptUsed);
  // Clear previous images
  while (imageContainer.firstChild) {
    imageContainer.removeChild(imageContainer.firstChild);
  }

  // Check and remove existing prompt
  const existingPrompt = document.querySelector('.art-gen-prompt');
  if (existingPrompt) {
    artInfoContainer.removeChild(existingPrompt);
  }

  // Display the prompt at the top
  const promptDiv = document.createElement('div');
  promptDiv.className = 'art-gen-prompt';
  promptDiv.textContent = promptText;
  artInfoContainer.insertBefore(promptDiv, imageContainer);

  images.forEach((imageUrl) => {
    // Create a new div for each image
    const imageDiv = document.createElement('div');
    imageDiv.className = 'art-gen-img-div';

    // Create the image
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = 'Generated Cover Art';
    img.className = 'art-gen-img';

    // Create a div for the icons
    const iconDiv = document.createElement('div');
    iconDiv.className = 'art-gen-icon-div';

    // Define the downloadIcon
    const downloadIcon = document.createElement('i');
    downloadIcon.className = 'fas fa-download';
    downloadIcon.title = 'Download image';

    const addPlaylistIcon = document.createElement('i');
    addPlaylistIcon.className = 'fas fa-plus fa-cover';
    addPlaylistIcon.title = 'Add to playlist';

    // Append the icons to the icon div
    iconDiv.appendChild(downloadIcon);
    iconDiv.appendChild(addPlaylistIcon);

    // Append the image and icon div to the image div
    imageDiv.appendChild(img);
    imageDiv.appendChild(iconDiv);

    // Append the image div to the container
    imageContainer.appendChild(imageDiv);

    // Check if there are any images
    if (images.length > 0) {
      // If there are images, set opacity to 1 and cursor to pointer
      document.getElementById('gen-refresh-icon').style.opacity = '1';
      document.getElementById('gen-refresh-icon').style.cursor = 'pointer';
    }
  });
}
