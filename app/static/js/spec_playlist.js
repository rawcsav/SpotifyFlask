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
