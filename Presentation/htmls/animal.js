document.addEventListener("DOMContentLoaded", () => {
    const animalContainer = document.getElementById("animal-container");



    // Spawn rates (in milliseconds)
    const RATES = {
        chicken: 365*24*60*60*1000 / 492137000,
        pig: 365*24*60*60*1000 / 14749000,
        cow: 365*24*60*60*1000 / (585000 + 1557000)
    };

    const ANIMALS = [
        { type: "chicken", emoji: "🐔", size: 1, rate: RATES.chicken },
        { type: "pig", emoji: "🐖", size: 5, rate: RATES.pig },
        { type: "cow", emoji: "🐄", size: 10, rate: RATES.cow },
    ];

    // Animal counters
    const counters = {
        chicken: 0,
        pig: 0,
        cow: 0,
    };
    function playSoundEffect() {
    const sound = new Audio("sounds/click.mp3"); // Create a new audio instance
    sound.play(); // Play the sound
    }

    // Helper to spawn an emoji animal
    function spawnAnimal(type, emoji, size) {
        const animalElement = document.createElement("div");
        animalElement.classList.add("animal");
        animalElement.textContent = emoji; // Add the emoji directly

        // Apply size (font size scaled appropriately)
        animalElement.style.fontSize = `${size * 10}px`; // Scale size dynamically (1 -> 10px, 10 -> 100px)



        // Random position within the viewport (visible area)
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        const xPos = Math.random() * viewportWidth; // Random horizontal position
        const yPos = Math.random() * viewportHeight; // Random vertical position

        // Position the animal relative to the container
        animalElement.style.left = `${xPos}px`;
        animalElement.style.top = `${yPos + window.scrollY}px`; // Account for scroll position
        animalElement.style.transform = `rotate(${Math.random() * 90 - 45}deg)`; // Random rotation (-45 to +45 degrees)

        // Random rotation (-45 to +45 degrees)
        const rotation = Math.random() * 90 - 45;
        animalElement.style.transform = `rotate(${rotation}deg)`;

        // Append to the container and play sound
        animalContainer.appendChild(animalElement);

        //playSoundEffect()

         // Update counters
        counters[type]++;
        updateBottomBox();

    }

        // Update the bottom sliding box with counters
    function updateBottomBox() {
        const bottomBox = document.getElementById("bottom-box");
        if (counters.cow ==1){
        bottomBox.textContent = `Er zijn in Nederland inmiddels: ${counters.chicken} kippen, ${counters.pig} varkens en ${counters.cow} koe geslacht.`;
        }else{
        bottomBox.textContent = `Er zijn in Nederland inmiddels: ${counters.chicken} kippen, ${counters.pig} varkens en ${counters.cow} koeien geslacht.`;
        }

    }

    // Show the bottom box after 10 seconds
    setTimeout(() => {
        const bottomBox = document.getElementById("bottom-box");
        bottomBox.classList.add("visible"); // Add class to make the box slide up
    }, 10000);


    // Start spawning emoji animals when "Voedsel" button is clicked
    document.querySelector('.voedsel-btn').addEventListener("click", () => {

        const splash = document.querySelector('.splash');
        if (splash) {
            splash.classList.add('hidden-content'); // Add the "hidden-content" class
        }
        const splashbg = document.querySelector('.splash-screen-background');
        if (splashbg) {
            splashbg.classList.add('hidden-content'); // Add the "hidden-content" class
        }



        ANIMALS.forEach((animal) => {
            setInterval(() => spawnAnimal(animal.type, animal.emoji, animal.size), animal.rate);
        });
    });
});