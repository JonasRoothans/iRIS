document.addEventListener('DOMContentLoaded', () => {
    // Target the "Vrienden" button
    const vriendenButton = document.querySelector('.vrienden-btn');
    const bb = document.getElementById("bottom-box");

    // Add click event to hide the splash div
    vriendenButton.addEventListener('click', () => {
        const splash = document.querySelector('.splash');
        if (splash) {
            splash.classList.add('hidden-content'); // Add the "hidden-content" class
        }
        const splashbg = document.querySelector('.splash-screen-background');
        if (splashbg) {
            splashbg.classList.add('hidden-content'); // Add the "hidden-content" class
        }
        bb.classList.add('hidden-content');
    });
});