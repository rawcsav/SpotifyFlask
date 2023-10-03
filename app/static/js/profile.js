document.addEventListener('DOMContentLoaded', function () {
  const refreshButton = document.getElementById('refresh-button');

  refreshButton.addEventListener('click', async () => {
    try {
      const response = await fetch('/refresh-data', {
        method: 'POST',
      });

      if (response.ok) {
        location.reload(); // Refresh the /profile page
      } else {
        console.error('Failed to refresh data');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  });
});
