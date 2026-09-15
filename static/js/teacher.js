// AttendX — Teacher Attendance Marking Helpers with GSAP Micro-Interactions

function markAll(status) {
    if (window.AttendXAnim && typeof window.AttendXAnim.markAll === 'function') {
        window.AttendXAnim.markAll(status);
    } else {
        const radios = document.querySelectorAll(`input[type="radio"][value="${status}"]`);
        radios.forEach(radio => {
            if (!radio.disabled) {
                radio.checked = true;
            }
        });
        updateCounts();
    }
}

function updateCounts() {
    if (window.AttendXAnim && typeof window.AttendXAnim.updateCounters === 'function') {
        window.AttendXAnim.updateCounters();
    } else {
        const presentRadios = document.querySelectorAll('input[type="radio"][value="present"]:checked');
        const absentRadios = document.querySelectorAll('input[type="radio"][value="absent"]:checked');

        const presentBadge = document.getElementById('count-present');
        const absentBadge = document.getElementById('count-absent');

        if (presentBadge) presentBadge.textContent = presentRadios.length;
        if (absentBadge) absentBadge.textContent = absentRadios.length;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const studentRows = document.querySelectorAll('.list-group-item[data-student-row]');
    studentRows.forEach(row => {
        const radios = row.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
            radio.addEventListener('change', () => {
                updateCounts();
            });
        });
    });

    updateCounts();

    const attendanceForm = document.getElementById('attendance-form');
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', (e) => {
            const confirmed = confirm("Are you sure you want to SUBMIT attendance?\n\nIMPORTANT: Once submitted, the attendance record will be PERMANENTLY LOCKED and cannot be edited by teachers.");
            if (!confirmed) {
                e.preventDefault();
            } else if (window.AttendXAnim && typeof window.AttendXAnim.toast === 'function') {
                window.AttendXAnim.toast("Locking Attendance", "Encrypting session and locking records...", "warning", 3000);
            }
        });
    }
});
