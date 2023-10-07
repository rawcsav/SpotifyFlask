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
