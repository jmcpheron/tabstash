/**
 * TabStash - Metronome for practice timing
 *
 * Usage:
 *   const metronome = new Metronome({ bpm: 120, onBeat: callback });
 *   metronome.start();  // Requires user interaction first (iOS Safari)
 *   metronome.stop();
 *   metronome.setBpm(140);
 *   metronome.toggle();
 */

class Metronome {
    constructor(options = {}) {
        // Configuration
        this.bpm = options.bpm || 120;
        this.onBeat = options.onBeat || null;
        this.onBpmChange = options.onBpmChange || null;

        // State
        this.isRunning = false;
        this.beatCount = 0;
        this.beatsPerMeasure = 4;  // For accent on beat 1

        // Web Audio API (lazy initialization for iOS Safari)
        this.audioContext = null;
        this.nextBeatTime = 0;
        this.schedulerTimerId = null;

        // Scheduler settings (lookahead approach for accuracy)
        this.lookahead = 25;          // ms - how often to call scheduler
        this.scheduleAheadTime = 0.1; // seconds - how far ahead to schedule

        // Sound settings
        this.clickFrequency = 1000;      // Hz - normal beat
        this.accentFrequency = 1500;     // Hz - accent beat (beat 1)
        this.clickDuration = 0.05;       // seconds
    }

    // Initialize AudioContext (must be called from user gesture)
    initAudio() {
        if (this.audioContext) return;

        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

        // iOS Safari requires resume after user gesture
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
    }

    // Generate click sound using oscillator
    playClick(time, isAccent = false) {
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();

        osc.connect(gain);
        gain.connect(this.audioContext.destination);

        osc.frequency.value = isAccent ? this.accentFrequency : this.clickFrequency;
        osc.type = 'sine';

        // Quick attack and decay envelope
        gain.gain.setValueAtTime(0.5, time);
        gain.gain.exponentialRampToValueAtTime(0.001, time + this.clickDuration);

        osc.start(time);
        osc.stop(time + this.clickDuration);
    }

    // Scheduler - runs frequently to schedule upcoming beats
    scheduler() {
        while (this.nextBeatTime < this.audioContext.currentTime + this.scheduleAheadTime) {
            const isAccent = (this.beatCount % this.beatsPerMeasure) === 0;
            this.playClick(this.nextBeatTime, isAccent);

            // Trigger visual callback
            if (this.onBeat) {
                const beatTime = this.nextBeatTime;
                const delay = Math.max(0, (beatTime - this.audioContext.currentTime) * 1000);
                const currentBeat = this.beatCount;
                const accent = isAccent;
                setTimeout(() => this.onBeat(currentBeat, accent), delay);
            }

            // Advance to next beat
            this.beatCount++;
            this.nextBeatTime += 60.0 / this.bpm;
        }
    }

    start() {
        if (this.isRunning) return;

        this.initAudio();

        // Resume context if suspended (iOS Safari)
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        this.isRunning = true;
        this.beatCount = 0;
        this.nextBeatTime = this.audioContext.currentTime + 0.05; // Small delay

        this.schedulerTimerId = setInterval(() => this.scheduler(), this.lookahead);
    }

    stop() {
        this.isRunning = false;

        if (this.schedulerTimerId) {
            clearInterval(this.schedulerTimerId);
            this.schedulerTimerId = null;
        }
    }

    toggle() {
        if (this.isRunning) {
            this.stop();
        } else {
            this.start();
        }
        return this.isRunning;
    }

    setBpm(bpm) {
        // Clamp to valid range (matches model.py: 20-300)
        this.bpm = Math.max(20, Math.min(300, parseInt(bpm, 10) || 120));

        if (this.onBpmChange) {
            this.onBpmChange(this.bpm);
        }

        return this.bpm;
    }

    getBpm() {
        return this.bpm;
    }

    // Get milliseconds per beat (useful for sync calculations)
    getMsPerBeat() {
        return 60000 / this.bpm;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Metronome;
}
