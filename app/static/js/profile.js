document.addEventListener('DOMContentLoaded', function () {
  const refreshButton = document.getElementById('refresh-button');

  refreshButton.addEventListener('click', function (event) {
    window.showLoading();

    event.stopImmediatePropagation();

    $.ajax({
      url: '/refresh-data',
      method: 'POST',
      success: function (response) {
        location.reload();
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.error('Failed to refresh data:', errorThrown);
        window.hideLoading();
      },
    });
  });
});
