// fav.js

document.addEventListener('DOMContentLoaded', () => {
  const STORAGE_KEY = 'favoriteCardIDs';
  const SOLID_STAR = '★';
  const HOLLOW_STAR = '☆';

  // --- Helper Functions ---

  // Get favorite IDs from localStorage as a Set for efficient lookups
  const getFavorites = () => {
    const favorites = localStorage.getItem(STORAGE_KEY);
    return favorites ? new Set(JSON.parse(favorites)) : new Set();
  };

  // Save the Set of favorite IDs back to localStorage
  const saveFavorites = (favoritesSet) => {
    const ids = Array.from(favoritesSet);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
  };


  // --- Main Logic ---

  // Find all star icons on the page
  const stars = document.querySelectorAll('.star-icon');
  const favoriteIDs = getFavorites();
  const filterfav = document.getElementById('filterfavs')
  const searchbox = document.getElementById('searchbox')

  stars.forEach(star => {
    const card = star.closest('.panel');
    if (!card) return;

    const cardId = card.dataset.id;

    // 1. On page load, set the correct star state
    if (favoriteIDs.has(cardId)) {
      star.textContent = SOLID_STAR;
      star.classList.add('favoriet')
    }

    // 2. Add click event listener
    star.addEventListener('click', (event) => {
      // Prevent click from bubbling up to the parent card
      event.stopPropagation();

      const currentFavorites = getFavorites();
      const isFavorited = currentFavorites.has(cardId);

      if (isFavorited) {
        // Un-favorite it
        currentFavorites.delete(cardId);
        star.textContent = HOLLOW_STAR;
        star.classList.remove('favoriet')
      } else {
        // Favorite it
        currentFavorites.add(cardId);
        star.textContent = SOLID_STAR;
        star.classList.add('favoriet')

      }

      // Save the updated list
      saveFavorites(currentFavorites);
    });


  });

  // --- NEW: Logic for filtering by favorites ---
  const filterStar = document.querySelector('.filterfavs');
  const searchBox = document.querySelector('#searchbox');

  if (filterStar && searchBox) {
    filterStar.addEventListener('click', () => {
      const isFilterActive = filterStar.classList.contains('favoriet');

      // Check if the filter is currently active AND the star is in the box
      if (isFilterActive && searchBox.value.includes(SOLID_STAR)) {
        // Deactivate: clear search and remove class
        filterStar.classList.remove('favoriet');
        searchBox.value = searchBox.value.replace(SOLID_STAR,'')
        searchBox.classList.remove('favoriet')
      } else {
        // Activate: add star to search and add class
        filterStar.classList.add('favoriet');
        searchBox.value = SOLID_STAR + searchBox.value;
        searchBox.classList.add('favoriet')
      }

      // Programmatically trigger an 'input' event on the search box.
      // This will make your liveSearch() function run as if a user typed.
      searchBox.dispatchEvent(new KeyboardEvent('keyup', { 'key': ' ' }));
    });
  }
});