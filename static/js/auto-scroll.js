/**
 * TabStash - Auto-scroll for hands-free practice
 *
 * Usage:
 *   const scroller = new AutoScroll(contentElement);
 *   scroller.start();
 *   scroller.stop();
 *   scroller.toggle();
 *   scroller.setSpeed('slow' | 'medium' | 'fast');
 */

class AutoScroll {
    constructor(container) {
        this.container = container;
        this.isScrolling = false;
        this.lastTime = 0;
        this.animationId = null;

        // Speed in pixels per second
        this.speeds = {
            slow: 20,
            medium: 40,
            fast: 70
        };
        this.currentSpeed = this.speeds.medium;

        // Create scroll indicator
        this.indicator = document.createElement('div');
        this.indicator.className = 'scroll-indicator';
        this.indicator.textContent = 'Scrolling...';
        document.body.appendChild(this.indicator);
    }

    start() {
        if (this.isScrolling) return;

        this.isScrolling = true;
        this.lastTime = performance.now();
        this.indicator.classList.add('visible');
        this.scroll();
    }

    stop() {
        this.isScrolling = false;
        this.indicator.classList.remove('visible');

        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    toggle() {
        if (this.isScrolling) {
            this.stop();
        } else {
            this.start();
        }
    }

    setSpeed(speedName) {
        if (this.speeds[speedName]) {
            this.currentSpeed = this.speeds[speedName];
        }
    }

    scroll() {
        if (!this.isScrolling) return;

        const now = performance.now();
        const delta = (now - this.lastTime) / 1000;
        this.lastTime = now;

        window.scrollBy(0, this.currentSpeed * delta);

        // Check if we've reached the bottom
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;

        if (scrollTop + clientHeight >= scrollHeight - 10) {
            this.stop();
            return;
        }

        this.animationId = requestAnimationFrame(() => this.scroll());
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutoScroll;
}
