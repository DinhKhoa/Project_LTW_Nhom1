document.addEventListener('DOMContentLoaded', () => {
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';
    const cartEndpoint = window.location.pathname;

    async function postCheckoutAction(payload) {
        const response = await fetch(cartEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new URLSearchParams(payload).toString()
        });

        if (!response.ok) {
            throw new Error('Không thể cập nhật dữ liệu.');
        }

        return response.json();
    }

    function syncCheckoutUI(data) {
        const depositBox = document.querySelector('.deposit-box');
        const depositAmountText = document.getElementById('depositAmountText');
        const summaryPayableAmount = document.getElementById('summaryPayableAmount');
        const codWarn = document.getElementById('codWarn');
        const depositWarn = document.getElementById('depositWarn');
        const voucherFixedText = document.getElementById('voucherFixedText');
        const couponCodeInput = document.getElementById('couponCodeInput');
        const bankPaymentAmount = document.getElementById('bankPaymentAmount');

        if (depositBox) {
            depositBox.classList.toggle('hidden', data.cart_payment_type !== 'deposit');
        }

        if (depositAmountText) {
            depositAmountText.textContent = `${data.formatted_deposit_amount} đ`;
        }

        const depositPercentText = document.getElementById('depositPercentValue');
        if (depositPercentText) {
            depositPercentText.textContent = data.deposit_percent;
        }

        // Sync deposit input value if present
        const depositInput = document.getElementById('depositPercentInput');
        if (depositInput) {
            depositInput.value = data.deposit_percent;
        }

        const payableText = data.cart_payment_type === 'deposit'
            ? `${data.formatted_deposit_amount} đ`
            : `${data.formatted_total_price} đ`;

        if (summaryPayableAmount) {
            summaryPayableAmount.textContent = payableText;
        }

        if (bankPaymentAmount) {
            bankPaymentAmount.textContent = data.formatted_total_price;
        }

        if (codWarn) {
            codWarn.classList.toggle('hidden', data.cart_payment_type !== 'full');
        }

        if (depositWarn) {
            depositWarn.classList.toggle('hidden', data.cart_payment_type !== 'deposit');
        }

        if (couponCodeInput && data.coupon_code !== undefined) {
            couponCodeInput.value = data.coupon_code;
        }

        if (voucherFixedText) {
            voucherFixedText.textContent = data.coupon_code ? data.coupon_code : 'Chưa áp dụng';
        }

        document.querySelectorAll('.order-method-btn').forEach((btn) => {
            const method = btn.dataset.method;
            btn.classList.toggle('active', method === data.order_method);
            if (method === 'cod') {
                btn.classList.toggle('disabled', data.cart_payment_type === 'full');
            }
        });
    }

    // Modal helpers
    window.openModal = function(id) {
        document.getElementById(id).classList.add('show');
    };

    window.closeModal = function(id) {
        document.getElementById(id).classList.remove('show');
    };

    window.showToast = function(message) {
        const toast = document.getElementById('successToast');
        if (toast) {
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2200);
        }
    };

    // Close modals when clicking on the close button
    document.querySelectorAll('[data-close]').forEach((btn) => {
        btn.addEventListener('click', () => closeModal(btn.dataset.close));
    });

    // Close modals when clicking outside the modal-box
    document.querySelectorAll('.modal').forEach((modal) => {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) modal.classList.remove('show');
        });
    });

    // In-place update for cart payment type
    const cartPaymentForm = document.getElementById('cartPaymentForm');
    if (cartPaymentForm) {
        cartPaymentForm.querySelectorAll('input[name="cart_payment_type"]').forEach((radio) => {
            radio.addEventListener('change', async () => {
                try {
                    const data = await postCheckoutAction({
                        action: 'update_payment_type',
                        cart_payment_type: radio.value
                    });
                    syncCheckoutUI(data);
                } catch (error) {
                    showToast(error.message);
                }
            });
        });
    }

    // Deposit percent: ▲▼ steppers, step 10, min 10 max 50
    let currentDepositPercent = parseInt(
        document.getElementById('depositPercentValue')?.textContent || '10', 10
    ) || 10;

    async function applyDepositPercent(newVal) {
        newVal = Math.max(10, Math.min(50, newVal));
        currentDepositPercent = newVal;
        const pv = document.getElementById('depositPercentValue');
        if (pv) pv.textContent = newVal;
        try {
            const data = await postCheckoutAction({
                action: 'update_deposit',
                deposit_delta: 0,
                deposit_percent_input: newVal
            });
            syncCheckoutUI(data);
            currentDepositPercent = data.deposit_percent;
        } catch (error) {
            showToast(error.message);
        }
    }

    document.querySelectorAll('.deposit-stepper-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            applyDepositPercent(currentDepositPercent + parseInt(btn.dataset.delta, 10));
        });
    });

    // In-place update for order payment method
    document.querySelectorAll('.order-method-btn').forEach((btn) => {
        btn.addEventListener('click', async () => {
            if (btn.classList.contains('disabled')) return;
            try {
                const data = await postCheckoutAction({
                    action: 'update_order_method',
                    order_method: btn.dataset.method
                });
                syncCheckoutUI(data);
            } catch (error) {
                showToast(error.message);
            }
        });
    });

    // In-place update for coupon and voucher row
    const couponForm = document.getElementById('couponForm');
    if (couponForm) {
        couponForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const codeInput = document.getElementById('couponCodeInput');
            try {
                const data = await postCheckoutAction({
                    action: 'apply_coupon',
                    coupon_code: codeInput ? codeInput.value : ''
                });
                syncCheckoutUI(data);
                showToast(data.coupon_code ? 'Đã áp dụng mã giảm giá' : 'Đã xóa mã giảm giá');
            } catch (error) {
                showToast(error.message);
            }
        });
    }

    // Display initial toast if needed
    const toastElement = document.getElementById('successToast');
    if (toastElement) {
        const toastMessage = toastElement.textContent.trim();
        if (toastMessage) {
            showToast(toastMessage);
        }
    }

    // Bank payment countdown timer
    const timerMinutes = document.getElementById('timerMinutes');
    const timerSeconds = document.getElementById('timerSeconds');
    if (timerMinutes && timerSeconds) {
        let timeRemaining = 5 * 60;
        function updateTimer() {
            const mins = Math.floor(timeRemaining / 60);
            const secs = timeRemaining % 60;
            timerMinutes.textContent = String(mins).padStart(2, '0');
            timerSeconds.textContent = String(secs).padStart(2, '0');
            if (timeRemaining > 0) {
                timeRemaining--;
                setTimeout(updateTimer, 1000);
            }
        }
        updateTimer();
    }
});
