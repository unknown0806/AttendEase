// Teacher Attendance Marking Helpers

function markAll(status) {
    const radios = document.querySelectorAll(`input[type="radio"][value="${status}"]`);
    radios.forEach(radio => {
        if (!radio.disabled) {
            radio.checked = true;
        }
    });
    updateCounts();
}

function updateCounts() {
    const presentRadios = document.querySelectorAll('input[type="radio"][value="present"]:checked');
    const absentRadios = document.querySelectorAll('input[type="radio"][value="absent"]:checked');

    const presentBadge = document.getElementById('count-present');
    const absentBadge = document.getElementById('count-absent');

    if (presentBadge) presentBadge.textContent = presentRadios.length;
    if (absentBadge) absentBadge.textContent = absentRadios.length;
}

document.addEventListener('DOMContentLoaded', () => {
    const allRadios = document.querySelectorAll('input[type="radio"][name^="status_"]');
    allRadios.forEach(radio => {
        radio.addEventListener('change', updateCounts);
    });
    updateCounts();

    const attendanceForm = document.getElementById('attendance-form');
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', (e) => {
            const confirmed = confirm("Are you sure you want to SUBMIT attendance?\n\nIMPORTANT: Once submitted, the attendance record will be PERMANENTLY LOCKED and cannot be edited by teachers.");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }
});
