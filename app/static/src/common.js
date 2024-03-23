function getCsrfToken() {
  return document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute("content");
}

document.addEventListener("DOMContentLoaded", function () {
  let ajaxRequestCount = 0;
  let timeoutId; // Ensure timeoutId is declared to manage visibility of loading overlay
  const vinyls = [
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading1",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading10",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading12",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading13",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading14",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading17",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading18",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading19",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading2",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading20",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading21",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading23",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading24",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading25",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading26",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading29",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading3",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading30",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading31",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading32",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading33",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading34",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading35",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading38",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading39",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading41",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading42",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading43",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading44",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading45",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading47",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading48",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading50",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading51",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading52",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading53",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading54",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading55",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading56",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading58",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading59",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading61",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading62",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading63",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading64",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading65",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading66",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading67",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading69",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading70",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading73",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading74",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading75",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading76",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading79",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading8",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading80",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading81",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading82",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading84",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading85",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading86",
    "http://res.cloudinary.com/dn9bcrimg/image/upload/v1/discloader/DiscLoading9",
  ];

  function getRandomVinyl() {
    const randomIndex = Math.floor(Math.random() * vinyls.length);
    return vinyls[randomIndex];
  }

  window.showLoading = function (duration = 4000) {
    let loadingOverlay = document.getElementById("loading-overlay");
    let vinylElement = document.getElementById("vinyl");

    if (loadingOverlay && loadingOverlay.style.display === "flex") {
      return;
    }

    if (!loadingOverlay) {
      loadingOverlay = document.createElement("div");
      loadingOverlay.id = "loading-overlay";
      document.body.appendChild(loadingOverlay);
    }

    if (!vinylElement) {
      vinylElement = document.createElement("div");
      vinylElement.id = "vinyl";
      loadingOverlay.appendChild(vinylElement);
    }

    vinylElement.style.backgroundImage = `url(${getRandomVinyl()})`;
    loadingOverlay.style.display = "flex";
    timeoutId = setTimeout(window.hideLoading, duration);
  };

  window.hideLoading = function () {
    clearTimeout(timeoutId);
    const loadingOverlay = document.getElementById("loading-overlay");
    const fadeOutDuration = 500;

    const completeHide = () => {
      loadingOverlay.remove();
    };

    const animationDisplayedAt = new Date().getTime();
    const timeSinceAnimationDisplayed =
      new Date().getTime() - animationDisplayedAt;
    const minimumDisplayTime = 1000;

    if (timeSinceAnimationDisplayed < minimumDisplayTime) {
      setTimeout(() => {
        loadingOverlay.style.opacity = "0";
        setTimeout(completeHide, fadeOutDuration);
      }, minimumDisplayTime - timeSinceAnimationDisplayed);
    } else {
      loadingOverlay.style.opacity = "0";
      setTimeout(completeHide, fadeOutDuration);
    }
  };

  window.showLoading();

  window.addEventListener("load", function () {
    window.hideLoading();
  });

  // Custom fetch wrapper to track AJAX requests
  window.customFetch = async function (url, options = {}) {
    ajaxRequestCount++;
    if (ajaxRequestCount === 1 && !window.isArtGenerationRequest) {
      window.showLoading();
    }

    try {
      const response = await fetch(url, options);
      return response;
    } finally {
      ajaxRequestCount--;
      if (ajaxRequestCount === 0 && !window.isArtGenerationRequest) {
        window.hideLoading();
      }
    }
  };

  // Event delegation for form submission
  document.addEventListener(
    "submit",
    function (event) {
      const form = event.target.closest("form");
      if (form && form.dataset.ajax) {
        event.preventDefault();
        window.showLoading();

        window
          .customFetch(form.action, {
            method: form.method,
            body: new FormData(form),
          })
          .finally(() => {
            window.hideLoading();
          });
      } else if (form) {
        window.showLoading();
      }
    },
    true,
  ); // Use capture phase for form submission
});

// eslint-disable-next-line no-unused-vars
function toggleDropdown(event) {
  event.stopPropagation(); // Prevents the dropdown from closing
  const menu = document.getElementById("menu");
  const settingsCog = document.getElementById("settingsCog");
  if (menu.style.display === "none" || menu.style.display === "") {
    menu.style.display = "block";
    settingsCog.style.display = "inline-block"; // Show the settings cog
  } else {
    menu.style.display = "none";
    settingsCog.style.display = "none"; // Hide the settings cog
  }
}

// eslint-disable-next-line no-unused-vars
function toggleSettings(event) {
  event.stopPropagation(); // Prevents the dropdown from closing
  // eslint-disable-next-line no-unused-vars
  const settingsCog = document.getElementById("settingsCog");
  const settingsMenu = document.getElementById("settings-menu");
  if (
    settingsMenu.style.display === "none" ||
    settingsMenu.style.display === ""
  ) {
    settingsMenu.style.display = "block";
  } else {
    settingsMenu.style.display = "none";
  }
}

// Close the dropdown if clicked outside
window.addEventListener("click", function (event) {
  const dropdown = document.getElementById("spotifyUserDropdown");
  if (!dropdown.contains(event.target)) {
    document.getElementById("menu").style.display = "none";
  }
});

// eslint-disable-next-line no-unused-vars
function toggleMode() {
  const body = document.body;
  const isDarkMode = body.classList.contains("dark-mode");
  const modeToSave = isDarkMode ? "light" : "dark";

  fetch("/update_mode", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({
      mode: modeToSave,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data.message);

      const toggleButton = document.getElementById("modeToggle");
      if (isDarkMode) {
        body.classList.remove("dark-mode");
        toggleButton.innerText = "Dark Mode";
      } else {
        body.classList.add("dark-mode");
        toggleButton.innerText = "Light Mode";
      }
      document.dispatchEvent(new Event("themeToggled"));
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function checkMode() {
  fetch("/get_mode", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const body = document.body;
      const toggleButton = document.getElementById("modeToggle");

      if (data.mode === "dark") {
        body.classList.add("dark-mode");
        toggleButton.innerText = "Light Mode";
      } else {
        body.classList.remove("dark-mode");
        toggleButton.innerText = "Dark Mode";
      }
      document.dispatchEvent(new Event("themeToggled"));
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
window.onload = function () {
  checkMode();
};
