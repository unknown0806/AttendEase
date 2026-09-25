/**
 * AttendX — Master GSAP Animation & Micro-Interactions Engine
 * Provides smooth, professional, performance-optimized animations across the entire ERP.
 */

window.AttendXAnim = (function () {
    'use strict';

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Centralized animation configuration
    const config = {
        duration: {
            instant: 0.15,
            fast: 0.28,
            normal: 0.45,
            slow: 0.75
        },
        ease: {
            smooth: 'power2.out',
            snappy: 'power3.out',
            bounceSubtle: 'back.out(1.4)',
            pop: 'back.out(2.0)'
        }
    };

    /**
     * 1. Page Load Stagger Animation
     */
    function initPageLoadAnimations() {
        if (prefersReducedMotion || typeof gsap === 'undefined') return;

        const tl = gsap.timeline({ defaults: { ease: config.ease.smooth } });

        // A. Header slide & fade
        const topHeader = document.querySelector('.app-top-header');
        if (topHeader) {
            tl.from(topHeader, {
                y: -18,
                opacity: 0,
                duration: config.duration.normal
            }, 0);
        }

        // B. Navbar fade in
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            tl.from(navbar, {
                opacity: 0,
                duration: config.duration.fast
            }, 0.05);
        }

        // C. Announcement / Shortage banners
        const banners = document.querySelectorAll('.announcement-banner, .alert-danger, .alert-warning');
        if (banners.length > 0) {
            tl.from(banners, {
                y: 15,
                opacity: 0,
                stagger: 0.06,
                duration: config.duration.normal
            }, 0.1);
        }

        // D. Summary & Dashboard Cards stagger
        const cards = document.querySelectorAll('.app-card, .subject-card');
        if (cards.length > 0) {
            tl.from(cards, {
                y: 22,
                opacity: 0,
                stagger: 0.07,
                duration: config.duration.normal
            }, 0.15);
        }

        // E. Action circle button grid pop-in
        const actionItems = document.querySelectorAll('.action-item');
        if (actionItems.length > 0) {
            tl.from(actionItems, {
                scale: 0.82,
                opacity: 0,
                stagger: 0.035,
                duration: config.duration.fast,
                ease: config.ease.bounceSubtle
            }, 0.25);
        }

        // F. Table rows / list items stagger
        const listItems = document.querySelectorAll('.list-group-item, table tbody tr');
        if (listItems.length > 0 && listItems.length <= 30) {
            tl.from(listItems, {
                y: 12,
                opacity: 0,
                stagger: 0.025,
                duration: config.duration.fast
            }, 0.3);
        }
    }

    /**
     * 2. Number & Percentage Counters Animation
     */
    function animateCounters() {
        if (typeof gsap === 'undefined') return;

        // Animate all elements with .counter-value or numbers in stat cards
        const counterElements = document.querySelectorAll('[data-counter], .animate-counter');
        counterElements.forEach(el => {
            const targetVal = parseFloat(el.getAttribute('data-target') || el.textContent.replace(/[^0-9.]/g, '') || '0');
            const isPercent = el.getAttribute('data-is-percent') === 'true' || el.textContent.includes('%');
            const prefix = el.getAttribute('data-prefix') || '';
            const suffix = isPercent ? '%' : (el.getAttribute('data-suffix') || '');

            const obj = { val: 0 };
            gsap.to(obj, {
                val: targetVal,
                duration: prefersReducedMotion ? 0.01 : 1.1,
                ease: 'power2.out',
                scrollTrigger: (typeof ScrollTrigger !== 'undefined') ? {
                    trigger: el,
                    start: 'top 92%',
                    toggleActions: 'play none none none'
                } : null,
                onUpdate: () => {
                    const current = Math.round(obj.val);
                    el.textContent = `${prefix}${current}${suffix}`;
                }
            });
        });
    }

    /**
     * 3. Conic Gauge Ring Animation (with dynamic color thresholds)
     */
    function animateCircularGauges() {
        if (typeof gsap === 'undefined') return;

        const gauges = document.querySelectorAll('.gauge-circle');
        gauges.forEach(gauge => {
            const targetPct = parseFloat(gauge.getAttribute('data-percent') || '0');
            const textEl = gauge.querySelector('.gauge-text');

            const gaugeState = { pct: 0 };

            gsap.to(gaugeState, {
                pct: targetPct,
                duration: prefersReducedMotion ? 0.01 : 1.2,
                ease: 'power2.out',
                scrollTrigger: (typeof ScrollTrigger !== 'undefined') ? {
                    trigger: gauge,
                    start: 'top 95%',
                    toggleActions: 'play none none none'
                } : null,
                onUpdate: () => {
                    const currentPct = Math.round(gaugeState.pct);
                    let color = '#184e96';
                    if (currentPct < 75) {
                        color = '#ef4444'; // Red Shortage
                    } else if (currentPct >= 85) {
                        color = '#10b981'; // Green Excellent
                    } else {
                        color = '#184e96'; // Blue Good
                    }

                    gauge.style.setProperty('--percent', currentPct);
                    gauge.style.setProperty('--gauge-color', color);
                    if (textEl) {
                        textEl.textContent = `${currentPct}%`;
                    }
                }
            });
        });
    }

    /**
     * 4. Linear Progress Bar Animation
     */
    function animateProgressBars() {
        if (typeof gsap === 'undefined') return;

        const progressBars = document.querySelectorAll('.progress-bar, [data-progress-target]');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('data-progress-target') || bar.style.width || '0%';
            bar.style.width = '0%';

            gsap.to(bar, {
                width: targetWidth,
                duration: prefersReducedMotion ? 0.01 : 1.0,
                ease: 'power2.out',
                scrollTrigger: (typeof ScrollTrigger !== 'undefined') ? {
                    trigger: bar,
                    start: 'top 95%',
                    toggleActions: 'play none none none'
                } : null
            });
        });
    }

    /**
     * 5. Interactive Cards & Action Buttons Hover / Click Micro-Interactions
     */
    function initCardAndButtonInteractions() {
        if (prefersReducedMotion || typeof gsap === 'undefined') return;

        // A. App Cards Hover Micro-Lift
        const cards = document.querySelectorAll('.app-card, .subject-card');
        cards.forEach(card => {
            const icon = card.querySelector('i');
            
            card.addEventListener('mouseenter', () => {
                gsap.to(card, {
                    y: -4,
                    scale: 1.012,
                    boxShadow: '0 10px 24px rgba(24, 78, 150, 0.12)',
                    duration: config.duration.fast,
                    ease: config.ease.smooth
                });
                if (icon && !card.classList.contains('no-icon-anim')) {
                    gsap.to(icon, {
                        scale: 1.12,
                        rotation: 6,
                        duration: config.duration.fast,
                        ease: config.ease.bounceSubtle
                    });
                }
            });

            card.addEventListener('mouseleave', () => {
                gsap.to(card, {
                    y: 0,
                    scale: 1.0,
                    boxShadow: '0 3px 12px rgba(18, 56, 108, 0.05)',
                    duration: config.duration.fast,
                    ease: config.ease.smooth
                });
                if (icon && !card.classList.contains('no-icon-anim')) {
                    gsap.to(icon, {
                        scale: 1.0,
                        rotation: 0,
                        duration: config.duration.fast,
                        ease: config.ease.smooth
                    });
                }
            });
        });

        // B. Action Circle Buttons
        const actionItems = document.querySelectorAll('.action-item');
        actionItems.forEach(item => {
            const circle = item.querySelector('.action-circle-btn');
            if (!circle) return;

            item.addEventListener('mouseenter', () => {
                gsap.to(circle, {
                    scale: 1.08,
                    y: -3,
                    duration: config.duration.fast,
                    ease: config.ease.bounceSubtle
                });
            });

            item.addEventListener('mouseleave', () => {
                gsap.to(circle, {
                    scale: 1.0,
                    y: 0,
                    duration: config.duration.fast,
                    ease: config.ease.smooth
                });
            });

            item.addEventListener('mousedown', () => {
                gsap.to(circle, {
                    scale: 0.94,
                    duration: config.duration.instant,
                    ease: config.ease.snappy
                });
            });

            item.addEventListener('mouseup', () => {
                gsap.to(circle, {
                    scale: 1.08,
                    duration: config.duration.instant,
                    ease: config.ease.bounceSubtle
                });
            });
        });

        // C. Standard Action Buttons Micro-Interactions
        const buttons = document.querySelectorAll('.btn:not(.no-anim)');
        buttons.forEach(btn => {
            btn.addEventListener('mousedown', () => {
                gsap.to(btn, {
                    scale: 0.96,
                    duration: config.duration.instant,
                    ease: config.ease.snappy
                });
            });

            btn.addEventListener('mouseup', () => {
                gsap.to(btn, {
                    scale: 1.0,
                    duration: config.duration.instant,
                    ease: config.ease.bounceSubtle
                });
            });

            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    scale: 1.0,
                    duration: config.duration.fast,
                    ease: config.ease.smooth
                });
            });
        });
    }

    /**
     * 6. Attendance Marking Interaction Feedback (Teacher Portal)
     */
    function initAttendanceMarkingInteractions() {
        const studentRows = document.querySelectorAll('.list-group-item[data-student-row]');
        
        studentRows.forEach(row => {
            const presentRadio = row.querySelector('input[value="present"]');
            const absentRadio = row.querySelector('input[value="absent"]');
            const avatar = row.querySelector('img, .avatar-circle, .rounded-circle');

            function triggerMarkFeedback(status) {
                if (prefersReducedMotion || typeof gsap === 'undefined') return;

                if (status === 'present') {
                    gsap.fromTo(row, 
                        { backgroundColor: 'rgba(220, 252, 231, 0.45)' },
                        { backgroundColor: 'transparent', duration: 0.6, ease: 'power2.out' }
                    );
                    if (avatar) {
                        gsap.fromTo(avatar, 
                            { scale: 1.15 }, 
                            { scale: 1.0, duration: 0.35, ease: 'back.out(2.0)' }
                        );
                    }
                } else if (status === 'absent') {
                    gsap.fromTo(row, 
                        { backgroundColor: 'rgba(254, 226, 226, 0.45)' },
                        { backgroundColor: 'transparent', duration: 0.6, ease: 'power2.out' }
                    );
                    if (avatar) {
                        gsap.fromTo(avatar, 
                            { x: -4 }, 
                            { x: 0, duration: 0.25, ease: 'elastic.out(1, 0.3)' }
                        );
                    }
                }
                updateLiveCounters();
            }

            if (presentRadio) {
                presentRadio.addEventListener('change', () => triggerMarkFeedback('present'));
            }
            if (absentRadio) {
                absentRadio.addEventListener('change', () => triggerMarkFeedback('absent'));
            }
        });
    }

    /**
     * Update and animate live attendance counter badges
     */
    function updateLiveCounters() {
        const presentRadios = document.querySelectorAll('input[type="radio"][value="present"]:checked');
        const absentRadios = document.querySelectorAll('input[type="radio"][value="absent"]:checked');

        const presentBadge = document.getElementById('count-present');
        const absentBadge = document.getElementById('count-absent');

        if (presentBadge) {
            const currentP = parseInt(presentBadge.textContent) || 0;
            const newP = presentRadios.length;
            if (currentP !== newP && typeof gsap !== 'undefined') {
                gsap.fromTo(presentBadge, 
                    { scale: 1.35, color: '#10b981' }, 
                    { scale: 1.0, color: 'inherit', duration: 0.3, ease: 'back.out(2)' }
                );
            }
            presentBadge.textContent = newP;
        }

        if (absentBadge) {
            const currentA = parseInt(absentBadge.textContent) || 0;
            const newA = absentRadios.length;
            if (currentA !== newA && typeof gsap !== 'undefined') {
                gsap.fromTo(absentBadge, 
                    { scale: 1.35, color: '#ef4444' }, 
                    { scale: 1.0, color: 'inherit', duration: 0.3, ease: 'back.out(2)' }
                );
            }
            absentBadge.textContent = newA;
        }
    }

    /**
     * Batch Mark All Students Helper
     */
    function markAllWithAnimation(status) {
        const radios = document.querySelectorAll(`input[type="radio"][value="${status}"]`);
        radios.forEach((r, index) => {
            r.checked = true;
            const row = r.closest('.list-group-item');
            if (row && typeof gsap !== 'undefined' && !prefersReducedMotion) {
                gsap.fromTo(row, 
                    { backgroundColor: status === 'present' ? 'rgba(220, 252, 231, 0.4)' : 'rgba(254, 226, 226, 0.4)' },
                    { backgroundColor: 'transparent', duration: 0.4, delay: index * 0.02, ease: 'power2.out' }
                );
            }
        });
        updateLiveCounters();
    }

    /**
     * 7. GSAP Toast Notification System
     */
    function showToast(title, message, type = 'info', durationMs = 4500) {
        let container = document.getElementById('attendx-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'attendx-toast-container';
            container.className = 'attendx-toast-container';
            document.body.appendChild(container);
        }

        const iconMap = {
            success: 'bi-check-circle-fill text-success',
            danger: 'bi-exclamation-triangle-fill text-danger',
            warning: 'bi-exclamation-circle-fill text-warning',
            info: 'bi-info-circle-fill text-primary'
        };

        const toast = document.createElement('div');
        toast.className = `attendx-toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="bi ${iconMap[type] || iconMap.info} fs-5"></i>
            </div>
            <div class="toast-content">
                <strong class="toast-title">${title}</strong>
                <div class="toast-msg">${message}</div>
            </div>
            <button type="button" class="toast-close" aria-label="Close">&times;</button>
        `;

        container.appendChild(toast);

        const closeBtn = toast.querySelector('.toast-close');
        const dismiss = () => {
            if (typeof gsap !== 'undefined' && !prefersReducedMotion) {
                gsap.to(toast, {
                    x: 60,
                    opacity: 0,
                    scale: 0.9,
                    duration: 0.25,
                    ease: 'power2.in',
                    onComplete: () => toast.remove()
                });
            } else {
                toast.remove();
            }
        };

        closeBtn.addEventListener('click', dismiss);

        // Slide in
        if (typeof gsap !== 'undefined' && !prefersReducedMotion) {
            gsap.fromTo(toast, 
                { x: 60, opacity: 0, scale: 0.92 },
                { x: 0, opacity: 1, scale: 1.0, duration: 0.35, ease: 'back.out(1.4)' }
            );
        }

        if (durationMs > 0) {
            setTimeout(dismiss, durationMs);
        }
    }

    /**
     * 8. GSAP Bootstrap Modal Enhancer
     */
    function initModalAnimations() {
        if (typeof gsap === 'undefined' || prefersReducedMotion) return;

        document.querySelectorAll('.modal').forEach(modalEl => {
            modalEl.addEventListener('show.bs.modal', () => {
                const dialog = modalEl.querySelector('.modal-dialog');
                if (dialog) {
                    gsap.fromTo(dialog, 
                        { scale: 0.92, y: 20, opacity: 0 },
                        { scale: 1.0, y: 0, opacity: 1, duration: 0.3, ease: 'back.out(1.5)' }
                    );
                }
            });
        });
    }

    /**
     * 9. Table Search & Filter Smooth Transitions
     */
    function initTableSearchFilter(searchInputId, targetRowsSelector) {
        const searchInput = document.getElementById(searchInputId);
        if (!searchInput) return;

        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase().trim();
            const rows = document.querySelectorAll(targetRowsSelector);

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const matches = text.includes(query);

                if (matches) {
                    if (row.style.display === 'none') {
                        row.style.display = '';
                        if (typeof gsap !== 'undefined' && !prefersReducedMotion) {
                            gsap.fromTo(row, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.2 });
                        }
                    }
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    /**
     * 10. Fast Page Transition
     */
    function initPageTransitions() {
        if (prefersReducedMotion || typeof gsap === 'undefined') return;

        // Intercept internal ERP navigation links safely
        document.querySelectorAll('a[href]:not([target="_blank"]):not([href^="#"]):not([href^="javascript"]):not([data-bs-toggle]):not([data-bs-target]):not([download]):not(.no-page-anim)').forEach(link => {
            link.addEventListener('click', (e) => {
                if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button !== 0) return;

                const targetUrl = link.getAttribute('href');
                if (!targetUrl || targetUrl.startsWith('#') || targetUrl.includes('/logout') || targetUrl.startsWith('mailto:') || targetUrl.startsWith('tel:')) return;

                // Animate main container out quickly
                const main = document.querySelector('main.app-container');
                if (main) {
                    e.preventDefault();
                    gsap.to(main, {
                        opacity: 0,
                        y: -10,
                        duration: 0.18,
                        ease: 'power2.in',
                        onComplete: () => {
                            window.location.href = targetUrl;
                        }
                    });
                }
            });
        });
    }

    /**
     * Initialize All Animation Subsystems
     */
    function initAll() {
        initPageLoadAnimations();
        animateCounters();
        animateCircularGauges();
        animateProgressBars();
        initCardAndButtonInteractions();
        initAttendanceMarkingInteractions();
        initModalAnimations();
        initPageTransitions();
        updateLiveCounters();
    }

    // Expose Public API
    return {
        init: initAll,
        toast: showToast,
        markAll: markAllWithAnimation,
        updateCounters: updateLiveCounters,
        initTableSearch: initTableSearchFilter,
        config: config
    };
})();

// Auto-run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', AttendXAnim.init);
} else {
    AttendXAnim.init();
}
