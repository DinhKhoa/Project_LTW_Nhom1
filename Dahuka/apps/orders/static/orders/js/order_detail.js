(function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    window.showToast = function(message, type = 'success') {
        const toast = document.getElementById('orderToast');
        if (!toast) return;
        
        toast.textContent = message;
        let bg = '#0f8b52'; 
        if (type === 'error') bg = '#dc2626'; 
        if (type === 'warning') bg = '#f59e0b'; 
        
        toast.style.background = bg;
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
        toast.style.pointerEvents = 'auto';
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            toast.style.pointerEvents = 'none';
        }, 3000);
    };

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

    async function performAjaxAction(action, payload = {}, btn = null) {
        if (btn) toggleLoading(btn, true);

        let formData;
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
                
                if (typeof updateUIAfterAction === 'function') {
                    updateUIAfterAction(data, action, payload);
                }

                document.querySelectorAll('.modal.show').forEach(m => m.classList.remove('show'));
                
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

    function updateUIAfterAction(data, action, payload) {
        const steps = document.querySelectorAll('.order-status-step');
        const currentStep = data.current_step;
        steps.forEach((step, index) => {
            if (index <= currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        const statusValue = document.querySelector('.summary-value .highlight');
        if (statusValue && data.order_status) {
        }

        if (action === 'assign_staff') {
            const staffValue = document.querySelectorAll('.summary-value')[0]; 
            if (staffValue && selectedStaffLabel) {
                staffValue.textContent = selectedStaffLabel.textContent;
            }
            setTimeout(() => window.location.reload(), 1500);
        }

        const rawStatus = data.order_status_raw;
        const orderActions = document.querySelector('.order-actions');
        if (orderActions) {
            if (rawStatus === 'confirmed') {
                const assignForm = document.getElementById('assignStaffForm');
                if (assignForm) assignForm.remove();
            }
        }
    }

    const staffSelectWrapper = document.getElementById('staffSelectWrapper');
    const staffSelectTrigger = document.getElementById('staffSelectTrigger');
    const staffSelectValue = document.getElementById('staffSelectValue');
    const selectedStaffLabel = document.getElementById('selectedStaffLabel');
    const staffOptions = document.querySelectorAll('.staff-option');

    if (staffSelectTrigger) {
        staffSelectTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            staffSelectWrapper.classList.toggle('open');
        });

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

        document.addEventListener('click', function() {
            staffSelectWrapper.classList.remove('open');
        });
    }

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

    const confirmStartShippingBtn = document.getElementById('confirmStartShippingBtn');
    if (confirmStartShippingBtn) {
        confirmStartShippingBtn.addEventListener('click', function () {
            performAjaxAction('start_shipping', {}, confirmStartShippingBtn);
        });
    }

    const submitCompleteBtn = document.getElementById('submitCompleteBtn');
    if (submitCompleteBtn) {
        submitCompleteBtn.addEventListener('click', function () {
            const fileInput = document.getElementById('proofImageInput');
            if (!fileInput.files || fileInput.files.length === 0) {
                window.showToast('Vui lòng tải lên ảnh minh chứng hoàn thành.', 'warning');
                return;
            }
            
            const completeForm = document.getElementById('completeTaskForm');
            const formData = new FormData(completeForm);
            
            performAjaxAction('complete', formData, submitCompleteBtn);
        });
    }

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

    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('show');
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('show');
    };

    document.querySelectorAll('.close-modal, [data-close]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-close') || this.closest('.modal').id;
            closeModal(modalId);
        });
    });

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
