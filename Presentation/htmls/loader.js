document.addEventListener("DOMContentLoaded", () => {
  // Select the header element
  const header = document.getElementById("header");
  const hide = document.getElementById('hide-during-loading')
  const hide2 = document.querySelectorAll('#hide-during-loading2')
  const show = document.getElementById('show-during-loading')


  // Simulate a delay of 5 seconds before removing the loading screen
  setTimeout(() => {
    header.classList.remove("full-screen-loader"); // Remove the fullscreen class
    if (hide) {
    hide.removeAttribute('id'); // Remove the id entirely
    }

    hide2.forEach(thing => {
    thing.removeAttribute('id')})

    if (show) {
    show.style.display = 'none';
    }
  }, 1000); // 5000ms = 5 seconds

});