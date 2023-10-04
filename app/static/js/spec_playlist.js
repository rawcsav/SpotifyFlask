$(document).ready(function () {
  const img = $('.playlist-cover')[0];
  if (img) {
    const colorThief = new ColorThief();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      const color = colorThief.getColor(img);

      const boxShadow = Array(5) // Create 5 layers of shadows for the aura effect
        .fill()
        .map(
          (_, index) =>
            `0 0 ${10 + index * 10}px ${10 + index * 5}px rgba(${color[0]}, ${
              color[1]
            }, ${color[2]}, 0.2)`,
        )
        .join(', ');

      img.style.boxShadow = boxShadow;
    };
    img.src = img.src; // Trigger the onload event
  }
  const artistContainers = $('.artist-container');

  // Loop over each container
  artistContainers.each(function (index, container) {
    const img = $(container).find('.artist-image')[0];
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      const colorThief = new ColorThief();
      const color = colorThief.getColor(img);

      const boxShadow = Array(5) // Create 5 layers of shadows for the aura effect
        .fill()
        .map(
          (_, index) =>
            `0 0 ${10 + index * 10}px ${10 + index * 5}px rgba(${color[0]}, ${
              color[1]
            }, ${color[2]}, 0.2)`,
        )
        .join(', ');

      container.style.boxShadow = boxShadow;
    };
    img.src = img.src; // Trigger the onload event
  });

  $('.data-view-btn').click(function () {
    var btnId = $(this).attr('id');

    var dataViewToShow;
    switch (btnId) {
      case 'summary-stats-btn':
        dataViewToShow = 'summary-stats';
        break;
      case 'genre-counts-btn':
        dataViewToShow = 'genre-counts';
        break;
      case 'feature-stats-btn':
        dataViewToShow = 'feature-stats';
        break;
    }

    $('.data-view').hide();

    // Show the selected data view
    $('#' + dataViewToShow).show();
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
      cutoutPercentage: 5, // Reduce the pie size slightly
      responsive: true,
      plugins: {
        title: {
          display: false,
          text: 'Distribution of Track Release Dates',
          fontSize: 16, // Optional: Adjust font size as needed
          align: 'center',
          position: 'bottom',
        },
        legend: {
          position: 'left', // Position the legend on the right side of the chart
          labels: {
            boxWidth: 10, // Optional: Adjust box width of the legend color boxes
            padding: 5, // Optional: Adjust padding between legend items
          },
        },
      },
    },
  });

  $('#like-all-songs-btn').click(function () {
    $.get('/like_all_songs/' + playlistId, function (response) {
      showToast(response); // Assumes a successful response message
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

    // Automatically hide the toast after 5 seconds
    setTimeout(() => {
      toast.style.display = 'none';
    }, 5000);
  }

  // Closing the toast when the 'X' is clicked
  document.querySelector('.close-toast').addEventListener('click', function () {
    this.parentElement.style.display = 'none';
  });
});
