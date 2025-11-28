document.addEventListener("click", (event) => {
    const target = event.target;

    // Find the closest ancestor with the "clickable-div" class
    const clickableDiv = target.closest(".clickable-div");

    if (clickableDiv) {
        const url = clickableDiv.getAttribute("data-url");

        if (url) {
            // Redirect to the URL
            window.location.href = url;
        }
    }
});