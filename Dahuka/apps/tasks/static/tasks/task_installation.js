/**
 * Task Management JavaScript
 * Handles filtering and searching in the task list
 */

document.addEventListener('DOMContentLoaded', function() {
    const jobSearch = document.getElementById('jobSearch');
    if (jobSearch) {
        jobSearch.addEventListener('input', applyJobFilters);
    }

    // Row navigation logic
    document.addEventListener('click', function(e) {
        const row = e.target.closest('.clickable-row');
        if (row && row.dataset.href) {
            window.location = row.dataset.href;
        }
    });

    // Close dropdowns on outside click
    window.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown-wrapper')) {
            document.querySelectorAll('.filter-dropdown-btn').forEach(btn => btn.classList.remove('open'));
            document.querySelectorAll('.filter-dropdown-menu').forEach(menu => menu.classList.remove('show'));
        }
    });
});

/**
 * Toggles the visibility of a filter dropdown
 * @param {string} id - The ID of the dropdown wrapper
 */
window.toggleFilterDropdown = function(id) {
    const wrapper = document.getElementById(id);
    if (!wrapper) return;
    wrapper.querySelector('.filter-dropdown-btn').classList.toggle('open');
    wrapper.querySelector('.filter-dropdown-menu').classList.toggle('show');
}

/**
 * Quickly applies a filter from the summary cards
 * @param {string} status - The status value to filter by
 */
window.quickFilter = function(status) {
    const item = document.querySelector(`#statusFilter .filter-item[data-value="${status}"]`);
    if (item) {
        selectJobFilter(item);
    }
}

/**
 * Selects a filter item and applies the filters
 * @param {HTMLElement} item - The clicked filter item element
 */
window.selectJobFilter = function(item) {
    const wrapper = item.closest('.filter-dropdown-wrapper');
    const items = wrapper.querySelectorAll('.filter-item');
    items.forEach(i => i.classList.remove('selected'));
    item.classList.add('selected');
    
    // Only get the text content of the filter name, excluding the checkmark
    const filterName = item.childNodes[0].textContent.trim();
    wrapper.querySelector('.filter-value').textContent = filterName;
    
    toggleFilterDropdown(wrapper.id);
    applyJobFilters();
}

/**
 * Applies both search and status filters to the table rows
 */
window.applyJobFilters = function() {
    const searchInput = document.getElementById('jobSearch');
    const selectedItem = document.querySelector('#statusFilter .filter-item.selected');
    
    if (!searchInput || !selectedItem) return;

    const keyword = searchInput.value.toLowerCase();
    const status = selectedItem.dataset.value;
    const rows = document.querySelectorAll('#jobTableBody tr');

    rows.forEach(row => {
        // Skip empty state row if it exists
        if (row.cells.length < 2) return;

        const rowText = row.textContent.toLowerCase();
        const rowStatus = row.dataset.status;
        
        const matchesSearch = rowText.includes(keyword);
        const matchesStatus = status === 'all' || rowStatus === status;

        row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    });
}