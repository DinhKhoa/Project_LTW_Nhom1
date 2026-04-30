window.toggleFilterDropdown = function(id) {
    var wrapper = document.getElementById(id);
    var btn = wrapper.querySelector('.filter-dropdown-btn');
    var menu = wrapper.querySelector('.filter-dropdown-menu');

    document.querySelectorAll('.filter-dropdown-wrapper').forEach(function (w) {
        if (w.id !== id) {
            w.querySelector('.filter-dropdown-btn').classList.remove('open');
            w.querySelector('.filter-dropdown-menu').classList.remove('show');
        }
    });

    btn.classList.toggle('open');
    menu.classList.toggle('show');
};

window.selectFilterItem = function(item, wrapperId) {
    var wrapper = document.getElementById(wrapperId);
    var value = item.getAttribute('data-value');
    var realSelect = document.getElementById('realStatusSelect');
    var form = realSelect.closest('form');

    wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
    item.classList.add('selected');

    // Update hidden select and submit
    realSelect.value = value;
    form.submit();
};

document.addEventListener('DOMContentLoaded', function() {
    // Close on outside click
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown-wrapper')) {
            document.querySelectorAll('.filter-dropdown-wrapper').forEach(function(w) {
                w.querySelector('.filter-dropdown-btn').classList.remove('open');
                w.querySelector('.filter-dropdown-menu').classList.remove('show');
            });
        }
    });
});
