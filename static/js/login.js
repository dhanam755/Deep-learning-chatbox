document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.btn-toggle');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.textContent = type === 'password' ? 'Show' : 'Hide';
        });
    }

    // Form validation
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        const email = document.querySelector('input[name="email"]').value;
        const password = passwordInput.value;

        if (!email || !password) {
            e.preventDefault();
            alert('Please fill in all fields');
            return false;
        }

        if (!email.includes('@')) {
            e.preventDefault();
            alert('Please enter a valid email');
            return false;
        }
    });
});
