// search.js

// Combine selectors for all items you want to search through.
let elementsToSearch = document.querySelectorAll('.panel, .adpanel')//, .photo-container');
let months = document.querySelectorAll('.date_box'); // This variable is unused in the function

function liveSearch() {
    let searchQuery = document.getElementById("searchbox").value;
    const favoriteChar = '★';

    // 1. Check if we are filtering by favorites
    const filterByFavorite = searchQuery.includes(favoriteChar);

    // 2. Create a clean text query by removing the star and extra spaces
    const textToFind = searchQuery.replace(favoriteChar, '').trim().toLowerCase();

    // 2b. initially hide all months
    months.forEach(month => {
        month.classList.add("hidden-content")

    })

    // Loop through all searchable elements
    for (let i = 0; i < elementsToSearch.length; i++) {
        const element = elementsToSearch[i];
        const elementText = element.textContent.toLowerCase();

        // 3. Check for matches

        // Condition A: Does it match the text query?
        // (Always true if the text query is empty)
        const textMatch = !textToFind || elementText.includes(textToFind);

        // Condition B: Does it match the favorite requirement?
        // (Always true if we are NOT filtering by favorites)
        const favoriteMatch = !filterByFavorite || elementText.includes(favoriteChar);
        const thismonth = element.closest('.date_box')

        // The element is shown only if BOTH conditions are true
        if (textMatch && favoriteMatch) {
            element.classList.remove("hidden-content");
            if(thismonth){
                element.closest('.date_box').classList.remove("hidden-content")
                }
        } else {
            element.classList.add("hidden-content");
        }
    }
}

//A little delay
let typingTimer;
let typeInterval = 500;
let searchInput = document.getElementById('searchbox');

searchInput.addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(liveSearch, typeInterval);
});