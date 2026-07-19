/**
 * auth.js — Auth Forms Utilities
 * ================================
 * Validates password strength bar, displays client-side feedback,
 * and handles toggle visibility controls.
 */

// ─── Toggle Password Visibility ─────────────────────────────────────────────

const pwToggle = document.getElementById('pwToggle');
const passwordInput = document.getElementById('password');

if (pwToggle && passwordInput) {
    pwToggle.addEventListener('click', () => {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = pwToggle.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
}

// ─── Password Strength Calculations ──────────────────────────────────────────

const strengthBar = document.getElementById('strengthBar');
const strengthText = document.getElementById('strengthText');

if (passwordInput && strengthBar && strengthText) {
    passwordInput.addEventListener('input', () => {
        const pw = passwordInput.value;
        let score = 0;
        
        if (!pw) {
            strengthBar.className = 'strength-meter-bar';
            strengthBar.style.width = '0%';
            strengthText.textContent = 'Password Strength: None';
            return;
        }

        // Basic checks
        if (pw.length >= 6) score += 1;
        if (pw.length >= 10) score += 1;
        if (/[A-Z]/.test(pw)) score += 1;
        if (/[a-z]/.test(pw)) score += 1;
        if (/[0-9]/.test(pw)) score += 1;
        if (/[^A-Za-z0-9]/.test(pw)) score += 1;

        // Map score to classes
        let strength = 'Weak';
        let barClass = 'weak';
        let width = '20%';

        if (score >= 5) {
            strength = 'Strong (Excellent)';
            barClass = 'strong';
            width = '100%';
        } else if (score >= 3) {
            strength = 'Medium (Satisfactory)';
            barClass = 'medium';
            width = '60%';
        } else {
            strength = 'Weak (Needs Work)';
            barClass = 'weak';
            width = '30%';
        }

        strengthBar.className = `strength-meter-bar ${barClass}`;
        strengthBar.style.width = width;
        strengthText.textContent = `Password Strength: ${strength}`;
    });
}
