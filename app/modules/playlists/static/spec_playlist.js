let artGenFetched = false;
var myPieChart;
let recommendationsFetched = false;

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toastMessage");

  toastMessage.textContent = message;

  if (type === "error") {
    toast.classList.add("error");
    toast.classList.remove("success");
  } else {
    toast.classList.add("success");
    toast.classList.remove("error");
  }

  toast.style.display = "block";

  setTimeout(() => {
    toast.style.display = "none";
  }, 5000);
}

function getCsrfToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

document.querySelector(".close-toast").addEventListener("click", function () {
  this.parentElement.style.display = "none";
});
var dataContainer = document.getElementById("data-container");

var artgenTen = dataContainer.dataset.artgenTen;
var yearCountData = dataContainer.dataset.yearCount;
var playlistId = dataContainer.dataset.playlistId;

try {
  yearCountData = JSON.parse(yearCountData);
} catch (error) {
  console.error("yearCountData could not be converted to a dictionary:", error);
}

const validJsonString = artgenTen.replace(/'/g, '"');

try {
  artgenTen = JSON.parse(validJsonString);
} catch (error) {
  console.error("The string could not be converted to a dictionary:", error);
}
document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("themeToggled", function () {
    if (typeof myPieChart !== "undefined") {
      let isDarkMode = document.body.classList.contains("dark-mode");
      let legendLabelColor = isDarkMode ? "#e9705a" : "#1c1d21";
      myPieChart.options.plugins.legend.labels.color = legendLabelColor;
      myPieChart.update();
    }
  });

  // eslint-disable-next-line no-undef
  function toggleDivVisibility(selector) {
    var el = document.querySelector(selector);
    if (getComputedStyle(el).display === "none") {
      el.style.display = "block";
    } else {
      el.style.display = "none";
    }
  }

  document.querySelectorAll(".data-view-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".data-view-btn").forEach((btn) => {
        btn.classList.remove("active");
      });
      this.classList.add("active");
      var btnId = this.id;
      var dataViewToShow = btnId.replace("-btn", "");
      document.querySelectorAll(".data-view").forEach((view) => {
        view.style.display = "none";
      });
      document.getElementById(dataViewToShow).style.display = "block";
    });
  });

  // eslint-disable-next-line no-undef
  let labels = Object.keys(yearCountData);
  // eslint-disable-next-line no-undef
  let data = Object.values(yearCountData);

  var ctx = document.getElementById("YrPieChart").getContext("2d");
  // eslint-disable-next-line no-undef
  myPieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.5)",
            "rgba(54, 162, 235, 0.5)",
            "rgba(255, 206, 86, 0.5)",
            "rgba(75, 192, 192, 0.5)",
            "rgba(153, 102, 255, 0.5)",
            "rgba(255, 159, 64, 0.5)",
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
          text: "Distribution of Track Release Dates",
          fontSize: 16,
          align: "center",
          position: "bottom",
        },
        legend: {
          position: "left",
          labels: {
            boxWidth: 10,
            padding: 5,
          },
        },
      },
    },
  });

  document
    .getElementById("like-all-songs-btn")
    .addEventListener("click", function () {
      // eslint-disable-next-line no-undef
      fetch("/playlist/like_all_songs/" + playlistId)
        .then((response) => response.text())
        .then((response) => {
          showToast(response);
        })
        // eslint-disable-next-line no-unused-vars
        .catch((error) => {
          showToast("An error occurred while liking all songs.", "error");
        });
    });

  document
    .getElementById("unlike-all-songs-btn")
    .addEventListener("click", function () {
      // eslint-disable-next-line no-undef
      fetch("/playlist/unlike_all_songs/" + playlistId)
        .then((response) => response.text())
        .then((response) => {
          showToast(response);
        })
        .catch((error) => {
          showToast(
            "An error occurred while unliking all songs:" + error,
            "error",
          );
        });
    });

  document
    .getElementById("remove-duplicates-btn")
    .addEventListener("click", function () {
      // eslint-disable-next-line no-undef
      fetch("/playlist/remove_duplicates/" + playlistId)
        .then((response) => response.text())
        // eslint-disable-next-line no-unused-vars
        .then((response) => {
          showToast("Successfully removed duplicates.");
        })
        .catch((error) => {
          showToast(
            "An error occurred while removing duplicates:" + error,
            "error",
          );
        });
    });

  // eslint-disable-next-line no-unused-vars
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate");
      } else {
        entry.target.classList.remove("animate");
      }
    });
  });

  document.querySelectorAll(".data-view").forEach((element) => {
    observer.observe(element);
  });

  function reorderPlaylist(criterion) {
    // eslint-disable-next-line no-undef
    fetch(`/playlist/playlist/${playlistId}/reorder`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ sorting_criterion: criterion }),
    })
      .then((response) => response.json())
      .then((response) => {
        if (response.status === "Playlist reordered successfully") {
          showToast("Playlist reordered successfully.");
        } else {
          showToast("Failed to reorder playlist.", "error");
        }
      })
      // eslint-disable-next-line no-unused-vars
      .catch((error) => {
        showToast(
          "An error occurred while reordering the playlist:" + error,
          "error",
        );
      });
  }

  function showReorderModal(callback) {
    document.getElementById("reorderModal").style.display = "block";

    document.getElementById("confirmReorder").onclick = function () {
      document.getElementById("reorderModal").style.display = "none";
      callback();
    };

    document.getElementById("cancelReorder").onclick = function () {
      document.getElementById("reorderModal").style.display = "none";
    };
  }

  document
    .getElementById("order-desc-btn")
    .addEventListener("click", function () {
      showReorderModal(function () {
        reorderPlaylist("Date Added - Descending");
      });
    });

  document
    .getElementById("order-asc-btn")
    .addEventListener("click", function () {
      showReorderModal(function () {
        reorderPlaylist("Date Added - Ascending");
      });
    });

  document.getElementById("rd-asc-btn").addEventListener("click", function () {
    showReorderModal(function () {
      reorderPlaylist("Release Date - Ascending");
    });
  });

  document.getElementById("rd-desc-btn").addEventListener("click", function () {
    showReorderModal(function () {
      reorderPlaylist("Release Date - Descending");
    });
  });
  document.getElementById("shuffle-btn").addEventListener("click", function () {
    showReorderModal(function () {
      reorderPlaylist("Shuffle");
    });
  });

  document
    .getElementById("recommendations-btn")
    .addEventListener("click", function (event) {
      event.preventDefault();
      if (!recommendationsFetched) {
        getPLRecommendations();
        recommendationsFetched = true;
      } else {
        toggleDivVisibility(".results-title-spot");
      }
    });

  async function getPLRecommendations() {
    try {
      const response = await fetch(
        `/playlist/get_pl_recommendations/${playlistId}/recommendations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
        },
      );
      const data = await response.json();
      toggleDivVisibility(".results-title-spot");
      displayRecommendations(data["recommendations"]);
    } catch (error) {
      console.error("Error:", error);
    }
  }

  function createTrackElement(trackInfo) {
    const div = document.createElement("div");
    div.className = "result-item";
    div.innerHTML = `
        <div class="result-cover-art-container">
            <img src="${trackInfo["cover_art"]}" alt="Cover Art" class="result-cover-art">
            <div class="caption">
                <h2>${trackInfo["trackName"]}</h2>
                <p>${trackInfo["artist"]}</p>
            </div>
            <div class="play-button noselect" id="play_${trackInfo["trackid"]}"><i class="icon-play"></i></div>
        </div>
        <div class="dropdown-content">
            <a href="#" class="add-to-saved" data-trackid="${trackInfo["trackid"]}"><i class="heart-icon icon-heart-plus"></i></a>
            <a href="#" class="add-to-playlist" data-trackid="${trackInfo["trackid"]}"><i class="plus-icon icon-album-plus"></i></a>
        </div>
        <audio controls class="audio-player" id="audio_${trackInfo["trackid"]}">
            <source src="${trackInfo["preview"]}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    `;
    return div; // Return the element for external handling
  }
  // Global reference to currently playing audio to manage play/pause
  let currentPlayingAudio = null;

  function setupPlayToggle(trackId) {
    const playButton = document.getElementById(`play_${trackId}`);
    const audioPlayer = document.getElementById(`audio_${trackId}`);
    const playIcon = playButton.querySelector("i"); // Assuming <i> is a direct child of the play button

    playButton.addEventListener("click", function () {
      // If there's any audio playing, pause it and reset its button
      if (currentPlayingAudio && currentPlayingAudio !== audioPlayer) {
        currentPlayingAudio.pause();
        currentPlayingAudio.currentTime = 0; // Optionally reset the audio to the start
        const playingId = currentPlayingAudio
          .getAttribute("id")
          .replace("audio_", "");
        const playingButtonIcon = document
          .getElementById(`play_${playingId}`)
          .querySelector("i");
        playingButtonIcon.className = "icon-play"; // Reset the icon
      }

      // Toggle play/pause for the clicked track
      if (audioPlayer.paused) {
        audioPlayer.play();
        playIcon.className = "icon-pause"; // Change the icon to pause
        currentPlayingAudio = audioPlayer; // Update the currently playing audio
      } else {
        audioPlayer.pause();
        playIcon.className = "icon-play"; // Change the icon back to play
        currentPlayingAudio = null; // No audio is playing now
      }
    });
  }
  // Assume you have a function like this to handle the display of recommendations
  function displayRecommendations(recommendations) {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = ""; // Clear existing entries

    recommendations.forEach((trackInfo) => {
      const trackElement = createTrackElement(trackInfo);
      resultsContainer.appendChild(trackElement); // Append the element here
      setupPlayToggle(trackInfo["trackid"]); // Setup control here if preferable
    });
  }

  document.addEventListener("click", function (event) {
    if (event.target.closest(".add-to-playlist")) {
      event.preventDefault();

      let plusIcon = event.target
        .closest(".add-to-playlist")
        .querySelector(".plus-icon");
      let trackId = event.target.closest(".add-to-playlist").dataset.trackid;

      if (plusIcon.classList.contains("icon-minus")) {
        fetch("/recs/remove_from_playlist", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          // eslint-disable-next-line no-undef
          body: JSON.stringify({ playlist_id: playlistId, track_id: trackId }),
        })
          .then((response) => response.json())
          // eslint-disable-next-line no-unused-vars
          .then((data) => {
            showToast("Track removed from playlist successfully!");

            plusIcon.classList.remove("icon-minus", "added");
            plusIcon.classList.add("icon-plus");
          })
          .catch((error) => {
            showToast(
              "An error occurred while removing the track from the playlist.",
              "error",
            );
            console.error("Error:", error);
          });
      } else {
        fetch("/recs/add_to_playlist", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ playlist_id: playlistId, track_id: trackId }),
        })
          .then((response) => response.json())
          // eslint-disable-next-line no-unused-vars
          .then((data) => {
            showToast("Track added to playlist successfully!");

            plusIcon.classList.remove("icon-plus");
            plusIcon.classList.add("icon-minus", "added");
          })
          .catch((error) => {
            showToast(
              "An error occurred while adding the track to the playlist.",
              "error",
            );
            console.error("Error:", error);
          });
      }
    }
  });
});

document.addEventListener("click", function (event) {
  if (event.target.closest(".add-to-saved")) {
    event.preventDefault();

    let heartIcon = event.target
      .closest(".add-to-saved")
      .querySelector(".heart-icon");
    let trackId = event.target.closest(".add-to-saved").dataset.trackid;

    if (heartIcon.classList.contains("icon-heart-minus")) {
      fetch("/recs/unsave_track", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ track_id: trackId }),
      })
        .then((response) => response.json())
        // eslint-disable-next-line no-unused-vars
        .then((data) => {
          showToast("Track unsaved successfully!");

          heartIcon.classList.remove("icon-heart-minus", "liked");
          heartIcon.classList.add("icon-heart-plus");
        })
        .catch((error) => {
          showToast("An error occurred while unsaving the track.", "error");
          console.error("Error:", error);
        });
    } else {
      fetch("/recs/save_track", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ track_id: trackId }),
      })
        .then((response) => response.json())
        // eslint-disable-next-line no-unused-vars
        .then((data) => {
          showToast("Track saved successfully!");

          heartIcon.classList.remove("icon-heart-plus");
          heartIcon.classList.add("icon-heart-minus", "liked");
        })
        .catch((error) => {
          showToast("An error occurred while saving the track.", "error");
          console.error("Error:", error);
        });
    }
  }
});

let genreItems = document.querySelectorAll("#genre-counts > ul > li");
genreItems.forEach((item) => {
  item.addEventListener("click", function () {
    let artistList = item.querySelector(".artist-genre-list");
    if (
      artistList.style.display === "none" ||
      artistList.style.display === ""
    ) {
      artistList.style.display = "block";
    } else {
      artistList.style.display = "none";
    }
  });
});

document.getElementById("apiKeyForm").onsubmit = function (e) {
  e.preventDefault();
  // eslint-disable-next-line no-unused-vars
  var apiKey = document.getElementById("apiKey").value;
  document.getElementById("connect-button").style.display = "block";
  document.getElementById("apiKeyForm").style.display = "none";
};

// eslint-disable-next-line no-unused-vars
function showArtGenContainer() {
  var artGenContainer = document.querySelector(".artist-gen-container");

  if (!artGenFetched) {
    const title =
      '<h2 id="art-gen-title" style="text-align: center;">Cover Art Gen</h2>';

    artGenContainer.innerHTML = title + artGenContainer.innerHTML;

    artGenFetched = true;

    artGenContainer.style.display = "flex";

    fetch("/check-api-key")
      .then((response) => response.json())
      .then((response) => {
        if (response.has_key) {
          document.getElementById("connect-button").style.display = "none";
          document.getElementById("update-button").style.display = "block";
          document.getElementById("generate-art-btn").style.display = "block";
          document.getElementById("gen-refresh-icon").style.display = "block";
          document.getElementById("parent-toggle-icon").style.display = "block";
          document.getElementById("hd-toggle-icon").style.display = "block";
        } else {
          document.getElementById("connect-button").style.display = "block";
          document.getElementById("update-button").style.display = "none";
          document.getElementById("generate-art-btn").style.display = "none";
          document.getElementById("gen-refresh-icon").style.display = "none";
          document.getElementById("parent-toggle-icon").style.display = "none";
          document.getElementById("hd-toggle-icon").style.display = "none";
        }
      })
      .catch((error) => {
        console.error("Error checking API key:", error);
      });
  } else {
    if (
      artGenContainer.style.display === "none" ||
      artGenContainer.style.display === ""
    ) {
      artGenContainer.style.display = "flex";
    } else {
      artGenContainer.style.display = "none";
    }
  }
}

// eslint-disable-next-line no-unused-vars
function handleApiKeySubmit(e) {
  e.preventDefault();

  var apiKey = document.getElementById("apiKey").value;

  fetch("/save-api-key", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({ api_key: apiKey }),
  })
    .then((response) => response.json())
    .then(() => {
      document.getElementById("update-button").style.display = "block";
      document.getElementById("connect-button").style.display = "none";
      document.getElementById("apiKeyForm").style.display = "none";
      document.getElementById("generate-art-btn").style.display = "block";
      document.getElementById("gen-refresh-icon").style.display = "block";
      document.getElementById("parent-toggle-icon").style.display = "block";
      document.getElementById("hd-toggle-icon").style.display = "block";

      showToast("API Key saved successfully!");
    })
    .catch((error) => {
      console.error("Error saving API key:", error);
      showToast("An error occurred while saving the API key.", "error");
    });
}

// eslint-disable-next-line no-unused-vars
function displayInputField(event) {
  event.preventDefault();

  fetch("/check-api-key")
    .then((response) => response.json())
    .then((response) => {
      if (response.has_key) {
        document.getElementById("connect-button").style.display = "none";
        document.getElementById("update-button").style.display = "block";
        document.getElementById("apiKeyForm").style.display = "none";
        document.getElementById("generate-art-btn").style.display = "block";
        document.getElementById("gen-refresh-icon").style.display = "block";
        document.getElementById("parent-toggle-icon").style.display = "block";
        document.getElementById("hd-toggle-icon").style.display = "block";
      } else {
        document.getElementById("connect-button").style.display = "none";
        document.getElementById("update-button").style.display = "none";
        document.getElementById("apiKeyForm").style.display = "flex";
        document.getElementById("generate-art-btn").style.display = "none";
        document.getElementById("gen-refresh-icon").style.display = "none";
        document.getElementById("parent-toggle-icon").style.display = "none";
        document.getElementById("hd-toggle-icon").style.display = "none";
      }
    })
    .catch((error) => {
      console.error("Error checking API key:", error);
    });
}

// eslint-disable-next-line no-unused-vars
function showKeyFormAndHideUpdateButton() {
  document.getElementById("update-button").style.display = "none";
  document.getElementById("generate-art-btn").style.display = "none";
  document.getElementById("gen-refresh-icon").style.display = "none";
  document.getElementById("parent-toggle-icon").style.display = "none";
  document.getElementById("hd-toggle-icon").style.display = "none";
  document.getElementById("apiKeyForm").style.display = "flex";
}

// eslint-disable-next-line no-unused-vars
function toggleCheckbox(checkboxId, iconId) {
  var checkbox = document.getElementById(checkboxId);
  var icon = document.getElementById(iconId);

  checkbox.checked = !checkbox.checked;

  if (checkbox.checked) {
    icon.classList.add("active");
  } else {
    icon.classList.remove("active");
  }
}

// eslint-disable-next-line no-unused-vars
function generateArtForPlaylist() {
  const isHD = document.getElementById("hd-toggle").checked;

  window.isArtGenerationRequest = true;
  window.showLoading(isHD ? 100000 : 60000);

  let genresList = [];
  const isCheckboxChecked = document.getElementById("parent-toggle").checked;

  if (isCheckboxChecked) {
    genresList = Object.values(artgenTen);
  }

  const quality = isHD ? "hd" : "standard";
  let dataPayload = {
    genres_list: genresList,
    quality: quality,
    refresh: false,
  };

  fetch(`/art_gen/generate_images/${playlistId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(dataPayload),
  })
    .then((response) => response.json())
    .then((response) => {
      displayImages(response.images_and_prompts);
      window.hideLoading();
      window.isArtGenerationRequest = false;
      showToast("Image generated successfully.");
    })
    .catch((error) => {
      console.error("Error generating images:", error);
      window.hideLoading();
      window.isArtGenerationRequest = false;
      showToast("An error occurred while generating the image.", "error");
    });
}

// eslint-disable-next-line no-unused-vars
function refreshArt() {
  const isHD = document.getElementById("hd-toggle").checked;
  const quality = isHD ? "hd" : "standard";

  window.isArtGenerationRequest = true;
  window.showLoading(isHD ? 100000 : 55000);

  let dataPayload = {
    quality: quality,
    refresh: true,
  };

  fetch(`/art_gen/generate_images/${playlistId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify(dataPayload),
  })
    .then((response) => response.json())
    .then((response) => {
      window.hideLoading();
      displayImages(response.images_and_prompts);
      window.isArtGenerationRequest = false;
      showToast("Image refreshed successfully.");
    })
    .catch((error) => {
      console.error("Error refreshing images:", error);
      window.hideLoading();
      window.isArtGenerationRequest = false;
      showToast("An error occurred while refreshing the image.", "error");
    });
}

function addArtToPlaylist(imageUrl) {
  fetch(`/playlist/playlist/${playlistId}/cover-art`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({
      image_url: imageUrl,
    }),
  })
    .then((response) => response.json())
    .then((response) => {
      if (
        response.status &&
        response.status === "Cover art updated successfully"
      ) {
        showToast("Playlist cover updated successfully.");
      } else {
        showToast(
          "Failed to update the playlist cover. Please try again.",
          "error",
        );
      }
    })
    .catch((error) => {
      showToast(`Error: ${error.message || "Unknown error"}`, "error");
    });
}

function displayImages(response) {
  const imageContainer = document.getElementById("art-gen-results");
  const imagesAndPrompts = response;

  // Clear the previous images and prompts
  while (imageContainer.firstChild) {
    imageContainer.removeChild(imageContainer.firstChild);
  }

  imagesAndPrompts.forEach((item) => {
    const imageUrl = item.image;
    const promptText = item.prompt;

    const imageDiv = document.createElement("div");
    imageDiv.className = "art-gen-img-div";

    const img = document.createElement("img");
    img.src = imageUrl;
    img.alt = "Generated Cover Art";
    img.className = "art-gen-img";

    // Create a hidden div for the prompt text
    const promptDiv = document.createElement("div");
    promptDiv.className = "art-gen-prompt hidden";
    promptDiv.textContent = promptText;

    const iconDiv = document.createElement("div");
    iconDiv.className = "art-gen-icon-div";

    // Add an information icon
    const infoIcon = document.createElement("i");
    infoIcon.className = "icon-circle-info";
    infoIcon.title = "Info";

    // Event listener for hover (mouseover and mouseout) to show/hide prompt
    infoIcon.addEventListener("mouseover", function () {
      promptDiv.classList.remove("hidden");
    });
    infoIcon.addEventListener("mouseout", function () {
      promptDiv.classList.add("hidden");
    });

    // Event listener for click to toggle prompt visibility
    infoIcon.addEventListener("click", function () {
      promptDiv.classList.toggle("hidden");
    });

    const downloadIcon = document.createElement("i");
    downloadIcon.className = "icon-download";
    downloadIcon.title = "Download image";
    downloadIcon.onclick = function () {
      window.open(imageUrl, "_blank");
    };

    const addPlaylistIcon = document.createElement("i");
    addPlaylistIcon.className = "icon-album-plus";
    addPlaylistIcon.title = "Add to playlist";
    addPlaylistIcon.onclick = function () {
      addArtToPlaylist(imageUrl);
    };

    iconDiv.appendChild(downloadIcon);
    iconDiv.appendChild(addPlaylistIcon);
    iconDiv.appendChild(infoIcon); // Append info icon to the icons
    // Append iconDiv containing the download, add to playlist, and info icons
    imageDiv.appendChild(iconDiv);
    imageDiv.appendChild(promptDiv); // Append the hidden prompt div
    imageDiv.appendChild(img);

    imageContainer.appendChild(imageDiv);
  });

  // Update UI elements if images are available
  if (imagesAndPrompts.length > 0) {
    document.getElementById("gen-refresh-icon").style.opacity = "1";
    document.getElementById("gen-refresh-icon").style.cursor = "pointer";
  }
}

// Function to apply alternating colors to each letter of a given element's text
function applyAlternatingColors(element, colors) {
  // Get the text from the element
  const text = element.textContent;
  // Clear the current text
  element.textContent = "";
  // Iterate over each character of the text
  for (let i = 0; i < text.length; i++) {
    // Create a new span element for each character
    const span = document.createElement("span");
    // Set the text of the span to the current character
    span.textContent = text[i];
    // Set the color of the span to the corresponding color from the array
    span.style.color = colors[i % colors.length];
    // Append the span to the element
    element.appendChild(span);
  }
}

function updateSvgContainerHeight() {
  const bodyHeight = document.body.scrollHeight; // Get the full scroll height of the body
  const svgContainer = document.querySelector(".svg-container");
  svgContainer.style.height = `${bodyHeight}px`; // Update the container height
}

const playlistNameElement = document.getElementById("playlist-name");
const colors = [
  "#ca403f",
  "#f7893b",
  "#f1db2b",
  "#5dab54",
  "#4b8dc2",
  "#9b5de5",
  "#f7a1d5",
];
applyAlternatingColors(playlistNameElement, colors);
const svgUrls = [
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/3673dcf5-01e4-43d2-ac71-ed04a7b56b34",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/amp",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/cd",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/clarinet",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/domra",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/drums_jsuiqf",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/f9cca628-b87a-4880-b2b3-a38e94b48d6f",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/grammy-svgrepo-com",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/gramophone",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/guitar_vqh6f4",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1701529651/randomsvg/headphones_lgdmiw.svg",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1701529651/randomsvg/headphone_pn69ku.svg",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_1",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_2",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_3",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_4",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_5",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_6",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano_hzttv3",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/radio-svgrepo-com",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/shape",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/speaker",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/trombone",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/vinyl_z1naey",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/wave_anpgln",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/xylophone",
];

const svgPositions = [
  { class: "svg1", x: "10%", y: "10%" },
  { class: "svg2", x: "60%", y: "12%" },
  { class: "svg3", x: "65%", y: "1%" },
  { class: "svg4", x: "1%", y: "27%" },
  { class: "svg5", x: "91%", y: "30%" },
  { class: "svg6", x: "3%", y: "46%" },
  { class: "svg7", x: "85%", y: "40%" },
  { class: "svg8", x: "30%", y: "20%" },
  { class: "svg9", x: "50%", y: "35%" },
  { class: "svg10", x: "39%", y: "6%" },
  { class: "svg11", x: "73%", y: "21%" },
  { class: "svg12", x: "15%", y: "53%" },
  { class: "svg13", x: "15%", y: "63%" },
  { class: "svg14", x: "92%", y: "68%" },
  { class: "svg15", x: "21%", y: "71%" },
  { class: "svg16", x: "74%", y: "73%" },
  { class: "svg17", x: "27%", y: "77%" },
];

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

const selectedPositions = shuffleArray(svgPositions);
document.body.style.position = "relative";
document.body.style.overflowX = "hidden"; // Prevent horizontal scrolling
document.body.style.margin = "0"; // Remove default margin

// Create a container for the SVG images
const svgContainer = document.createElement("div");
svgContainer.classList.add("svg-container"); // Add the class for the query selector
svgContainer.style.position = "absolute"; // Change to absolute to scroll with content
svgContainer.style.width = "100%";
// Initial height will be set by updateSvgContainerHeight function
svgContainer.style.top = "0";
svgContainer.style.left = "0";
svgContainer.style.zIndex = "-1"; // Ensure it's behind all other content
document.body.prepend(svgContainer); // Insert it as the first child of body

svgContainer.querySelectorAll(".svg-placeholder").forEach((el) => el.remove());

// Create and append SVG images to the svgContainer
selectedPositions.forEach((position, index) => {
  const svgImage = document.createElement("img");
  svgImage.src = svgUrls[index % svgUrls.length]; // Cycle through SVG URLs
  svgImage.classList.add("svg-placeholder", position.class);
  svgImage.style.position = "absolute";
  svgImage.style.left = position.x;
  svgImage.style.top = position.y;
  svgContainer.style.overflowX = "hidden"; // Prevent scrollbars if SVGs overflow

  svgContainer.appendChild(svgImage);
});
updateSvgContainerHeight();
window.addEventListener("resize", updateSvgContainerHeight);
