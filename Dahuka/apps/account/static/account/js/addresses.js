function showDeleteModal(el) {
    const modal = document.getElementById('deleteAddressModal');
    const form = document.getElementById('deleteAddressForm');
    const infoText = document.getElementById('deleteAddressInfo');
    
    form.action = el.dataset.url;
    infoText.textContent = el.dataset.info;
    modal.classList.add('active');
}

function closeDeleteModal() {
    document.getElementById('deleteAddressModal').classList.remove('active');
}

window.onclick = function(event) {
    const deleteModal = document.getElementById('deleteAddressModal');
    const addressModal = document.getElementById('addressModal');
    if (event.target == deleteModal) {
        closeDeleteModal();
    }
    if (event.target == addressModal) {
        closeAddressModal();
    }
}

document.addEventListener('submit', async function(e) {
    if (e.target && e.target.id === 'addressEntryForm') {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const url = form.action;
        const body = document.getElementById('addressModalBody');

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            
            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }

            const result = await response.json();
            
            if (result.success) {
                window.location.href = window.location.pathname; 
            } else if (result.html) {
                body.innerHTML = result.html;
                executeScripts(body);
            }
        } catch (error) {
            console.error("AJAX submission error:", error);
            window.showToast("Đã xảy ra lỗi: " + error.message, 'error');
        }
    }
});

function executeScripts(container) {
    const scripts = container.querySelectorAll('script');
    scripts.forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
}

async function openAddressModal(url) {
    const modal = document.getElementById('addressModal');
    const body = document.getElementById('addressModalBody');
    const title = document.getElementById('addressModalTitle');
    
    title.textContent = 'THÔNG TIN KHÁCH HÀNG';
    body.innerHTML = '<div style="text-align:center; padding:40px;">Đang tải...</div>';
    modal.classList.add('active');

    try {
        const response = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        body.innerHTML = data.html;
        executeScripts(body);
    } catch (error) {
        body.innerHTML = '<div style="color:red; text-align:center; padding:40px;">Không thể tải form. Vui lòng thử lại.</div>';
    }
}

function closeAddressModal() {
    document.getElementById('addressModal').classList.remove('active');
}
