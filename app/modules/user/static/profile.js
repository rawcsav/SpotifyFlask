function updateSvgContainerHeight() {
  const bodyHeight = document.body.scrollHeight; // Get the full scroll height of the body
  const svgContainer = document.querySelector(".svg-container");
  svgContainer.style.height = `${bodyHeight}px`; // Update the container height
}

document.addEventListener("DOMContentLoaded", function () {
  const svgUrls = [
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/3673dcf5-01e4-43d2-ac71-ed04a7b56b34",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/amp",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/cd",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/clarinet",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/domra",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/drums_jsuiqf",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/f9cca628-b87a-4880-b2b3-a38e94b48d6f",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/grammy-svgrepo-com",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/gramophone",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/guitar_vqh6f4",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1701529651/randomsvg/headphones_lgdmiw.svg",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1701529651/randomsvg/headphone_pn69ku.svg",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_1",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_2",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_3",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_30",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_33",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_35",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_36",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_4",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_5",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/Layer_6",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/piano_hzttv3",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/radio-svgrepo-com",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/shape",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/speaker",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/trombone",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/vinyl_z1naey",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/wave_anpgln",
    "https://res.cloudinary.com/dn9bcrimg/image/upload/v1/randomsvg/xylophone",
  ];
  const refreshButton = document.getElementById("refresh-button");

  refreshButton.addEventListener("click", function (event) {
    window.showLoading();

    event.stopImmediatePropagation();

    fetch("/refresh-data", {
      method: "POST",
    })
      .then((response) => {
        if (response.ok) {
          location.reload();
        } else {
          throw new Error("Failed to refresh data");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        window.hideLoading();
      });
  });
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

  svgContainer
    .querySelectorAll(".svg-placeholder")
    .forEach((el) => el.remove());

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
});
