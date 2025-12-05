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
        this.accumulatedScroll = 0;  // Accumulator for sub-pixel values (iOS fix)

        // Speed in pixels per second
        this.speeds = {
            slow: 20,
            medium: 40,
            fast: 70
        };
        this.currentSpeed = this.speeds.medium;

        // Sync mode (BPM-driven scrolling)
        this.syncMode = false;
        this.syncPixelsPerBeat = 0;
        this.lastManualSpeed = this.currentSpeed;

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
        this.accumulatedScroll = 0;  // Reset accumulator
        this.indicator.classList.add('visible');

        // Disable smooth scrolling during auto-scroll (fixes iOS Safari)
        document.documentElement.style.scrollBehavior = 'auto';

        this.scroll();
    }

    stop() {
        this.isScrolling = false;
        this.indicator.classList.remove('visible');

        // Restore smooth scrolling
        document.documentElement.style.scrollBehavior = '';

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
            this.lastManualSpeed = this.currentSpeed;
        }
    }

    // Enable sync mode with BPM-driven scrolling
    enableSync(pixelsPerBeat, bpm) {
        this.syncMode = true;
        this.syncPixelsPerBeat = pixelsPerBeat;
        // Calculate speed: pixels/beat * beats/minute / 60 = pixels/second
        this.currentSpeed = (pixelsPerBeat * bpm) / 60;
    }

    // Disable sync mode and restore manual speed
    disableSync() {
        this.syncMode = false;
        this.currentSpeed = this.lastManualSpeed;
    }

    // Update sync speed when BPM changes
    updateSyncBpm(bpm) {
        if (this.syncMode) {
            this.currentSpeed = (this.syncPixelsPerBeat * bpm) / 60;
        }
    }

    // Check if in sync mode
    isSynced() {
        return this.syncMode;
    }

    scroll() {
        if (!this.isScrolling) return;

        const now = performance.now();
        const delta = (now - this.lastTime) / 1000;
        this.lastTime = now;

        // Accumulate fractional pixels (iOS Safari ignores sub-pixel scrollBy)
        this.accumulatedScroll += this.currentSpeed * delta;

        // Only scroll when we have at least 1 whole pixel
        if (this.accumulatedScroll >= 1) {
            const scrollAmount = Math.floor(this.accumulatedScroll);
            this.accumulatedScroll -= scrollAmount;

            // Use scrollTo for better iOS Safari compatibility
            const currentY = window.pageYOffset || document.documentElement.scrollTop;
            window.scrollTo(0, currentY + scrollAmount);
        }

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
