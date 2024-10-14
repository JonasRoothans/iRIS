function toggleRowsById(id, buttonElem) {
    const rows = document.querySelectorAll(`tr[id="${id}"]`);
    let hidden = false;

    // Toggle the visibility for the specific set of rows
    rows.forEach(row => {
        row.classList.toggle('hidden');
        if (row.classList.contains('hidden')) {
            hidden = true;
        }
    });

    // Update button appearance based on row visibility
    if (hidden) {
        buttonElem.style.backgroundColor = 'grey';
        buttonElem.innerText = `Toon ${id}`;
    } else {
        buttonElem.style.backgroundColor = 'red';
        buttonElem.innerText = `Verberg ${id}`;
    }
}