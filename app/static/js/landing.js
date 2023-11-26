function handleAuthClick() {
  window.isArtGenerationRequest = true;
  window.showLoading(20000);

  // Set up a function to hide the loading indicator
  function checkArtGenerationRequest() {
    if (window.isArtGenerationRequest) {
      window.hideLoading();
      window.isArtGenerationRequest = false;
    }
  }

  // Check the art generation request status on load
  window.addEventListener('load', checkArtGenerationRequest);
}

// Function to adjust the title container width based on the title width
function adjustTitleContainerWidth() {
  var titleWidth = document.querySelector('.landing-title').offsetWidth;
  var titleContainer = document.querySelector('.title-container');
  titleContainer.style.width = titleWidth + 'px';
}

// Adjust the title container width on load and resize
window.addEventListener('load', adjustTitleContainerWidth);
window.addEventListener('resize', adjustTitleContainerWidth);
