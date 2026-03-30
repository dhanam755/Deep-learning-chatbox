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
        const username = document.querySelector('input[name="username"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();
        const password = passwordInput.value.trim();

        if (!username || !email || !password) {
            e.preventDefault();
            alert('Please fill in all fields');
            return false;
        }

        if (!email.includes('@') || !email.includes('.')) {
            e.preventDefault();
            alert('Please enter a valid email');
            return false;
        }

        if (password.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters');
            return false;
        }
    });
});
