document.addEventListener('DOMContentLoaded', () => {
    const statusButtons = document.querySelectorAll('.status-step');
    const statusBadge = document.getElementById('currentStatusBadge');
    const proofHistory = document.getElementById('proofHistory');
    const proofModal = document.getElementById('proofModal');
    const proofModalClose = document.getElementById('proofModalClose');
    const proofCancel = document.getElementById('proofCancel');
    const proofForm = document.getElementById('proofForm');
    const proofStatus = document.getElementById('proofStatus');
    const proofText = document.getElementById('proofText');
    const proofImage = document.getElementById('proofImage');
    const proofPreview = document.getElementById('proofPreview');

    let pendingStatus = null;
    const completedProofs = new Set();

    function getStatusButton(statusValue) {
        return document.querySelector(`.status-step[data-status="${statusValue}"]`);
    }

    function getNextStatus(statusValue) {
        const order = ['chua-nhan-hang', 'da-nhan-hang', 'dang-van-chuyen', 'lap-dat-thanh-cong'];
        const index = order.indexOf(statusValue);
        return index >= 0 ? order[index + 1] : null;
    }

    function appendProofHistory(statusLabel, message, fileName) {
        if (!proofHistory) {
            return;
        }

        const item = document.createElement('article');
        item.className = 'proof-history-item';
        item.innerHTML = `
            <div>
                <strong>${statusLabel}</strong>
                <p>${message}</p>
                <p>Hình ảnh: ${fileName}</p>
            </div>
            <span class="proof-history-badge is-done">Đã lưu</span>
        `;
        proofHistory.appendChild(item);
    }

    function openModal() {
        proofModal.classList.add('is-visible');
        proofModal.setAttribute('aria-hidden', 'false');
    }

    function closeModal() {
        proofModal.classList.remove('is-visible');
        proofModal.setAttribute('aria-hidden', 'true');
        proofForm.reset();
        proofPreview.textContent = 'Chưa có hình ảnh nào được chọn';
        pendingStatus = null;
    }

    statusButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (button.disabled) {
                window.showAppToast('Bạn cần hoàn tất minh chứng của trạng thái trước đó');
                return;
            }

            pendingStatus = {
                value: button.dataset.status,
                label: button.dataset.label,
                element: button,
            };
            proofStatus.value = pendingStatus.label;
            openModal();
        });
    });

    if (proofImage) {
        proofImage.addEventListener('change', () => {
            const fileName = proofImage.files && proofImage.files[0] ? proofImage.files[0].name : '';
            proofPreview.textContent = fileName
                ? `Đã chọn hình ảnh: ${fileName}`
                : 'Chưa có hình ảnh nào được chọn';
        });
    }

    proofForm.addEventListener('submit', (event) => {
        event.preventDefault();

        if (!pendingStatus) {
            return;
        }

        const proofMessage = proofText.value.trim();
        const hasImage = proofImage.files && proofImage.files.length > 0;

        if (!proofMessage || !hasImage) {
            window.showAppToast('Vui lòng nhập minh chứng và chọn hình ảnh chứng minh');
            return;
        }

        const proofFileName = proofImage.files[0].name;

        statusButtons.forEach((button) => button.classList.remove('is-active'));
        pendingStatus.element.classList.add('is-active');
        statusBadge.textContent = pendingStatus.label;
        statusBadge.dataset.status = pendingStatus.value;

        completedProofs.add(pendingStatus.value);
        appendProofHistory(pendingStatus.label, proofMessage, proofFileName);

        const nextStatus = getNextStatus(pendingStatus.value);
        const nextButton = getStatusButton(nextStatus);
        if (nextButton && completedProofs.has(pendingStatus.value)) {
            nextButton.disabled = false;
        }

        const successLabel = pendingStatus.label;
        closeModal();
        window.showAppToast(`Cập nhật trạng thái thành công: ${successLabel}`);
    });

    [proofModalClose, proofCancel].forEach((button) => {
        if (button) {
            button.addEventListener('click', closeModal);
        }
    });

    proofModal.addEventListener('click', (event) => {
        if (event.target === proofModal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && proofModal.classList.contains('is-visible')) {
            closeModal();
        }
    });
});
