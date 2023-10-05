document.addEventListener('DOMContentLoaded', function () {
  const refreshButton = document.getElementById('refresh-button');

  refreshButton.addEventListener('click', function (event) {
    // Show loading animation once
    window.showLoading();

    // Stop other event handlers from executing
    event.stopImmediatePropagation();

    $.ajax({
      url: '/refresh-data',
      method: 'POST',
      success: function (response) {
        // Refresh the page
        location.reload();
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('Failed to refresh data:', errorThrown);
        // Hide loading animation in case of error
        window.hideLoading();
      },
    });
  });
});
