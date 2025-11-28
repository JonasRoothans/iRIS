document.addEventListener('DOMContentLoaded', function () {
    const collapsibleDivs = document.querySelectorAll('.collapsible');
    const closeButtons = document.querySelectorAll('.close-button');

    // Add click event to collapsible divs
    collapsibleDivs.forEach(function (div) {
        div.addEventListener('click', function (event) {
            // Prevent the collapse/expand functionality if the click is on a link or close button
            if (event.target.tagName === 'A' || event.target.closest('a') || event.target.classList.contains('close-button')) {
                event.stopPropagation(); // Stop the click from bubbling to the parent div
                return;
            }

            // Prevent click functionality if the div is already expanded
            if (div.classList.contains('expanded')) {
                return;
            }

            if (div.id=='parent'){
                event.stopPropagation()

                const anchor = div.querySelector('a')
                if (anchor) {
                    const href = anchor.getAttribute('href'); // Get the href
                    if (href) {
                        window.location.href = href; // Navigate to the href URL
                    }
                }


                return;
            }



            // Collapse other expanded collapsible divs
            collapsibleDivs.forEach(function (other) {
                if (other !== div && other.classList.contains('expanded')) {
                    other.classList.remove('expanded');
                    other.querySelectorAll('.hidden-content').forEach(function (hiddenDiv) {
                        hiddenDiv.classList.remove('show');
                    });
                }
            });

            // Expand this div
            div.classList.add('expanded');

            // Smooth scroll into view when expanded
            const stickyHeaderHeight = 150; // Adjust this value to match the height of your sticky header
            const elementPosition = div.getBoundingClientRect().top + window.scrollY; // Element's position on the page
            const offsetPosition = elementPosition - stickyHeaderHeight;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });

            // Show hidden content
            div.querySelectorAll('.hidden-content').forEach(function (hiddenDiv) {
                hiddenDiv.classList.add('show');
            });
        });
    });

    // Add click event to close buttons
    closeButtons.forEach(function (btn) {
        btn.addEventListener('click', function (event) {
            event.stopPropagation(); // Prevent triggering the parent div's click event

            // Get the parent collapsible div
            const parentDiv = btn.closest('.collapsible');
            if (parentDiv && parentDiv.classList.contains('expanded')) {
                // Collapse the parent div
                parentDiv.classList.remove('expanded');
                parentDiv.querySelectorAll('.hidden-content').forEach(function (hiddenDiv) {
                    hiddenDiv.classList.remove('show');
                });
            }
        });
    });

    const segments = document.querySelectorAll('.bar-segment');
    const relatedDivs = document.querySelectorAll('.hidden-content');

        segments.forEach(segment => {
            segment.addEventListener('click', (event) => {
                console.log(`Clicked segment with ID: ${segment.id}`);


                relatedDivs.forEach(div => {
                    div.classList.remove('showflex');
                    if (div.id == segment.id){
                    div.classList.add('showflex')}

                });


            });
        })
});