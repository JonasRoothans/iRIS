document.addEventListener('DOMContentLoaded', function () {
    const header = document.querySelector('.search-header'); // Select the header
    let lastScrollY = window.scrollY; // Track the last scroll position
    const offsetThreshold = 300; // Distance where the header hides (scroll threshold)
    const endOfPageThreshold = 50; // Distance from the bottom to consider "end of page"

    // Scroll event listener
    window.addEventListener('scroll', function () {
        const currentScrollY = window.scrollY; // Get the current scroll position
        const scrollBottom = document.body.scrollHeight - window.innerHeight; // Scroll position at the bottom of the page

        if (currentScrollY > lastScrollY && currentScrollY > offsetThreshold) {
            // Hide the header when scrolling down and scrolled far enough
            header.classList.add('hidden');
        } else if (currentScrollY < lastScrollY && currentScrollY < scrollBottom - endOfPageThreshold) {
            // Show the header when scrolling up, unless near the bottom of the page
            header.classList.remove('hidden');
        }

        // Update last scroll position
        lastScrollY = currentScrollY;
    });
});