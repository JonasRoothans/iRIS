let cards = document.querySelectorAll('.jump-link')
let months = document.querySelectorAll('.date_box')
let photos = document.querySelectorAll('.photo-container')

function liveSearch() {
    let search_query = document.getElementById("searchbox").value;

    //Use innerText if all contents are visible
    //Use textContent for including hidden elements
    for (var i = 0; i < cards.length; i++) {
        if(cards[i].textContent.toLowerCase()
                .includes(search_query.toLowerCase()) ||
                cards[i].getAttribute('data-speaker').toLowerCase()
                .includes(search_query.toLowerCase())) {
            cards[i].classList.remove("hidden-content");
        } else {
            cards[i].classList.add("hidden-content");
        }
    }
    for (var i = 0; i < photos.length;i++){
        if (photos[i].textContent.toLowerCase()
                .includes(search_query.toLowerCase())) {
                photos[i].classList.remove("hidden-content");
                }
                else {
                photos[i].classList.add("hidden-content");
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