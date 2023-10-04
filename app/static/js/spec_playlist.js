$(document).ready(function () {
  const img = $('.playlist-cover')[0];
  if (img) {
    const colorThief = new ColorThief();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      const color = colorThief.getColor(img);
      const boxShadow = Array(3)
        .fill()
        .map(
          (_, index) =>
            `0 0 ${10 + index * 5}px ${10 + index * 10}px rgba(${color[0]}, ${
              color[1]
            }, ${color[2]}, 0.2)`,
        )
        .join(', ');

      img.style.boxShadow = boxShadow;
    };
    img.src = img.src;
  }

  const artistContainers = $('.artist-container');

  artistContainers.each(function (index, container) {
    const img = $(container).find('.artist-image')[0];
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      const colorThief = new ColorThief();
      const color = colorThief.getColor(img);
      const boxShadow = Array(5)
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
    img.src = img.src;
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
      // If the element is in the viewport
      if (entry.isIntersecting) {
        // Add a class to animate the element
        entry.target.classList.add('animate');
      } else {
        // If the element is not in the viewport, remove the 'animate' class
        entry.target.classList.remove('animate');
      }
    });
  });

  // Start observing each '.data-view' element
  $('.data-view').each(function (index, element) {
    observer.observe(element);
  });
});
