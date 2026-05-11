// Hàm xử lý đóng/mở Accordion (các phần nội dung co giãn như "Thông số", "Hình ảnh")
function toggleAcc(header) {
    const item = header.parentElement;
    const content = item.querySelector('.acc-content');
    const chevron = header.querySelector('.icon-chevron'); // Biểu tượng mũi tên
    
    if (content) {
        const isShow = content.classList.contains('show');
        content.classList.toggle('show', !isShow); // Hiện nếu đang ẩn và ngược lại
        chevron.classList.toggle('fa-chevron-down', !isShow); // Quay mũi tên xuống
        chevron.classList.toggle('fa-chevron-right', isShow); // Quay mũi tên sang phải
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

// Khởi tạo trình quản lý ảnh Gallery (Cho phép chọn nhiều ảnh và xem trước)
function initAdminGallery() {
    const gallerySections = document.querySelectorAll('.thumb-list[data-type="gallery"]');
    gallerySections.forEach(thumbList => {
        const addBtn = thumbList.querySelector('.add-btn'); // Nút dấu cộng (+)
        if (!addBtn) return;

        // Tạo một ô input file ẩn để người dùng chọn ảnh
        const input = document.createElement('input');
        input.type = 'file';
        input.name = 'gallery_images';
        input.multiple = true; // Cho phép chọn nhiều ảnh cùng lúc
        input.accept = 'image/*';
        input.style.display = 'none';
        thumbList.appendChild(input);

        let dataTransfer = new DataTransfer();

        // Khi nhấn nút cộng (+) thì kích hoạt ô chọn file ẩn
        addBtn.addEventListener('click', () => input.click());

        input.addEventListener('change', function() {
            const files = Array.from(this.files);
            files.forEach((file) => {
                dataTransfer.items.add(file);
                
                // Dùng FileReader để hiển thị ảnh ngay lập tức mà không cần upload lên server trước
                const reader = new FileReader();
                reader.onload = function(e) {
                    const newItem = document.createElement('div');
                    newItem.className = 'thumb-item newly-added has-image';
                    newItem.innerHTML = `
                        <img src="${e.target.result}" alt="Preview">
                        <button type="button" class="btn-delete-thumb" onclick="removeGalleryPreview(this, '${file.name}')">
                            <i class="fa fa-times"></i>
                        </button>
                    `;
                    thumbList.insertBefore(newItem, addBtn); // Chèn ảnh vừa chọn vào danh sách hiển thị
                };
                reader.readAsDataURL(file);
            });
            input.files = dataTransfer.files;
        });

        // Hàm xóa ảnh xem trước khi người dùng nhấn dấu (X)
        window.removeGalleryPreview = function(btn, fileName) {
            const item = btn.closest('.thumb-item');
            
            const newDataTransfer = new DataTransfer();
            Array.from(dataTransfer.files).forEach(f => {
                if (f.name !== fileName) newDataTransfer.items.add(f);
            });
            dataTransfer = newDataTransfer;
            input.files = dataTransfer.files;

            // Hiệu ứng biến mất mượt mà
            item.style.opacity = '0';
            item.style.transform = 'scale(0.8)';
            setTimeout(() => item.remove(), 200);
        };
    });
}

function initFeaturedToggle() {
    const activeToggle = document.querySelector('input[name="is_active"]') ||
                         document.getElementById('id_is_active');
    const featuredToggle = document.querySelector('input[name="is_featured"]') ||
                           document.getElementById('id_is_featured');
    const featuredSection = document.getElementById('featuredSection');

    if (!activeToggle || !featuredSection) return;

    function syncFeaturedUI() {
        if (activeToggle.checked) {
            featuredSection.style.setProperty('display', 'flex', 'important');
        } else {
            featuredSection.style.setProperty('display', 'none', 'important');
            if (featuredToggle) featuredToggle.checked = false;
        }
    }

    activeToggle.addEventListener('change', function() {
        updateToggleTxt(this);
        syncFeaturedUI();
    });

    syncFeaturedUI();
}

document.addEventListener('DOMContentLoaded', function() {
    initAdminGallery();
    initFeaturedToggle();

    // Logic xem trước ảnh chính
    const mainImgInput = document.querySelector('input[name="image"]') || document.getElementById('id_image');
    if (mainImgInput) {
        mainImgInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    // Cập nhật ảnh chính to
                    const mainImgBox = document.querySelector('.image-box');
                    if (mainImgBox) {
                        mainImgBox.innerHTML = `<img src="${e.target.result}" alt="Preview" id="mainProductImage">`;
                    }

                    // Cập nhật ảnh nhỏ trong mục "Ảnh chính" của accordion
                    const thumbContainer = document.querySelector('.thumb-item[onclick*="\'image\'"]');
                    if (thumbContainer) {
                        thumbContainer.classList.remove('empty-state');
                        thumbContainer.classList.add('has-image');
                        thumbContainer.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <button type="button" class="btn-delete-thumb" onclick="clearSingleField(event, 'image')" title="Xóa ảnh">
                                <i class="fa fa-times"></i>
                            </button>
                        `;
                    }
                    console.log("Main Image Preview Updated");
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Logic xem trước các ảnh phụ (thông số, tính năng, mô tả)
    ['image_features', 'image_description'].forEach(fieldName => {
        const input = document.querySelector(`input[name="${fieldName}"]`);
        if (input) {
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    console.log(`Field ${fieldName} Changed - File:`, file.name);
                    const reader = new FileReader();
                    const container = document.querySelector(`.thumb-item[onclick*="${fieldName}"]`);

                    reader.onload = function(e) {
                        if (container) {
                            container.classList.remove('empty-state');
                            container.classList.add('has-image');
                            container.innerHTML = `
                                <img src="${e.target.result}" alt="Preview">
                                <button type="button" class="btn-delete-thumb" onclick="clearSingleField(event, '${fieldName}')" title="Xóa ảnh">
                                    <i class="fa fa-times"></i>
                                </button>
                            `;
                            console.log(`Preview updated for ${fieldName}`);
                        }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    });
});

window.addEventListener('load', function() {
    console.log("Window Loaded - Final Sync");
    initFeaturedToggle();
});