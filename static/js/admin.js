// Admin Panel Helpers

document.addEventListener('DOMContentLoaded', () => {
    // Validate mandatory reason on correction forms
    const correctionForms = document.querySelectorAll('.correction-form');
    correctionForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const reasonInput = form.querySelector('textarea[name="reason"], input[name="reason"]');
            if (reasonInput && !reasonInput.value.trim()) {
                e.preventDefault();
                alert("A mandatory reason is required to correct locked attendance.");
                reasonInput.focus();
            }
        });
    });
});
