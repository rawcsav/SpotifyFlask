$('.data-view-btn').click(function () {
  // Get the ID of the button that was clicked
  var btnId = $(this).attr('id');

  // Determine which data view to show based on the button clicked
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

  // Hide all data views
  $('.data-view').hide();

  // Show the selected data view
  $('#' + dataViewToShow).show();
});
$('.data-view-btn').click(function () {
  // Remove the 'active' class from all buttons
  $('.data-view-btn').removeClass('active');

  // Add the 'active' class to the clicked button
  $(this).addClass('active');

  // Hide all data-view divs
  $('.data-view').hide();

  // Show the data-view div that corresponds to the clicked button
  var id = $(this).attr('id').replace('-btn', '');
  $('#' + id).show();
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
          // You can define your colors here
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
    responsive: true,
    title: {
      display: true,
      text: 'Distribution of Track Release Dates',
    },
  },
});
