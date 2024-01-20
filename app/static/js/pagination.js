document.addEventListener('DOMContentLoaded', function () {
    const ROWS_PER_PAGE = 3;
    const table = document.querySelector('.evidence-table');
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    let CurrentPage = 1;

    function showPage(page) {
        const start = (page - 1) * ROWS_PER_PAGE;
        const end = start + ROWS_PER_PAGE;

        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? '' : 'none';
        });
    }

    function updatePaginationButtons() {
        const totalPages = Math.ceil(rows.length / ROWS_PER_PAGE);
        const prevButton = document.getElementById('previous-page');
        const nextButton = document.getElementById('Next-page');
        const pageIndicator = document.getElementById('Current-page');

        prevButton.disabled = CurrentPage === 1;
        nextButton.disabled = CurrentPage === totalPages;

        pageIndicator.innerText = `Page ${CurrentPage} of ${totalPages}`;
        pageIndicator.style.color = '#ffffff';
    }

    function goToPage(page) {
        CurrentPage = page;
        showPage(CurrentPage);
        updatePaginationButtons();
    }

    // Initial setup
    showPage(CurrentPage);
    updatePaginationButtons();

    // Event listeners for pagination buttons
    document.getElementById('previous-page').addEventListener('click', () => goToPage(CurrentPage - 1));
    document.getElementById('Next-page').addEventListener('click', () => goToPage(CurrentPage + 1));
});