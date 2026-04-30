document.addEventListener('DOMContentLoaded', () => {
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';
    const cartEndpoint = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

    async function postCheckoutAction(payload) {
        const response = await fetch(cartEndpoint, {
            method: 'POST', headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }, body: new URLSearchParams(payload).toString()
        });

        if (!response.ok) {
            throw new Error('Không thể cập nhật dữ liệu.');
        }

        return response.json();
    }

    function syncCheckoutUI(data) {
        const summaryPayableAmount = document.getElementById('summaryPayableAmount');
        const codWarn = document.getElementById('codWarn');
        const depositWarn = document.getElementById('depositWarn');
        const bankPaymentAmount = document.getElementById('bankPaymentAmount');

        const payableText = data.cart_payment_type === 'deposit' ? `${data.formatted_deposit_amount} đ` : `${data.formatted_total_price} đ`;

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

        document.querySelectorAll('.order-method-btn').forEach((btn) => {
            const method = btn.dataset.method;
            btn.classList.toggle('active', method === data.order_method);
            if (method === 'cod') {
                btn.classList.toggle('disabled', data.cart_payment_type === 'full');
            }
        });
    }

    // Handle data-close if not already handled by main.js (though it is)
    // Removed redundant openModal/closeModal

    // Order method update
    document.querySelectorAll('.order-method-btn').forEach((btn) => {
        btn.addEventListener('click', async () => {
            if (btn.classList.contains('disabled')) return;
            try {
                const data = await postCheckoutAction({
                    action: 'update_order_method', order_method: btn.dataset.method
                });
                syncCheckoutUI(data);
            } catch (error) {
                showToast(error.message);
            }
        });
    });

    // Countdown timer
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
