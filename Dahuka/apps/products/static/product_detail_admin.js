console.log("Dahuka Admin JS v1.0.2 - Initialization Started");

function toggleAcc(header) {
    const item = header.parentElement;
    const content = item.querySelector('.acc-content');
    const chevron = header.querySelector('.icon-chevron');
    
    if (content) {
        const isShow = content.classList.contains('show');
        content.classList.toggle('show', !isShow);
        chevron.classList.toggle('fa-chevron-down', !isShow);
        chevron.classList.toggle('fa-chevron-right', isShow);
    }
}

function updateToggleTxt(input) {
    const txt = document.getElementById('toggleTxt');
    if (txt) {
        if (input && input.type === 'checkbox') {
            txt.innerText = input.checked ? 'Hiển thị trên website' : 'Ẩn khỏi website';
        }
    }
}

function showToast() {
    const toast = document.getElementById('saveToast');
    if (toast) {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
}

function initAdminGallery() {
    const gallerySections = document.querySelectorAll('.thumb-list');
    gallerySections.forEach(thumbList => {
        const addBtn = thumbList.querySelector('.add-btn');
        const type = thumbList.getAttribute('data-type'); 
        
        if (addBtn && type && !thumbList.querySelector('input[type="file"]')) {
            const input = document.createElement('input');
            input.type = 'file';
            input.name = type + '_images';
            input.multiple = true;
            input.accept = 'image/*';
            input.style.display = 'none';
            thumbList.appendChild(input);

            addBtn.addEventListener('click', () => input.click());

            input.addEventListener('change', function() {
                const files = Array.from(this.files);
                files.forEach((file, index) => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const newItem = document.createElement('div');
                        newItem.className = 'thumb-item newly-added';
                        // Gắn nút xóa cho ảnh vừa thêm (chưa lưu)
                        newItem.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <button type="button" class="btn-delete-thumb" onclick="removeNewPreview(this)" title="Gỡ ảnh này">
                                <i class="fa fa-times"></i>
                            </button>
                        `;
                        thumbList.insertBefore(newItem, addBtn);
                    };
                    reader.readAsDataURL(file);
                });
            });
        }
    });
}

// Hàm gỡ ảnh preview chưa lưu
function removeNewPreview(btn) {
    const item = btn.closest('.thumb-item');
    item.style.opacity = '0';
    item.style.transform = 'scale(0.8)';
    setTimeout(() => item.remove(), 200);
}

function initFeaturedToggle() {
    // Tìm input is_active bằng nhiều cách
    const activeToggle = document.querySelector('input[name="is_active"]') || 
                         document.getElementById('id_is_active') || 
                         document.querySelector('.ios-toggle[name="is_active"]');
    
    const featuredToggle = document.querySelector('input[name="is_featured"]') || 
                           document.getElementById('id_is_featured');
    
    const featuredSection = document.getElementById('featuredSection');

    if (!activeToggle || !featuredSection) {
        console.warn("Featured Toggle Elements Not Found:", { activeToggle, featuredSection });
        return;
    }

    function syncFeaturedUI() {
        console.log("Syncing UI - is_active status:", activeToggle.checked);
        if (activeToggle.checked) {
            featuredSection.style.setProperty('display', 'flex', 'important');
        } else {
            featuredSection.style.setProperty('display', 'none', 'important');
            if (featuredToggle) {
                featuredToggle.checked = false;
            }
        }
    }

    // Gán sự kiện
    activeToggle.addEventListener('change', function() {
        updateToggleTxt(this);
        syncFeaturedUI();
    });

    // Chạy lần đầu
    syncFeaturedUI();
}

// Chạy khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Content Loaded - Running Inits");
    
    // Khởi tạo các thư mục ảnh
    initAdminGallery();
    
    // Khởi tạo Logic ẩn/hiện mục nổi bật
    initFeaturedToggle();
    
    // Logic xem trước ảnh chính
    const mainImgInput = document.querySelector('input[name="image"]') || document.getElementById('id_image');
    const mainImgPreview = document.getElementById('mainProductImage');
    if (mainImgInput && mainImgPreview) {
        mainImgInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => mainImgPreview.src = e.target.result;
                reader.readAsDataURL(file);
            }
        });
    }
});

// Chạy thêm một lần nữa khi toàn bộ trang (bao gồm cả css/script khác) load xong
window.addEventListener('load', function() {
    console.log("Window Loaded - Final Sync");
    initFeaturedToggle();
});
