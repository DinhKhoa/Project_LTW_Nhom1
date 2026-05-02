/**
 * Shared JS for handling order actions (Cancel, Assign, Complete)
 */
(function () {
    // 1. Logic for shared cancel modal (Customer, Admin, Staff)
    const cancelReasonArea = document.getElementById('sharedCancelReason');
    const submitCancelBtn = document.getElementById('submitSharedCancelBtn');
    const cancelForm = document.getElementById('sharedCancelForm');

    if (submitCancelBtn && cancelForm) {
        submitCancelBtn.addEventListener('click', function () {
            if (!cancelReasonArea.value.trim()) {
                window.showToast('Vui lòng nhập lý do hủy đơn.', 'warning');
                return;
            }
            
            // For now, let's submit the form normally or prepare for AJAX
            // If we want to use the existing cancel_order view, we need the URL
            // Get the database ID from the data attribute
            const orderLabel = document.querySelector('.order-id-label');
            const orderId = orderLabel.getAttribute('data-order-id');
            const formAction = `/account/purchases/${orderId}/cancel/`; 
            
            const formData = new FormData(cancelForm);
            formData.append('cancel_reason', cancelReasonArea.value);

            // Simple submission for now to keep it working with existing views
            cancelForm.method = 'POST';
            cancelForm.action = formAction;
            
            // Create a hidden input for the reason if the view expects 'cancel_reason'
            const hiddenReason = document.createElement('input');
            hiddenReason.type = 'hidden';
            hiddenReason.name = 'cancel_reason';
            hiddenReason.value = cancelReasonArea.value;
            cancelForm.appendChild(hiddenReason);
            
            cancelForm.submit();
        });
    }

    // 2. Placeholder for other actions (Admin Assign, Staff Progress)
    // These will be implemented in their respective app JS files or here
})();
