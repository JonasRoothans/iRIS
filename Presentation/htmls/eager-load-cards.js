// js/eager-load-cards.js

document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll('.card-container');

    if (cards.length === 0) {
        return; // No cards to load
    }

    // A function to fetch and populate a single card
    const loadCard = (cardElement) => {
        const cardId = cardElement.id.replace('card-', ''); // Extracts '12345' from 'card-12345'
        const url = `cards/${cardId}.json`; // Template literal for the correct URL

        // Fetch the JSON file
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status} for ${url}`);
                }
                return response.json();
            })
            .then(data => {
                // Populate the vote placeholder, if it exists and data is available
                const votePlaceholder = document.getElementById(`vote-details-${cardId}`);
                if (votePlaceholder && data.vote) {
                    votePlaceholder.innerHTML = data.vote;
                }

                // Populate the keywords placeholder
                const keywordsPlaceholder = document.getElementById(`keywords-details-${cardId}`);
                if (keywordsPlaceholder && data.keywords) {
                    keywordsPlaceholder.innerHTML = data.keywords;
                }

                // Populate the keywords placeholder
                const inhoudPlaceholder = document.getElementById(`inhoud-details-${cardId}`);
                if (inhoudPlaceholder && data.inhoud) {
                    inhoudPlaceholder.innerHTML = data.inhoud;
                }

                // Add more logic for other placeholders if needed ...
            })
            .catch(error => {
                console.error(`Failed to load content for card ${cardId}:`, error);

                // Optionally display an error or fallback content in the card
                cardElement.innerHTML = '<p class="error">Unable to load card content.</p>';
            });
    };

    // Loop through all the cards and fetch their data
    const promises = Array.from(cards).map(card => loadCard(card));

    // When all cards have been loaded
    Promise.all(promises).then(() => {
        console.log("All card content has been loaded.");
    });
});