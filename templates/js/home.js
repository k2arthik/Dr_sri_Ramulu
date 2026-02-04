/**
 * Contains slideshow and modal code for home page
 */

function initHome() {
    console.log("Initializing Slideshow and Modals...");
    // Slideshow with 10s interval
    const container = document.querySelector(".review-container");
    if (container) {
        new SlideShow(container, true, 10000);
    }

    // Modal
    const modalEl = document.querySelector("#modal");
    if (modalEl) new Modal(modalEl);

    // Counters
    animateCounters();
}

// Global scope check to run as soon as possible
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initHome();
} else {
    document.addEventListener('DOMContentLoaded', initHome);
}
// Fallback for slower assets
window.addEventListener('load', () => {
    const counters = document.querySelectorAll('.counter');
    if (counters.length && counters[0].innerText === '0') {
        animateCounters();
    }
});
