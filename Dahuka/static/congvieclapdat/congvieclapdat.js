document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('jobSearch');
    const filterButtons = document.querySelectorAll('.filter-chip');
    const rows = document.querySelectorAll('#jobTableBody tr');

    let currentFilter = 'all';

    function normalizeText(value) {
        return (value || '').toLowerCase().trim();
    }

    function applyFilters() {
        const keyword = normalizeText(searchInput.value);

        rows.forEach((row) => {
            const rowText = normalizeText(row.textContent);
            const status = row.dataset.status || 'pending';

            const matchesKeyword = !keyword || rowText.includes(keyword);
            const matchesFilter = currentFilter === 'all' || status === currentFilter;

            row.classList.toggle('job-row-hidden', !(matchesKeyword && matchesFilter));
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    filterButtons.forEach((button) => {
        button.addEventListener('click', () => {
            filterButtons.forEach((item) => item.classList.remove('is-active'));
            button.classList.add('is-active');
            currentFilter = button.dataset.filter || 'all';
            applyFilters();
        });
    });
});
