document.addEventListener('DOMContentLoaded', () => {
    const dropdownItems = document.querySelectorAll('.site-nav__item--dropdown');

    function closeAllDropdowns(exceptItem = null) {
        dropdownItems.forEach((item) => {
            if (item !== exceptItem) {
                item.classList.remove('is-open');
                const trigger = item.querySelector('.site-nav__trigger');
                if (trigger) {
                    trigger.setAttribute('aria-expanded', 'false');
                }
            }
        });
    }

    dropdownItems.forEach((item) => {
        const trigger = item.querySelector('.site-nav__trigger');

        if (!trigger) {
            return;
        }

        trigger.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = item.classList.contains('is-open');
            closeAllDropdowns(item);
            item.classList.toggle('is-open', !isOpen);
            trigger.setAttribute('aria-expanded', String(!isOpen));
        });
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.site-nav')) {
            closeAllDropdowns();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeAllDropdowns();
        }
    });
});

(function () {
    let confirmOverlay = null;
    let toastStack = null;

    function ensureConfirmDialog() {
        if (confirmOverlay) {
            return confirmOverlay;
        }

        confirmOverlay = document.createElement('div');
        confirmOverlay.className = 'app-confirm-overlay';
        confirmOverlay.innerHTML = `
            <div class="app-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="app-confirm-title">
                <h3 id="app-confirm-title">Xác nhận thao tác</h3>
                <p class="app-confirm-message">Bạn có chắc chắn muốn tiếp tục?</p>
                <div class="app-confirm-actions">
                    <button type="button" class="dark-button app-confirm-cancel">Hủy</button>
                    <button type="button" class="green-button app-confirm-submit">Xác nhận</button>
                </div>
            </div>
        `;

        document.body.appendChild(confirmOverlay);
        return confirmOverlay;
    }

    function ensureToastStack() {
        if (toastStack) {
            return toastStack;
        }

        toastStack = document.createElement('div');
        toastStack.className = 'app-toast-stack';
        document.body.appendChild(toastStack);
        return toastStack;
    }

    window.showAppToast = function showAppToast(message, type = 'success') {
        const stack = ensureToastStack();
        const toast = document.createElement('div');
        toast.className = `app-toast app-toast--${type}`;
        toast.textContent = message;
        stack.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('is-visible');
        });

        setTimeout(() => {
            toast.classList.remove('is-visible');
            setTimeout(() => toast.remove(), 220);
        }, 2600);
    };

    window.showAppConfirm = function showAppConfirm({
        title = 'Xác nhận thao tác',
        message = 'Bạn có chắc chắn muốn tiếp tục?',
        onConfirm = null,
        onCancel = null,
    } = {}) {
        const overlay = ensureConfirmDialog();
        const titleElement = overlay.querySelector('#app-confirm-title');
        const messageElement = overlay.querySelector('.app-confirm-message');
        const cancelButton = overlay.querySelector('.app-confirm-cancel');
        const confirmButton = overlay.querySelector('.app-confirm-submit');

        titleElement.textContent = title;
        messageElement.textContent = message;

        const closeDialog = () => {
            overlay.classList.remove('is-visible');
            document.removeEventListener('keydown', handleEscape);
            cancelButton.removeEventListener('click', handleCancel);
            confirmButton.removeEventListener('click', handleConfirm);
            overlay.removeEventListener('click', handleOverlayClick);
        };

        const handleCancel = () => {
            closeDialog();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        };

        const handleConfirm = () => {
            closeDialog();
            if (typeof onConfirm === 'function') {
                onConfirm();
            }
        };

        const handleOverlayClick = (event) => {
            if (event.target === overlay) {
                handleCancel();
            }
        };

        const handleEscape = (event) => {
            if (event.key === 'Escape') {
                handleCancel();
            }
        };

        cancelButton.addEventListener('click', handleCancel);
        confirmButton.addEventListener('click', handleConfirm);
        overlay.addEventListener('click', handleOverlayClick);
        document.addEventListener('keydown', handleEscape);

        overlay.classList.add('is-visible');
    };
})();
