document.addEventListener('DOMContentLoaded', function() {
    const getStats = (id) => {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : 0;
    };

    const pending = getStats('pending-data');
    const confirmed = getStats('confirmed-data');
    const processing = getStats('processing-data');
    const completed = getStats('completed-data');
    const cancelled = getStats('cancelled-data');

    const chartCanvas = document.getElementById('orderPieChart');
    if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Chờ xử lý', 'Đã xác nhận', 'Đang giao', 'Hoàn thành', 'Đã hủy'],
                datasets: [{
                    data: [pending, confirmed, processing, completed, cancelled],
                    backgroundColor: ['#d97706', '#3b82f6', '#8b5cf6', '#059669', '#dc2626'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true }
                },
                cutout: '70%',
                onClick: (evt, activeElements, chart) => {
                    if (activeElements.length > 0) {
                        const index = activeElements[0].index;
                        const label = chart.data.labels[index];
                        const statusMap = {
                            'Chờ xử lý': 'pending',
                            'Đã xác nhận': 'confirmed',
                            'Đang giao': 'processing',
                            'Hoàn thành': 'completed',
                            'Đã hủy': 'cancelled'
                        };
                        const status = statusMap[label];
                        if (status) {
                            window.location.href = `?trang_thai=${status}`;
                        }
                    }
                }
            }
        });
    }

    window.toggleFilterDropdown = function(id) {
        const wrapper = document.getElementById(id);
        if (!wrapper) return;
        
        const btn = wrapper.querySelector('.filter-dropdown-btn');
        const menu = wrapper.querySelector('.filter-dropdown-menu');

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
        const wrapper = document.getElementById(wrapperId);
        const value = item.getAttribute('data-value');
        const realSelect = document.querySelector('select[name="trang_thai"]');
        
        if (realSelect) {
            const form = realSelect.closest('form');
            if (wrapper) {
                wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
            }
            realSelect.value = value;
            form.submit();
        }
    };

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown-wrapper')) {
            document.querySelectorAll('.filter-dropdown-wrapper').forEach(function(w) {
                w.querySelector('.filter-dropdown-btn').classList.remove('open');
                w.querySelector('.filter-dropdown-menu').classList.remove('show');
            });
        }
    });
});
