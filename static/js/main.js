// AttendX — Modern UI Helper Scripts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Circular Ring Gauges
    initCircularGauges();

    // 2. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 3. Toggle Password Visibility
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            const icon = togglePasswordBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-eye');
                icon.classList.toggle('bi-eye-slash');
            }
        });
    }
});

function initCircularGauges() {
    const gauges = document.querySelectorAll('.gauge-circle');
    gauges.forEach(gauge => {
        const pct = parseFloat(gauge.getAttribute('data-percent') || '0');
        let color = '#184e96'; // Default Academic Blue
        
        if (pct < 75) {
            color = '#ef4444'; // Red for < 75% shortage alert
        } else if (pct >= 85) {
            color = '#10b981'; // Green for excellent
        } else {
            color = '#184e96'; // Blue for 75-84%
        }
        
        gauge.style.setProperty('--percent', pct);
        gauge.style.setProperty('--gauge-color', color);
    });
}

// Quick fill helper for demo login
function quickLogin(email, password) {
    const emailInput = document.getElementById('email');
    const passInput = document.getElementById('password');
    if (emailInput && passInput) {
        emailInput.value = email;
        passInput.value = password;
        const form = emailInput.closest('form');
        if (form) {
            form.submit();
        }
    }
}
