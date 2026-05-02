document.addEventListener('DOMContentLoaded', () => {
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';
    const cartEndpoint = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

    // Core AJAX helper
    async function performAction(url, payload) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new URLSearchParams(payload).toString()
        });
        if (!response.ok) throw new Error('Không thể kết nối đến máy chủ.');
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        return data;
    }

    function syncUI(data) {
        // 1. Update totals
        const totalPriceEl = document.getElementById('totalPrice');
        if (totalPriceEl && data.formatted_base_total) {
            totalPriceEl.textContent = `${data.formatted_base_total} đ`;
        }

        const depositAmountText = document.getElementById('depositAmountText');
        if (depositAmountText) {
            depositAmountText.textContent = `${data.formatted_deposit_amount} đ`;
        }

        const depositPercentValue = document.getElementById('depositPercentValue');
        if (depositPercentValue && data.deposit_percent !== undefined) {
            depositPercentValue.textContent = data.deposit_percent;
        }

        // 2. Update caption
        const totalCaptionEl = document.querySelector('.cart-total .total-caption');
        if (totalCaptionEl && data.selected_count !== undefined) {
            totalCaptionEl.textContent = `Tổng cộng ${data.selected_count} sản phẩm`;
        }

        // 3. Update header badge
        const badge = document.querySelector('.js-cart-badge');
        if (badge && data.cart_count !== undefined) {
            badge.textContent = data.cart_count;
            badge.classList.toggle('badge-hidden', data.cart_count === 0);
        }

        // 4. Update checkout button
        const checkoutBtn = document.querySelector('#cartCheckoutForm button[type="submit"]');
        if (checkoutBtn && data.selected_count !== undefined) {
            checkoutBtn.disabled = data.selected_count === 0;
        }

        // 5. Update deposit box visibility
        const depositBox = document.querySelector('.deposit-box');
        if (depositBox) {
            depositBox.classList.toggle('hidden', data.cart_payment_type !== 'deposit');
        }
    }

    function updateLocalSummary() {
        const rows = document.querySelectorAll('.cart-item');
        let selectedCount = 0;
        let selectedTotal = 0;
        const totalItemCount = rows.length;

        rows.forEach(row => {
            const cb = row.querySelector('.item-checkbox');
            if (cb && cb.checked) {
                selectedCount++;
                const sub = parseInt(row.dataset.itemSubtotal || '0', 10);
                selectedTotal += sub;
            }
        });

        // Update Select All visual
        const selectAll = document.getElementById('selectAllCheckbox');
        if (selectAll) {
            selectAll.checked = (totalItemCount > 0 && selectedCount === totalItemCount);
        }

        // Update "Chọn tất cả (#)" label
        const selectAllCountEl = document.getElementById('selectAllCount');
        if (selectAllCountEl) {
            selectAllCountEl.textContent = totalItemCount;
        }

        return { selectedCount, selectedTotal };
    }

    // --- Global Actions ---
    window.showToast = function(msg, type = 'success') {
        const toast = document.getElementById('successToast');
        if (toast) {
            toast.textContent = msg;
            toast.className = 'toast'; // Reset classes
            if (type === 'error') toast.classList.add('toast-error');
            if (type === 'warning') toast.classList.add('toast-warning');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }
    };

    window.directDeleteItem = async function(itemId) {
        try {
            const data = await performAction(`/cart/delete/${itemId}/`, {});
            if (data.ok) {
                const row = document.querySelector(`.cart-item[data-item-id="${itemId}"]`);
                if (row) {
                    row.style.opacity = '0';
                    row.style.transform = 'translateX(20px)';
                    setTimeout(() => {
                        row.remove();
                        if (document.querySelectorAll('.cart-item').length === 0) {
                            window.location.reload();
                        } else {
                            syncUI(data);
                            updateLocalSummary();
                        }
                    }, 300);
                }
            }
        } catch (e) {
            showToast(e.message, 'error');
        }
    };

    // --- Event Listeners ---
    
    // Select All
    const selectAllCb = document.getElementById('selectAllCheckbox');
    if (selectAllCb) {
        selectAllCb.addEventListener('change', async () => {
            try {
                const data = await performAction(cartEndpoint, {
                    action: 'toggle_select_all',
                    is_selected: selectAllCb.checked
                });
                if (data.ok) {
                    document.querySelectorAll('.cart-item .item-checkbox').forEach(cb => {
                        cb.checked = selectAllCb.checked;
                    });
                    syncUI(data);
                    updateLocalSummary();
                }
            } catch (e) {
                selectAllCb.checked = !selectAllCb.checked;
                showToast(e.message, 'error');
            }
        });
    }

    // Bulk Delete
    const bulkBtn = document.getElementById('bulkDeleteBtn');
    if (bulkBtn) {
        bulkBtn.addEventListener('click', () => {
            const { selectedCount } = updateLocalSummary();
            if (selectedCount === 0) {
                showToast('Vui lòng chọn sản phẩm cần xóa', 'warning');
                return;
            }

            const confirmBtn = document.getElementById('confirmDeleteBtn');
            const modal = document.getElementById('deleteConfirmModal');
            if (modal && confirmBtn) {
                modal.querySelector('.modal-body p').textContent = `Xác nhận xóa ${selectedCount} sản phẩm đã chọn khỏi giỏ hàng?`;
                confirmBtn.onclick = async () => {
                    try {
                        const data = await performAction(cartEndpoint, { action: 'bulk_delete' });
                        if (data.ok) window.location.reload();
                    } catch (e) {
                        showToast(e.message, 'error');
                    }
                };
                modal.classList.add('show');
            }
        });
    }

    // Item Selection
    document.querySelectorAll('.cart-item .item-checkbox').forEach(cb => {
        cb.addEventListener('change', async () => {
            const itemId = cb.closest('.cart-item').dataset.itemId;
            try {
                const data = await performAction(cartEndpoint, {
                    action: 'toggle_select',
                    item_id: itemId,
                    is_selected: cb.checked
                });
                if (data.ok) {
                    syncUI(data);
                    updateLocalSummary();
                }
            } catch (e) {
                cb.checked = !cb.checked;
                showToast(e.message, 'error');
            }
        });
    });

    // Quantity Steppers
    document.querySelectorAll('.item-qty-stepper').forEach(stepper => {
        const input = stepper.querySelector('.qty-input');
        const row = stepper.closest('.cart-item');
        const itemId = row.dataset.itemId;

        stepper.querySelectorAll('.qty-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const delta = parseInt(btn.dataset.delta, 10);
                const newVal = parseInt(input.value, 10) + delta;
                if (newVal < 1) return;

                try {
                    btn.disabled = true;
                    const data = await performAction(cartEndpoint, {
                        action: 'update_quantity',
                        item_id: itemId,
                        quantity: newVal
                    });
                    if (data.ok) {
                        input.value = newVal;
                        const price = parseInt(row.querySelector('.item-price').textContent.replace(/\D/g, ''), 10);
                        row.dataset.itemSubtotal = price * newVal;
                        syncUI(data);
                        updateLocalSummary();
                    }
                } catch (e) {
                    showToast(e.message, 'error');
                } finally {
                    btn.disabled = false;
                }
            });
        });
    });

    // Payment Type
    document.querySelectorAll('input[name="cart_payment_type"]').forEach(radio => {
        radio.addEventListener('change', async () => {
            try {
                const data = await performAction(cartEndpoint, {
                    action: 'update_payment_type',
                    cart_payment_type: radio.value
                });
                syncUI(data);
            } catch (e) {
                showToast(e.message, 'error');
            }
        });
    });

    // Deposit Steppers
    document.querySelectorAll('.deposit-stepper-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const current = parseInt(document.getElementById('depositPercentValue').textContent, 10);
            const next = current + parseInt(btn.dataset.delta, 10);
            if (next < 10 || next > 50) return;
            try {
                const data = await performAction(cartEndpoint, {
                    action: 'update_deposit',
                    deposit_percent_input: next
                });
                syncUI(data);
            } catch (e) {
                showToast(e.message, 'error');
            }
        });
    });

    // Modal close
    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modal = document.getElementById(btn.dataset.close);
            if (modal) modal.classList.remove('show');
        });
    });

    // Initial Sync
    updateLocalSummary();
});
