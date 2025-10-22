// Sound Effects Manager
// Generates sounds programmatically using Web Audio API

class SoundManager {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.volume = 0.3; // 30% volume
        
        // Initialize audio context on first user interaction
        this.initAudioContext();
    }

    initAudioContext() {
        // Create audio context on first user interaction (browser requirement)
        document.addEventListener('click', () => {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                console.log('🔊 Sound system initialized');
            }
        }, { once: true });
    }

    getAudioContext() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.audioContext;
    }

    // Play success tick sound (for scan success)
    playTickSound() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            // Create a pleasant "tick" sound
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(this.volume, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);

            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.1);
        } catch (e) {
            console.warn('Could not play tick sound:', e);
        }
    }

    // Play success sound (for NFC scan)
    playScanSuccess() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            
            // Two-tone success beep
            this.playTone(ctx, 600, 0.05, 0);
            this.playTone(ctx, 800, 0.1, 0.06);
        } catch (e) {
            console.warn('Could not play scan sound:', e);
        }
    }

    // Play drag sound (for drag-drop)
    playDragSound() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            // Swoosh sound
            oscillator.frequency.setValueAtTime(400, ctx.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.15);
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(this.volume * 0.5, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.15);

            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.15);
        } catch (e) {
            console.warn('Could not play drag sound:', e);
        }
    }

    // Play delete sound
    playDeleteSound() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            
            // Descending tone for delete
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            oscillator.frequency.setValueAtTime(600, ctx.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.2);
            oscillator.type = 'square';

            gainNode.gain.setValueAtTime(this.volume * 0.4, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);

            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.2);
        } catch (e) {
            console.warn('Could not play delete sound:', e);
        }
    }

    // Play error sound
    playErrorSound() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            
            // Harsh buzz for error
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            oscillator.frequency.value = 200;
            oscillator.type = 'sawtooth';

            gainNode.gain.setValueAtTime(this.volume * 0.6, ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);

            oscillator.start(ctx.currentTime);
            oscillator.stop(ctx.currentTime + 0.3);
        } catch (e) {
            console.warn('Could not play error sound:', e);
        }
    }

    // Play countdown beep
    playCountdownBeep() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            this.playTone(ctx, 1000, 0.1, 0);
        } catch (e) {
            console.warn('Could not play countdown beep:', e);
        }
    }

    // Play final countdown sound (for "Smile!")
    playCountdownFinal() {
        if (!this.enabled) return;
        
        try {
            const ctx = this.getAudioContext();
            
            // Three quick ascending tones
            this.playTone(ctx, 800, 0.08, 0);
            this.playTone(ctx, 1000, 0.08, 0.1);
            this.playTone(ctx, 1200, 0.15, 0.2);
        } catch (e) {
            console.warn('Could not play countdown final:', e);
        }
    }

    // Helper function to play a tone
    playTone(ctx, frequency, duration, startTime) {
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';

        const start = ctx.currentTime + startTime;
        gainNode.gain.setValueAtTime(this.volume, start);
        gainNode.gain.exponentialRampToValueAtTime(0.01, start + duration);

        oscillator.start(start);
        oscillator.stop(start + duration);
    }

    // Toggle sound on/off
    toggleSound() {
        this.enabled = !this.enabled;
        console.log(`🔊 Sound ${this.enabled ? 'enabled' : 'disabled'}`);
        return this.enabled;
    }

    // Set volume (0.0 to 1.0)
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        console.log(`🔊 Volume set to ${Math.round(this.volume * 100)}%`);
    }
}

// Create global sound manager instance
const soundManager = new SoundManager();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = soundManager;
}
