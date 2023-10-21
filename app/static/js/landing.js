function toggleMode() {
  const body = document.body;
  const toggleButton = document.getElementById('modeToggle');

  if (body.classList.contains('dark-mode')) {
    body.classList.remove('dark-mode');
    toggleButton.innerText = 'Dark Mode';
  } else {
    body.classList.add('dark-mode');
    toggleButton.innerText = 'Light Mode';
  }
}

function handleAuthClick() {
  window.isArtGenerationRequest = true;
  window.showLoading(20000);
  window.onload = function () {
    if (window.isArtGenerationRequest) {
      window.hideLoading();
      // Reset the flag
      window.isArtGenerationRequest = false;
    }
  };
}
