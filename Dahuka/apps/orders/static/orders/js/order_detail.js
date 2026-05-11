/**
 * JAVASCRIPT CHO TRANG CHI TIẾT ĐƠN HÀNG (ORDER DETAIL JAVASCRIPT)
 * Xử lý: Các thao tác AJAX (Giao việc, Giao hàng, Hoàn thành, Hủy đơn).
 * Handles: AJAX operations (Assignment, Shipping, Completion, Cancellation).
 */
(function () {
    /**
     * Lấy Token bảo mật của Django (CSRF) để gửi kèm trong mọi yêu cầu POST.
     * Đây là lớp bảo vệ chống lại các cuộc tấn công giả mạo yêu cầu từ trang web khác.
     * Retrieves Django's CSRF token for secure POST requests to prevent CSRF attacks.
     */
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // --- TIỆN ÍCH UI (UI UTILITIES) ---
    
    /**
     * Hiển thị thông báo Toast nhanh ở góc màn hình.
     * Displays a temporary Toast notification on the screen.
     * @param {string} message - Nội dung thông báo / Notification content.
     * @param {string} type - Loại: success (xanh), error (đỏ), warning (vàng) / Type of toast.
     */
    window.showToast = function(message, type = 'success') {
        const toast = document.getElementById('orderToast');
        if (!toast) return;
        
        toast.textContent = message;
        let bg = '#0f8b52'; // Thành công (Xanh) / Success (Green)
        if (type === 'error') bg = '#dc2626'; // Lỗi (Đỏ) / Error (Red)
        if (type === 'warning') bg = '#f59e0b'; // Cảnh báo (Vàng) / Warning (Yellow)
        
        toast.style.background = bg;
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
        toast.style.pointerEvents = 'auto';
        
        // Tự động ẩn sau 3 giây / Auto-hide after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            toast.style.pointerEvents = 'none';
        }, 3000);
    };

    /**
     * Hiệu ứng Loading cho nút bấm (Vô hiệu hóa nút để tránh người dùng nhấn liên tục).
     * Loading effect for buttons (Disables interaction during processing).
     * @param {HTMLElement} btn - Nút cần tạo hiệu ứng / Target button.
     * @param {boolean} isLoading - Trạng thái loading / Loading state.
     */
    function toggleLoading(btn, isLoading) {
        if (!btn) return;
        if (isLoading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Đang xử lý...';
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
            btn.disabled = false;
        }
    }

    // --- CORE AJAX ENGINE ---
    
    /**
     * Hàm lõi thực hiện gọi API (AJAX) không tải lại trang lên server Django.
     * Core function to perform asynchronous API calls (AJAX) to the Django server.
     * @param {string} action - Tên hành động (assign_staff, complete, v.v.) / Action name.
     * @param {object|FormData} payload - Dữ liệu đi kèm / Data payload.
     * @param {HTMLElement} btn - Nút bấm kích hoạt (để dùng hiệu ứng loading) / Trigger button.
     */
    async function performAjaxAction(action, payload = {}, btn = null) {
        if (btn) toggleLoading(btn, true);

        let formData;
        /**
         * Kiểm tra payload: Nếu là FormData (có chứa File ảnh) thì dùng trực tiếp,
         * nếu là Object thông thường thì chuyển đổi sang FormData.
         * Payload check: Use directly if FormData (for files), otherwise convert object to FormData.
         */
        if (payload instanceof FormData) {
            formData = payload;
            if (!formData.has('csrfmiddlewaretoken')) formData.append('csrfmiddlewaretoken', csrfToken);
            if (!formData.has('action')) formData.append('action', action);
        } else {
            formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfToken);
            formData.append('action', action);
            for (const [key, value] of Object.entries(payload)) {
                formData.append(key, value);
            }
        }

        try {
            /**
             * Sử dụng fetch API để gửi yêu cầu POST bất đồng bộ.
             * Sử dụng Header 'X-Requested-With' để Django nhận diện đây là yêu cầu AJAX.
             * Performs async POST request using fetch API.
             */
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            if (!response.ok) throw new Error('Không thể kết nối đến máy chủ.');
            const data = await response.json();

            if (data.status === 'success') {
                window.showToast(data.message, 'success');
                
                // Cập nhật giao diện động (Thanh tiến trình, trạng thái) ngay lập tức
                // Dynamically updates UI components (Progress bar, status)
                if (typeof updateUIAfterAction === 'function') {
                    updateUIAfterAction(data, action, payload);
                }

                // Tự động đóng các cửa sổ Modal đang mở / Close all active modals
                document.querySelectorAll('.modal.show').forEach(m => m.classList.remove('show'));
                
                /**
                 * Đối với các hành động quan trọng, thực hiện tải lại trang sau 1.5s
                 * để đảm bảo dữ liệu toàn cục được đồng bộ hóa chính xác nhất.
                 * Reload page after 1.5s for major actions to ensure data synchronization.
                 */
                if (['complete', 'cancel', 'start_shipping', 'assign_staff'].includes(action)) {
                    setTimeout(() => window.location.reload(), 1500);
                }
            } else {
                throw new Error(data.message || 'Có lỗi xảy ra.');
            }
        } catch (e) {
            window.showToast(e.message, 'error');
        } finally {
            if (btn) toggleLoading(btn, false);
        }
    }

    /**
     * Cập nhật các thành phần UI (Thanh tiến độ, Trạng thái chữ) sau khi AJAX thành công.
     * Updates UI components (Progress bar, labels) upon successful AJAX response.
     */
    function updateUIAfterAction(data, action, payload) {
        const steps = document.querySelectorAll('.order-status-step');
        const currentStep = data.current_step;
        
        // 1. Cập nhật thanh tiến trình (Progress Bar) / Update the visual progress bar
        steps.forEach((step, index) => {
            if (index <= currentStep) {
                step.classList.add('active'); // Đánh dấu các bước đã hoàn thành / Mark completed steps
            } else {
                step.classList.remove('active');
            }
        });

        // 2. Cập nhật nhãn trạng thái hiển thị bằng tiếng Việt / Update display status label
        const statusValue = document.querySelector('.summary-value .highlight');
        if (statusValue && data.order_status) {
            statusValue.textContent = data.order_status;
        }

        // 3. Xử lý riêng khi Giao việc (Assign Staff) thành công / Handling Staff Assignment
        if (action === 'assign_staff') {
            const staffValue = document.querySelectorAll('.summary-value')[0]; 
            if (staffValue && selectedStaffLabel) {
                staffValue.textContent = selectedStaffLabel.textContent;
            }
        }

        // 4. Dọn dẹp giao diện: Ẩn các nút thao tác đã cũ
        // Interface cleanup: Remove outdated action buttons
        const rawStatus = data.order_status_raw;
        const orderActions = document.querySelector('.order-actions');
        if (orderActions) {
            if (rawStatus === 'confirmed') {
                const assignForm = document.getElementById('assignStaffForm');
                if (assignForm) assignForm.remove();
            }
        }
    }

    // --- XỬ LÝ DROPDOWN CHỌN NHÂN VIÊN (Dành cho Admin) (STAFF SELECTION DROPDOWN) ---
    
    const staffSelectWrapper = document.getElementById('staffSelectWrapper');
    const staffSelectTrigger = document.getElementById('staffSelectTrigger');
    const staffSelectValue = document.getElementById('staffSelectValue');
    const selectedStaffLabel = document.getElementById('selectedStaffLabel');
    const staffOptions = document.querySelectorAll('.staff-option');

    if (staffSelectTrigger) {
        // Mở menu khi nhấn vào trigger / Open menu on click
        staffSelectTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            staffSelectWrapper.classList.toggle('open');
        });

        // Xử lý khi chọn một nhân viên cụ thể / Handle staff option selection
        staffOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.stopPropagation();
                const value = this.dataset.value;
                const name = this.dataset.name;
                
                staffSelectValue.value = value;
                selectedStaffLabel.textContent = name;
                staffSelectWrapper.classList.remove('open');
                
                staffOptions.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
            });
        });

        // Đóng menu nếu click ra ngoài / Close menu if clicking outside
        document.addEventListener('click', function() {
            if (staffSelectWrapper) staffSelectWrapper.classList.remove('open');
        });
    }

    // --- ĐĂNG KÝ SỰ KIỆN CHO CÁC NÚT BẤM (PART 4: EVENT LISTENERS) ---

    // 1. Nút Giao việc cho nhân viên / Staff Assignment Button
    const confirmAssignBtn = document.getElementById('confirmAssignBtn');
    if (confirmAssignBtn) {
        confirmAssignBtn.addEventListener('click', function () {
            if (!staffSelectValue.value) {
                window.showToast('Vui lòng chọn nhân viên để giao việc.', 'warning');
                return;
            }
            performAjaxAction('assign_staff', { 'assigned_staff': staffSelectValue.value }, confirmAssignBtn);
        });
    }

    // 2. Nút Bắt đầu giao hàng / Start Shipping Button
    const confirmStartShippingBtn = document.getElementById('confirmStartShippingBtn');
    if (confirmStartShippingBtn) {
        confirmStartShippingBtn.addEventListener('click', function () {
            performAjaxAction('start_shipping', {}, confirmStartShippingBtn);
        });
    }

    // 3. Nút Hoàn thành (Yêu cầu tải ảnh minh chứng) / Complete Task Button
    const submitCompleteBtn = document.getElementById('submitCompleteBtn');
    if (submitCompleteBtn) {
        submitCompleteBtn.addEventListener('click', function () {
            const fileInput = document.getElementById('proofImageInput');
            // Kiểm tra xem đã có ảnh minh chứng chưa / Check for proof image
            if (!fileInput.files || fileInput.files.length === 0) {
                window.showToast('Vui lòng tải lên ảnh minh chứng hoàn thành.', 'warning');
                return;
            }
            
            const completeForm = document.getElementById('completeTaskForm');
            /**
             * Sử dụng FormData để bao bọc tệp tin ảnh gửi lên server Django.
             * Uses FormData to encapsulate the proof image file for upload.
             */
            const formData = new FormData(completeForm); 
            
            performAjaxAction('complete', formData, submitCompleteBtn);
        });
    }

    // 4. Nút Xác nhận hủy đơn / Cancel Order Button
    const submitSharedCancelBtn = document.getElementById('submitSharedCancelBtn');
    if (submitSharedCancelBtn) {
        submitSharedCancelBtn.addEventListener('click', function () {
            const reason = document.getElementById('sharedCancelReason').value;
            if (!reason.trim()) {
                window.showToast('Vui lòng nhập lý do hủy.', 'warning');
                return;
            }
            
            performAjaxAction('cancel', { 'cancel_reason': reason }, submitSharedCancelBtn);
        });
    }

    // --- TIỆN ÍCH MODAL (MODAL UTILS) ---
    
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('show');
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('show');
    };

    // Tự động gán sự kiện đóng cho các nút có class .close-modal
    // Auto-assign close events to buttons with .close-modal class
    document.querySelectorAll('.close-modal, [data-close]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-close') || this.closest('.modal').id;
            closeModal(modalId);
        });
    });

    /**
     * Xử lý giao diện: Hiển thị tên tệp tin sau khi người dùng chọn ảnh minh chứng.
     * UI Handling: Display the file name after a user selects a proof image.
     */
    const proofImageInput = document.getElementById('proofImageInput');
    const fileNameLabel = document.getElementById('fileNameLabel');
    if (proofImageInput && fileNameLabel) {
        proofImageInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                fileNameLabel.textContent = this.files[0].name;
                fileNameLabel.parentElement.style.borderColor = '#0d734d';
                fileNameLabel.parentElement.style.color = '#0d734d';
            } else {
                fileNameLabel.textContent = 'Chọn ảnh minh chứng...';
                fileNameLabel.parentElement.style.borderColor = '#cbd5e1';
                fileNameLabel.parentElement.style.color = '#64748b';
            }
        });
    }

})();
