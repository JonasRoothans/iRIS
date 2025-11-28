document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('raadsvergaderingvideo');
    const links = document.querySelectorAll('.jump-link'); // All links
    const speaker_photo = document.getElementById('speaker-photo'); // Speaker photo element
    const speaker_name = document.getElementById('speaker-name'); // Speaker name element
    const speaker_party = document.getElementById('speaker-party'); // Speaker party element
    const subject_title = document.getElementById('subject-title');
    const subject_poho = document.getElementById('subject-poho');
    const subject_info = document.getElementById('subject-info');
    const stickyVideoHeight = 375; // Height of the sticky video at the top
    const speakerBox = document.getElementById('speakingbox');
    const subjectBox = document.getElementById('subjectbox');
    let userScrolling = false; // Flag to track active user scrolling
    let scrollTimeout = null; // Timer for resetting scrolling inactivity

    // Listen for user scroll events
    window.addEventListener('scroll', function () {
        userScrolling = true;

        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }

        scrollTimeout = setTimeout(function () {
            userScrolling = false;
        }, 3000);
    });

    // Helper function: Update subtitles, speakers, and agenda items based on current time
    function updateContent(currentTime) {
        let closestLink = null;
        let closestTimestamp = -Infinity;

        links.forEach(link => {
            const timestamp = parseFloat(link.getAttribute('data-timestamp'));

            if (timestamp <= currentTime && timestamp > closestTimestamp) {
                closestLink = link;
                closestTimestamp = timestamp;
            }
        });

        if (closestLink) {
            // Highlight the subtitle that matches the current timestamp
            links.forEach(link => link.classList.remove('highlight'));
            closestLink.classList.add('highlight');

            // Check if the closest link is an agenda item (`ai`) or speaker
            if (!closestLink.dataset.speaker) {
                if (closestLink.id === 'ai') {
                    if (closestLink.dataset.moduleid) {
                        subject_title.textContent = closestLink.dataset.title;
                        subject_title.setAttribute('href', '../' + closestLink.dataset.moduleid + '.html');
                        subject_poho.src = closestLink.dataset.photo || '../missingphoto.png';
                        subjectBox.classList.add('visible');
                    } else {
                        subjectBox.classList.remove('visible');
                    }
                } else {
                    speakerBox.classList.remove('visible');
                }
            } else {
                // Update speaker information
                speaker_photo.src = closestLink.dataset.photo || '../missingphoto.png';
                speaker_name.textContent = closestLink.dataset.speaker;
                speaker_name.setAttribute('href', '../' + closestLink.dataset.memberid + '.html');
                speaker_party.textContent = closestLink.dataset.party || '';
                speaker_name.style.color = closestLink.dataset.color;
                speaker_photo.style.borderColor = closestLink.dataset.color;
                speakerBox.classList.add('visible');
            }

            // Scroll the link into view if the user is not actively scrolling
            if (!userScrolling) {
                const linkRect = closestLink.getBoundingClientRect();
                const absoluteElementTop = window.scrollY + linkRect.top;
                const scrollTarget = absoluteElementTop - stickyVideoHeight;

                if (
                    linkRect.top < stickyVideoHeight || // Above viewport
                    linkRect.bottom > window.innerHeight // Below viewport
                ) {
                    window.scrollTo({
                        top: scrollTarget,
                        behavior: 'smooth'
                    });
                }
            }
        }
    }

    // Helper function: Always update the latest agenda item (`ai`)
    function updateLatestAgendaItem(currentTime) {
        let latestAgendaItem = null;
        let latestTimestamp = -Infinity;

        links.forEach(link => {
            const timestamp = parseFloat(link.getAttribute('data-timestamp'));

            if (link.id === 'ai' && timestamp <= currentTime && timestamp > latestTimestamp) {
                latestAgendaItem = link;
                latestTimestamp = timestamp;
            }
        });

        if (latestAgendaItem) {
            // Update the agenda item information
            subject_title.textContent = latestAgendaItem.dataset.title;

            if (latestAgendaItem.dataset.moduleid) {
                // If moduleid exists, create a valid link
                subject_title.setAttribute('href', '../' + latestAgendaItem.dataset.moduleid + '.html');
                subject_title.style.pointerEvents = 'auto'; // Enable clicking on the link
            } else {
                // If moduleid is empty, make the link inactive
                subject_title.removeAttribute('href'); // Remove the href attribute
                subject_title.style.pointerEvents = 'none'; // Disable pointer events (clicking)
            }
            subject_poho.src = latestAgendaItem.dataset.photo || '../missingphoto.png';
            subjectBox.classList.add('visible');
        } else {
            // If no agenda item matches, hide the box
            subjectBox.classList.remove('visible');
        }
    }

    // Event listener: Update speaker and agenda info during playback (`timeupdate`)
    video.addEventListener('timeupdate', function () {
        const currentTime = video.currentTime;
        updateContent(currentTime); // Update speaker/subtitles
        updateLatestAgendaItem(currentTime); // Always update the latest agenda item
    });

    // Event listener: Subtitle/other interactions trigger video time jump
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const timestamp = parseFloat(link.getAttribute('data-timestamp'));
            video.currentTime = timestamp; // Jump to the timestamp
            updateContent(timestamp); // Update speaker/subtitles
            updateLatestAgendaItem(timestamp); // Update agenda item
        });
    });

    // Event listener: Handle seeked event (when video timestamp changes)
    video.addEventListener('seeked', function () {
        const currentTime = video.currentTime;
        updateContent(currentTime); // Update speaker/subtitles
        updateLatestAgendaItem(currentTime); // Update agenda item
    });
});