let cards = document.querySelectorAll('.panel, .adpanel')
let months = document.querySelectorAll('.date_box')
let photos = document.querySelectorAll('.photo-container')

function extractMeetingId(url) {
  // Regular expression to match the numeric meeting_id after specific paths
  const regex = /\/(?:vergadering|bijeenkomst)\/(\d+)/;

  const match = url.match(regex);

  // If there's a match, return the first capturing group (the meeting_id)
  return match ? match[1] : url;
}

function liveSearch() {
    let search_query_raw = document.getElementById("searchbox").value;
    search_query = extractMeetingId(search_query_raw)



    //Use innerText if all contents are visible
    //Use textContent for including hidden elements
    for (var i = 0; i < cards.length; i++) {
        if(cards[i].textContent.toLowerCase()
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