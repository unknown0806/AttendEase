/**
 * AttendX — Master Chart.js & Attendance Visualization Engine
 * Clean, animated charts for Student, Teacher, and Admin dashboards.
 */

window.AttendXCharts = (function () {
    'use strict';

    // Chart.js default styling matching AttendX design palette
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.color = '#64748b';
        Chart.defaults.plugins.tooltip.backgroundColor = '#10376d';
        Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
        Chart.defaults.plugins.tooltip.bodyColor = '#f3f6fa';
        Chart.defaults.plugins.tooltip.padding = 10;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
    }

    /**
     * Student Weekly Attendance Trend Line Chart
     */
    function renderStudentTrendChart(canvasId, labels, dataPoints) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || typeof Chart === 'undefined') return;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                datasets: [{
                    label: 'Attendance %',
                    data: dataPoints || [85, 90, 75, 80, 88, 92],
                    borderColor: '#184e96',
                    backgroundColor: 'rgba(24, 78, 150, 0.08)',
                    borderWidth: 2.5,
                    tension: 0.35,
                    fill: true,
                    pointBackgroundColor: '#184e96',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4.5,
                    pointHoverRadius: 6.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                scales: {
                    y: {
                        min: 50,
                        max: 100,
                        grid: { color: 'rgba(226, 232, 240, 0.6)' },
                        ticks: {
                            callback: value => value + '%'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Teacher Subject Attendance Distribution Bar Chart
     */
    function renderTeacherSubjectBarChart(canvasId, subjects, percentages) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || typeof Chart === 'undefined') return;

        const backgroundColors = percentages.map(p => p < 75 ? '#ef4444' : (p >= 85 ? '#10b981' : '#184e96'));

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: subjects || ['DBMS', 'OS', 'DSA', 'Networks', 'SE'],
                datasets: [{
                    label: 'Average Class Attendance',
                    data: percentages || [88, 72, 91, 78, 84],
                    backgroundColor: backgroundColors,
                    borderRadius: 8,
                    borderSkipped: false,
                    barThickness: 24
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1100,
                    easing: 'easeOutQuart'
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(226, 232, 240, 0.6)' },
                        ticks: { callback: value => value + '%' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Admin Institutional Attendance Donut Chart
     */
    function renderAdminAttendanceDonut(canvasId, presentCount, absentCount) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || typeof Chart === 'undefined') return;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Present Today', 'Absent Today'],
                datasets: [{
                    data: [presentCount || 142, absentCount || 23],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 16
                        }
                    }
                }
            }
        });
    }

    return {
        studentTrend: renderStudentTrendChart,
        teacherBar: renderTeacherSubjectBarChart,
        adminDonut: renderAdminAttendanceDonut
    };
})();
