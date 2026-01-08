document.addEventListener("DOMContentLoaded", function () {
    const fabMain = document.getElementById("fabMain");
    const fabOptions = document.getElementById("fabOptions");
    const fabOverlay = document.getElementById("fabOverlay");

    fabMain.addEventListener("click", () => {
        fabOptions.classList.toggle("show");
        fabMain.classList.toggle("active");
        fabOverlay.classList.toggle("active");
    });

    // Close menu when clicking outside
    fabOverlay.addEventListener("click", () => {
        fabOptions.classList.remove("show");
        fabMain.classList.remove("active");
        fabOverlay.classList.remove("active");
    });
});
