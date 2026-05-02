document.addEventListener('DOMContentLoaded', function() {
    const eyeIcons = document.querySelectorAll('.password-eye');
    
    eyeIcons.forEach(function(eyeIcon) {
        eyeIcon.addEventListener('click', function() {
            const passwordField = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordField.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
});
