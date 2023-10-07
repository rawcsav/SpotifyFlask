$(document).ready(function () {
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
  var myPieChart = new Chart(ctx, {
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
    getPLRecommendations();
  });

  function getPLRecommendations() {
    $.post(
      `/get_pl_recommendations/${playlistId}/recommendations`,
      function (data) {
        let recommendations = data['recommendations'];
        if (recommendations.length > 0) {
          $('.recommendations-title').show();
        }
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
      },
    ).fail(function () {
      console.log('An error occurred while getting the recommendations.');
    });
  }

  $(document).on('click', '.add-to-playlist', function (event) {
    event.preventDefault();

    let trackId = $(this).attr('data-trackid');

    $.ajax({
      url: '/add_to_playlist',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ playlist_id: playlistId, track_id: trackId }),
      success: function (data) {
        // Display the toast message on successful addition
        showToast('Track added to playlist successfully!');
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
  });

  $(document).on('click', '.add-to-saved', function (event) {
    event.preventDefault();

    let trackId = $(this).attr('data-trackid');
    $.ajax({
      url: '/save_track',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ track_id: trackId }),
      success: function (data) {
        // Display the toast message on successful save
        showToast('Track saved successfully!');
      },
      error: function (jqXHR, textStatus, errorThrown) {
        // Display error toast
        showToast('An error occurred while saving the track.', 'error');
        console.error('Error:', textStatus, errorThrown);
      },
    });
  });
  $(document).on('click', '.heart-icon', function () {
    $(this).toggleClass('clicked');

    if ($(this).hasClass('clicked')) {
      // Change to filled heart
      $(this).removeClass('far fa-heart').addClass('fas fa-heart');
    } else {
      // Change to empty heart
      $(this).removeClass('fas fa-heart').addClass('far fa-heart');
    }
  });
  $(document).on('click', '.plus-icon', function () {
    $(this).toggleClass('clicked');
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
