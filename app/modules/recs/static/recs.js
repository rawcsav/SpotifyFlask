function getCsrfToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

document.addEventListener("DOMContentLoaded", function () {
  const playlistsContainer = document.getElementById("playlistOptions");

  fetch("/recs/get-user-playlists")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((playlists) => {
      if (playlists.error) {
        playlistsContainer.innerHTML = `<p>Error: ${playlists.error}</p>`;
      } else {
        // Generate HTML for each playlist and join them into a single string
        const playlistsHtml = playlists
          .map((playlist) => {
            return `<div class="playlist-option" data-playlistid="${playlist.id}">
                    <div class="playlist-item">
                      <img src="${playlist.cover_art}" alt="${playlist.name}" class="playlist-image">
                      <h3 class="playlist-name">${playlist.name}</h3>
                      <p>Owner: ${playlist.owner}</p>
                    </div>
                    </div>`;
          })
          .join("");
        // Set the innerHTML of the playlistsContainer to the generated HTML
        playlistsContainer.innerHTML = playlistsHtml;
      }
    })
    .catch((error) => {
      console.error(
        "There has been a problem with your fetch operation:",
        error,
      );
      playlistsContainer.innerHTML = `<p>Failed to load playlists.</p>`;
    });
  const modal = document.getElementById("instructionsModal");
  const closeBtn = document.querySelector(".close");

  document
    .getElementById("showInstructions")
    .addEventListener("click", function () {
      modal.style.display = "block";
    });

  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  document
    .getElementById("showInstructions")
    .addEventListener("click", function () {
      document.getElementById("instructionsModal").style.display = "block";
      document.body.style.overflow = "hidden";
    });

  document.querySelector(".close").addEventListener("click", function () {
    document.getElementById("instructionsModal").style.display = "none";
    document.body.style.overflow = "auto";
  });

  window.addEventListener("click", function (event) {
    if (event.target === document.getElementById("instructionsModal")) {
      document.getElementById("instructionsModal").style.display = "none";
      document.body.style.overflow = "auto";
    }
  });

  // eslint-disable-next-line no-unused-vars
  function getSliderConfig(sliderId, inputId) {
    const slider = document.getElementById(sliderId);

    console.log("sliderId:", sliderId);
    console.log("valueLow (raw):", slider.getAttribute("valueLow")); // Get the raw attribute value
    console.log("valueHigh (raw):", slider.getAttribute("valueHigh"));

    const valueLow = parseFloat(slider.getAttribute("valueLow")); // Modify to get the attribute directly
    const valueHigh = parseFloat(slider.getAttribute("valueHigh"));

    console.log("valueLow (parsed):", valueLow, typeof valueLow);
    console.log("valueHigh (parsed):", valueHigh, typeof valueHigh);

    return {
      start: [valueLow, valueHigh],
      connect: true,
      range: {
        min: Math.min(valueLow, valueHigh), // Ensures correct overall min
        max: Math.max(valueLow, valueHigh), // Ensures correct overall max
      },
    };
  }

  function createSlider(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const sliderConfig = getSliderConfig(sliderId, inputId);

    // eslint-disable-next-line no-undef
    noUiSlider.create(slider, sliderConfig); // No need to log here anymore

    slider.noUiSlider.on("update", function (values, handle) {
      document.getElementById(inputId).value = values.join(",");
    });
  }
  createSlider("popularity_slider", "popularity_input");
  createSlider("energy_slider", "energy_input");
  createSlider("instrumentalness_slider", "instrumentalness_input");
  createSlider("tempo_slider", "tempo_input");
  createSlider("danceability_slider", "danceability_input");
  createSlider("valence_slider", "valence_input");
});

function getTotalSeeds() {
  return document.querySelectorAll(
    "#universal_seeds_container .clickable-result",
  ).length;
}
document
  .getElementById("universal_search_results")
  .addEventListener("click", function (event) {
    if (event.target.closest(".clickable-result")) {
      if (getTotalSeeds() < 5) {
        let seedType = event.target
          .closest(".clickable-result")
          .classList.contains("track")
          ? "track"
          : "artist";
        let seed = event.target.closest(".clickable-result").cloneNode(true);
        seed.classList.add(seedType);
        document.getElementById("universal_seeds_container").appendChild(seed);
        updateSeedsInput("universal_seeds_container");
      } else {
        alert("You can select no more than 5 combined seeds.");
      }
    }
  });

document
  .getElementById("universal_search")
  .addEventListener("click", function () {
    let query = document.getElementById("universal_input").value;
    document.getElementById("universal_search_results").innerHTML = "";

    fetch("/recs/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        query: query,
        type: "track,artist",
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        let trackResults = data["tracks"]["items"];
        let artistResults = data["artists"]["items"];
        let searchResults = document.getElementById("universal_search_results");
        searchResults.innerHTML = "";

        trackResults.forEach((result) => {
          searchResults.insertAdjacentHTML(
            "beforeend",
            `<div class="clickable-result track" data-id="${result["id"]}">
             <img src="${result["album"]["images"][0]["url"]}" alt="Cover Art" class="result-image">
             <div class="result-info">
                 <h2>${result["name"]}</h2>
                 <p>${result["artists"][0]["name"]}</p>
             </div>
           </div>`,
          );
        });

        artistResults.forEach((result) => {
          searchResults.insertAdjacentHTML(
            "beforeend",
            `<div class="clickable-result artist" data-id="${result["id"]}">
             <img src="${result["images"][0]["url"]}" alt="${result["name"]}" class="result-image">
             <div class="result-info">
                 <h2>${result["name"]}</h2>
             </div>
           </div>`,
          );
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

document
  .getElementById("universal_input")
  .addEventListener("keypress", function (e) {
    if (e.which === 13) {
      // eslint-disable-next-line no-unused-vars
      let query = this.value;
      document.getElementById("universal_search").click();
    }
  });
document
  .getElementById("universal_seeds_container")
  .addEventListener("click", function (event) {
    if (event.target.closest(".clickable-result")) {
      event.target.closest(".clickable-result").remove();
      console.log("Seed removed");
      updateSeedsInput("universal_seeds_container");
    }
  });

document.querySelector("form").addEventListener("submit", function (event) {
  event.preventDefault();
  getRecommendations();
});

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

document.addEventListener("click", function (event) {
  if (event.target.closest(".add-to-saved")) {
    event.preventDefault();

    let heartIcon = event.target
      .closest(".add-to-saved")
      .querySelector(".heart-icon");
    let trackId = event.target.closest(".add-to-saved").dataset.trackid;
    let button = event.target.closest(".add-to-saved");

    if (heartIcon.classList.contains("icon-")) {
      fetch("/recs/unsave_track", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ track_id: trackId }),
      })
        .then((response) => {
          if (response.ok) {
            showToast(button, "Track unsaved successfully!");
            heartIcon.classList.remove("icon-heart-minus", "liked");
            heartIcon.classList.add("icon-heart-plus");
          } else {
            throw new Error("Error unsaving the track");
          }
        })
        .catch((error) => {
          showToast(button, "An error occurred while unsaving the track.");
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
        .then((response) => {
          if (response.ok) {
            showToast(button, "Track saved successfully!");
            heartIcon.classList.remove("icon-heart-plus");
            heartIcon.classList.add("icon-heart-minus", "liked");
          } else {
            throw new Error("Error saving the track");
          }
        })
        .catch((error) => {
          showToast(button, "An error occurred while saving the track.");
          console.error("Error:", error);
        });
    }
  }
});

document.addEventListener("click", function (event) {
  // Check if the clicked element or its parent has the 'add-to-playlist' class
  if (event.target.closest(".add-to-playlist")) {
    event.preventDefault(); // Prevent default action

    const button = event.target.closest(".add-to-playlist");
    const trackId = button.dataset.trackid; // Retrieve the track ID from the data attribute
    const playlistModal = document.getElementById("playlistModal");

    // Set the track ID and button reference in the modal for later use
    playlistModal.dataset.trackid = trackId;
    playlistModal.dataset.button = button;
    playlistModal.style.display = "block"; // Display the modal
  }
});

// This function handles adding a track to a playlist
function addToPlaylist(trackId, playlistId, button) {
  fetch("/recs/add_to_playlist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(), // Ensure CSRF token is correctly used
    },
    body: JSON.stringify({ track_id: trackId, playlist_id: playlistId }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      showToast(button, "Added to Playlist!"); // Show success message
      const plusIcon = button.querySelector(".plus-icon");
      plusIcon.classList.remove("plus-icon-grey");
      plusIcon.classList.add("plus-icon-green"); // Update icon color
      document.getElementById("playlistModal").style.display = "none"; // Hide the modal
    })
    .catch((error) => {
      console.error("Error:", error);
      showToast(button, "An error occurred while adding to the playlist.");
    });
}

// Listen for clicks on playlist options within the modal
document.addEventListener("click", function (event) {
  if (event.target.closest(".playlist-option")) {
    event.preventDefault();

    const playlistOption = event.target.closest(".playlist-option");
    const playlistId = playlistOption.dataset.playlistid; // Retrieve the playlist ID
    const modal = document.getElementById("playlistModal");
    const trackId = modal.dataset.trackid; // Retrieve the track ID set earlier
    const button = modal.dataset.button; // Retrieve the button reference

    addToPlaylist(trackId, playlistId, button); // Call the function to add to playlist
  }
});

document.querySelectorAll(".close").forEach((closeButton) => {
  closeButton.addEventListener("click", function () {
    document.getElementById("playlistModal").style.display = "none";
  });
});

window.addEventListener("click", function (event) {
  if (event.target === document.getElementById("playlistModal")) {
    document.getElementById("playlistModal").style.display = "none";
  }
});

document.addEventListener("click", function (event) {
  if (event.target.closest(".add-to-seeds-toggle")) {
    event.preventDefault();
    event.target
      .closest(".add-to-seeds-toggle")
      .nextElementSibling.classList.toggle("hidden");
  }
});

window.addEventListener("click", function (event) {
  if (!event.target.closest(".add-to-seeds-dropdown")) {
    document.querySelectorAll(".seeds-options").forEach((element) => {
      element.classList.add("hidden");
    });
  }
});
function updateSeedsInput(inputId) {
  let ids = [];
  let trackIds = [];
  let artistIds = [];
  const seedsContainer = document.getElementById("universal_seeds_container");

  // Then, use the seedsContainer variable to find all .clickable-result elements within it
  seedsContainer
    .querySelectorAll(".clickable-result")
    .forEach(function (element) {
      const id = element.getAttribute("data-id");
      ids.push(id);

      if (element.classList.contains("track")) {
        trackIds.push(id);
      } else if (element.classList.contains("artist")) {
        artistIds.push(id);
      }
    });

  document.getElementById(inputId).value = ids.join(",");
  console.log("trackIds:", trackIds);
  console.log("artistIds:", artistIds);
  document.getElementById("track_seeds").value = trackIds.join(",");
  document.getElementById("artist_seeds").value = artistIds.join(",");
}
async function getRecommendations() {
  const formData = new FormData(document.querySelector("form"));
  const formObject = Object.fromEntries(formData.entries());
  const formJSON = JSON.stringify(formObject);

  try {
    const response = await fetch("/recs/get_recommendations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: formJSON,
    });
    const data = await response.json();
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
  if (event.target.closest(".add-to-seeds")) {
    event.preventDefault();
    if (getTotalSeeds() < 5) {
      let trackId, trackName, artistName, artistId;
      let seedType = event.target
        .closest(".add-to-seeds")
        .classList.contains("track")
        ? "track"
        : "artist";
      let imgSrc = event.target
        .closest(".result-item")
        .querySelector(".result-cover-art-container img").src;

      let seedElement;
      if (seedType === "track") {
        trackId = event.target.closest(".add-to-seeds").dataset.trackid;
        trackName = event.target.closest(".add-to-seeds").dataset.name;
        artistName = event.target.closest(".add-to-seeds").dataset.artist;
        seedElement = document.createElement("div");
        seedElement.classList.add("clickable-result", "track");
        seedElement.dataset.id = trackId;
        seedElement.innerHTML = `<img src="${imgSrc}" alt="Cover Art" class="result-image">
                                 <div class="result-info">
                                     <h2>${trackName}</h2>
                                     <p>${artistName}</p>
                                 </div>`;
      } else {
        artistName = event.target.closest(".add-to-seeds").dataset.artist;
        artistId = event.target.closest(".add-to-seeds").dataset.artistid;
        seedElement = document.createElement("div");
        seedElement.classList.add("clickable-result", "artist");
        seedElement.dataset.id = artistId;
        seedElement.innerHTML = `<img src="${imgSrc}" alt="Cover Art" class="result-image">
                                 <div class="result-info">
                                     <h2>${artistName}</h2>
                                 </div>`;
      }

      document
        .getElementById("universal_seeds_container")
        .appendChild(seedElement);
      updateSeedsInput("universal_seeds_container");
    } else {
      alert("You can select no more than 5 combined seeds.");
    }
  }
});

function updateSvgContainerHeight() {
  const bodyHeight = document.body.scrollHeight; // Get the full scroll height of the body
  const svgContainer = document.querySelector(".svg-container");
  svgContainer.style.height = `${bodyHeight}px`; // Update the container height
}

const toggleButton = document.getElementById("toggleButton");
const formContainer = document.querySelector(".form-container");
const searchContainer = document.querySelector(".search-container");
const seedsContainer = document.querySelector(".seed-container"); // Add this line

let isFormVisible = false; // The form is not visible by default
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
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_30",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_33",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_35",
  "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_36",
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
  { class: "svg1", x: "10%", y: "4%" },
  { class: "svg2", x: "80%", y: "10%" },
  { class: "svg3", x: "65%", y: "1%" },
  { class: "svg4", x: "1%", y: "27%" },
  { class: "svg5", x: "91%", y: "30%" },
  { class: "svg6", x: "3%", y: "53%" },
  { class: "svg7", x: "85%", y: "60%" },
  { class: "svg8", x: "30%", y: "70%" },
  { class: "svg9", x: "50%", y: "75%" },
  { class: "svg10", x: "39%", y: "6%" },
  { class: "svg11", x: "73%", y: "81%" },
  { class: "svg12", x: "15%", y: "80%" },
];

const selectedPositions = svgPositions
  .sort(() => 0.5 - Math.random())
  .slice(0, 12);

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
svgContainer.style.overflow = "hidden"; // Prevent scrollbars if SVGs overflow
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
  svgContainer.appendChild(svgImage);
});
updateSvgContainerHeight();
window.addEventListener("resize", updateSvgContainerHeight);

toggleButton.addEventListener("click", function () {
  // Check if the viewport width is less than or equal to 620px
  if (window.innerWidth <= 1024) {
    if (isFormVisible) {
      formContainer.style.display = "none";
      searchContainer.style.display = "flex"; // Adjust according to your layout
      seedsContainer.style.display = "flex"; // Show seeds container - adjust if needed
    } else {
      formContainer.style.display = "flex"; // Adjust according to your layout
      searchContainer.style.display = "none";
      seedsContainer.style.display = "none"; // Hide seeds container
    }
    isFormVisible = !isFormVisible;
  }
});

// Optional: Add a resize event listener to handle cases when the window is resized across the 620px threshold
window.addEventListener("resize", function () {
  if (window.innerWidth > 1024) {
    // If the viewport is wider than 620px, ensure both containers are visible
    formContainer.style.display = "flex";
    searchContainer.style.display = "flex";
    seedsContainer.style.display = "flex"; // Show seeds container - adjust if needed
  } else {
    // If the viewport is 620px or less, apply the visibility based on the isFormVisible flag
    if (isFormVisible) {
      formContainer.style.display = "flex";
      searchContainer.style.display = "none";
      seedsContainer.style.display = "none"; // Hide seeds container
    } else {
      formContainer.style.display = "none";
      searchContainer.style.display = "flex";
      seedsContainer.style.display = "flex"; // Show seeds container - adjust if needed
    }
  }
});
