document.addEventListener('DOMContentLoaded', function () {
  const refreshButton = document.getElementById('refresh-button');

  refreshButton.addEventListener('click', function () {
    $.ajax({
      url: '/refresh-data',
      method: 'POST',
      success: function (response) {
        location.reload(); // Refresh the /profile page
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('Failed to refresh data:', errorThrown);
      },
    });
  });
});
