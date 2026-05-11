// Logic quản lý tính năng so sánh sản phẩm toàn cục cho hệ thống Dahuka
// Giới hạn số lượng sản phẩm tối đa có thể so sánh cùng lúc
const MAX_COMPARE = 3;

/**
 * Hàm đồng bộ trạng thái so sánh từ LocalStorage lên giao diện (Compare Bar)
 * Được gọi mỗi khi có thay đổi (thêm/xóa sản phẩm) hoặc khi tải lại trang.
 */
function syncGlobalCompare() {
    // Lấy danh sách ID sản phẩm từ LocalStorage (được lưu dưới dạng chuỗi JSON)
    const items = JSON.parse(localStorage.getItem('compareItems') || '[]');
    const bar = document.getElementById('compareBar');
    const list = document.getElementById('compareItemsList');
    const countLabel = document.getElementById('compareCountLabel');
    const btnGo = document.getElementById('btnCompareGo');
    const form = document.getElementById('compareForm');

    if (!bar) return;

    // 1. Hiển thị hoặc ẩn thanh Compare Bar dựa trên việc có sản phẩm nào được chọn hay không
    if (items.length > 0) {
        bar.classList.add('active');
    } else {
        bar.classList.remove('active');
    }

    // Cập nhật nhãn hiển thị số lượng
    if (countLabel) countLabel.textContent = `Đã chọn ${items.length} sản phẩm`;

    // 2. Kiểm soát nút "So sánh ngay": Chỉ cho phép bấm khi có ít nhất 2 sản phẩm
    if (btnGo) {
        if (items.length >= 2) {
            btnGo.style.opacity = '1';
            btnGo.style.pointerEvents = 'auto';
        } else {
            btnGo.style.opacity = '0.5';
            btnGo.style.pointerEvents = 'none';
        }
    }

    // 3. Cập nhật các input ẩn (hidden) trong Form để khi người dùng nhấn "So sánh", 
    // các ID này sẽ được gửi lên server qua phương thức GET/POST.
    if (form) {
        const container = document.getElementById('hiddenIdInputs') || form;
        // Xóa sạch các input cũ trước khi tạo mới
        container.querySelectorAll('input[name="id"]').forEach(el => el.remove());
        items.forEach(item => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'id';
            input.value = item.id;
            container.appendChild(input);
        });
    }

    // 4. Render danh sách ảnh sản phẩm thu nhỏ trên thanh Bar
    if (list) {
        list.innerHTML = '';
        items.forEach(item => {
            const el = document.createElement('div');
            el.className = 'compare-item-card';
            el.innerHTML = `
                <img src="${item.img}" alt="product" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">
                <div class="remove-item" data-id="${item.id}"><i class="fa fa-times"></i></div>
            `;
            list.appendChild(el);
        });
        
        // Tạo các ô trống (Empty Slots) nếu số lượng chọn < MAX_COMPARE để giữ layout cân đối
        for (let i = items.length; i < MAX_COMPARE; i++) {
            const empty = document.createElement('div');
            empty.className = 'compare-item-card empty-slot';
            list.appendChild(empty);
        }
    }
}

/**
 * Lắng nghe sự kiện CLICK toàn cục (Event Delegation)
 * Giúp tối ưu hiệu năng: không cần gắn sự kiện vào từng nút riêng lẻ.
 */
document.addEventListener('click', function(e) {
    // TRƯỜNG HỢP 1: Nhấn nút "Thêm vào so sánh" trên card sản phẩm
    const addBtn = e.target.closest('.compare-btn');
    if (addBtn) {
        const card = addBtn.closest('[data-id]');
        if (!card) return;
        
        const pid = card.getAttribute('data-id');
        const pimg = card.getAttribute('data-img') || '/static/img/no-image.png';
        if (!pid) return;

        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        
        // Kiểm tra xem sản phẩm đã tồn tại trong danh sách chưa
        if (items.find(i => String(i.id) === String(pid))) {
            window.showToast('Sản phẩm này đã có trong danh sách so sánh!', 'warning');
            return;
        }

        // Kiểm tra giới hạn số lượng
        if (items.length >= MAX_COMPARE) {
            window.showToast(`Bạn chỉ có thể so sánh tối đa ${MAX_COMPARE} sản phẩm!`, 'error');
            return;
        }

        // Thêm mới và lưu lại vào LocalStorage
        items.push({ id: String(pid), img: pimg });
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncGlobalCompare();
        
        window.showToast('Đã thêm sản phẩm vào danh sách so sánh', 'success');
    }

    // TRƯỜNG HỢP 2: Nhấn nút Xóa (X) trên thanh Compare Bar
    const removeBtn = e.target.closest('.remove-item');
    if (removeBtn) {
        const pid = removeBtn.getAttribute('data-id');
        let items = JSON.parse(localStorage.getItem('compareItems') || '[]');
        // Lọc bỏ sản phẩm có ID trùng khớp
        items = items.filter(i => String(i.id) !== String(pid));
        localStorage.setItem('compareItems', JSON.stringify(items));
        syncGlobalCompare();
    }

    // TRƯỜNG HỢP 3: Nhấn nút "Xóa tất cả"
    if (e.target.id === 'btnClearAll') {
        localStorage.removeItem('compareItems');
        syncGlobalCompare();
        window.showToast('Đã xóa danh sách so sánh', 'success');
    }
});

// Khi trang web tải xong, thực hiện đồng bộ lần đầu để hiển thị lại các sản phẩm cũ (nếu có)
document.addEventListener('DOMContentLoaded', syncGlobalCompare);
