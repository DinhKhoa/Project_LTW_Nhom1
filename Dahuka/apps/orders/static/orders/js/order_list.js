/**
 * JAVASCRIPT CHO TRANG DANH SÁCH ĐƠN HÀNG (ORDER LIST JAVASCRIPT)
 * Xử lý: Biểu đồ thống kê (Chart.js) và Bộ lọc tìm kiếm linh hoạt.
 * Handles: Statistical charts (Chart.js) and flexible search filters.
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // --- PHẦN 1: LẤY DỮ LIỆU TỪ DJANGO (PART 1: DATA EXTRACTION) ---
    /**
     * Hàm hỗ trợ lấy dữ liệu JSON được nhúng trong thẻ <script id="..."> ở HTML.
     * Helper function to extract JSON data embedded in <script id="..."> tags in HTML.
     * @param {string} id - ID của thẻ script chứa dữ liệu / ID of the script tag.
     */
    const getStats = (id) => {
        const el = document.getElementById(id);
        // Chuyển đổi chuỗi văn bản JSON sang đối tượng Javascript (số lượng)
        // Converts JSON string content into a Javascript object/number
        return el ? JSON.parse(el.textContent) : 0;
    };

    // Lấy số lượng đơn hàng theo từng trạng thái từ các thẻ script ẩn để vẽ biểu đồ
    // Retrieve order counts by status from hidden script tags for chart rendering
    const pending = getStats('pending-data');
    const confirmed = getStats('confirmed-data');
    const processing = getStats('processing-data');
    const completed = getStats('completed-data');
    const cancelled = getStats('cancelled-data');

    // --- PHẦN 2: KHỞI TẠO BIỂU ĐỒ (CHART.JS) (PART 2: CHART INITIALIZATION) ---
    const chartCanvas = document.getElementById('orderPieChart');
    if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut', // Loại biểu đồ: Hình vòng khuyết (Doughnut chart type)
            data: {
                labels: ['Chờ xử lý', 'Đã xác nhận', 'Đang giao', 'Hoàn thành', 'Đã hủy'],
                datasets: [{
                    // Dữ liệu thực tế tương ứng với các nhãn trên
                    // Actual data corresponding to the labels above
                    data: [pending, confirmed, processing, completed, cancelled],
                    // Bảng màu nhận diện cho từng trạng thái / Color palette for each status
                    backgroundColor: ['#d97706', '#3b82f6', '#8b5cf6', '#059669', '#dc2626'],
                    borderWidth: 0, // Không dùng đường viền giữa các phần / No borders between slices
                    hoverOffset: 4  // Hiệu ứng nhô ra khi di chuột vào / Pop-out effect on hover
                }]
            },
            options: {
                responsive: true, // Tự động co giãn theo kích thước màn hình / Auto-resize with screen
                maintainAspectRatio: false, // Cho phép tùy chỉnh tỉ lệ khung hình / Allow custom aspect ratio
                plugins: {
                    legend: { display: false }, // Ẩn chú giải mặc định của Chart.js để tự làm bằng HTML/CSS
                    tooltip: { enabled: true }  // Hiện thông tin chi tiết khi di chuột vào từng phần
                },
                cutout: '70%', // Độ lớn của lỗ hổng ở giữa (70% bán kính) / Center hole radius
                
                /**
                 * SỰ KIỆN CLICK (CLICK EVENT):
                 * Khi người dùng nhấn vào một phần của biểu đồ, trang web sẽ tự động lọc danh sách theo trạng thái đó.
                 * Clicking a chart slice will automatically filter the order list by that status.
                 */
                onClick: (evt, activeElements, chart) => {
                    if (activeElements.length > 0) {
                        const index = activeElements[0].index;
                        const label = chart.data.labels[index];
                        // Bản đồ ánh xạ nhãn hiển thị sang giá trị lưu trong Database
                        // Mapping display labels to Database status values
                        const statusMap = {
                            'Chờ xử lý': 'pending',
                            'Đã xác nhận': 'confirmed',
                            'Đang giao': 'processing',
                            'Hoàn thành': 'completed',
                            'Đã hủy': 'cancelled'
                        };
                        const status = statusMap[label];
                        if (status) {
                            // Chuyển hướng trình duyệt kèm tham số lọc trên URL
                            // Redirect browser with filter parameters in the URL
                            window.location.href = `?trang_thai=${status}`;
                        }
                    }
                }
            }
        });
    }

    // --- PHẦN 3: XỬ LÝ DROPDOWN BỘ LỌC TÙY CHỈNH (PART 3: CUSTOM FILTER DROPDOWN) ---
    
    /**
     * Hàm Đóng/Mở menu thả xuống khi nhấn vào nút lọc.
     * Function to toggle the dropdown menu visibility on button click.
     * @param {string} id - ID của khối bao ngoài dropdown / ID of the dropdown wrapper.
     */
    window.toggleFilterDropdown = function(id) {
        const wrapper = document.getElementById(id);
        if (!wrapper) return;
        
        const btn = wrapper.querySelector('.filter-dropdown-btn');
        const menu = wrapper.querySelector('.filter-dropdown-menu');

        /**
         * Logic: Duyệt và đóng tất cả các dropdown khác đang mở để tránh xung đột giao diện.
         * Logic: Close all other open dropdowns to prevent UI overlap.
         */
        document.querySelectorAll('.filter-dropdown-wrapper').forEach(function (w) {
            if (w.id !== id) {
                w.querySelector('.filter-dropdown-btn').classList.remove('open');
                w.querySelector('.filter-dropdown-menu').classList.remove('show');
            }
        });

        // Đảo ngược trạng thái hiển thị (Đóng <-> Mở) / Toggle visibility state
        btn.classList.toggle('open');
        menu.classList.toggle('show');
    };

    /**
     * Hàm xử lý khi người dùng chọn một mục trong danh sách lọc.
     * Function to handle item selection from the custom filter list.
     * @param {HTMLElement} item - Phần tử vừa được nhấn / The clicked element.
     * @param {string} wrapperId - ID của khối bao ngoài / Parent wrapper ID.
     */
    window.selectFilterItem = function(item, wrapperId) {
        const wrapper = document.getElementById(wrapperId);
        const value = item.getAttribute('data-value');
        // Tìm thẻ <select> ẩn trong form HTML để gán giá trị thực tế
        // Find the hidden <select> tag in HTML form to assign the real value
        const realSelect = document.querySelector('select[name="trang_thai"]');
        
        if (realSelect) {
            const form = realSelect.closest('form');
            if (wrapper) {
                // Cập nhật giao diện: Đánh dấu mục đang được chọn (active)
                // Update UI: Highlight the selected item
                wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
            }
            // Gán giá trị vào thẻ <select> thật để chuẩn bị gửi về server Django
            // Set value to the real <select> for Django backend to process
            realSelect.value = value;
            form.submit(); // Tự động gửi Form (Auto-submit)
        }
    };

    /**
     * Sự kiện click toàn cầu: Tự động đóng dropdown nếu người dùng nhấn ra ngoài vùng menu.
     * Global click event: Automatically close dropdowns if the user clicks outside the menu area.
     */
    document.addEventListener('click', function(e) {
        // Nếu điểm nhấn không nằm trong bất kỳ dropdown nào / If click is not inside a dropdown wrapper
        if (!e.target.closest('.filter-dropdown-wrapper')) {
            document.querySelectorAll('.filter-dropdown-wrapper').forEach(function(w) {
                w.querySelector('.filter-dropdown-btn').classList.remove('open');
                w.querySelector('.filter-dropdown-menu').classList.remove('show');
            });
        }
    });
});
