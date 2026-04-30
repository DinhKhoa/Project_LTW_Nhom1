(function () {
    // Handling Start Process
    const startProcessBtn = document.getElementById('startProcessBtn');
    if (startProcessBtn) {
        startProcessBtn.addEventListener('click', function () {
            if (confirm('Bạn có chắc chắn muốn bắt đầu giao hàng?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                // Submit to current URL
                form.action = window.location.href;
                
                // Add CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                const actionInput = document.createElement('input');
                actionInput.type = 'hidden';
                actionInput.name = 'action';
                actionInput.value = 'start_shipping';
                form.appendChild(actionInput);
                
                document.body.appendChild(form);
                form.submit();
            }
        });
    }

    // Handling Complete Task
    const submitCompleteTaskBtn = document.getElementById('submitCompleteTaskBtn');
    if (submitCompleteTaskBtn) {
        submitCompleteTaskBtn.addEventListener('click', function () {
            const proofInput = document.getElementById('completeTaskProof');
            if (!proofInput.files || proofInput.files.length === 0) {
                alert('Vui lòng tải lên ảnh minh chứng hoàn thành.');
                return;
            }
            
            const form = document.getElementById('completeTaskForm');
            form.method = 'POST';
            form.action = window.location.href;
            form.enctype = "multipart/form-data"; // Important for file upload
            
            // Add CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
            
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'complete';
            form.appendChild(actionInput);
            
            // Change file input name to match what backend expects
            proofInput.name = 'proof_image';
            
            form.submit();
        });
    }
})();
