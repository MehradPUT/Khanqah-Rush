/**
 * Procedural Web Audio SFX Engine for Khanqah Rush
 * Generates crisp, low-latency audio without external dependencies
 */
export class SoundEngine {
	private ctx: AudioContext | null = null;
	private enabled: boolean = true;
	private masterGain: GainNode | null = null;

	// AudioContext is initialized on first user interaction (see initContext)
	private initContext() {
		if (!this.ctx) {
			const AudioCtx =
				window.AudioContext ||
				(window as unknown as { webkitAudioContext: typeof AudioContext })
					.webkitAudioContext;
			this.ctx = new AudioCtx();
			this.masterGain = this.ctx.createGain();
			this.masterGain.gain.setValueAtTime(0.8, this.ctx.currentTime);
			this.masterGain.connect(this.ctx.destination);
		}
		if (this.ctx.state === "suspended") {
			this.ctx.resume();
		}
	}

	public setEnabled(enabled: boolean) {
		this.enabled = enabled;
	}

	public isEnabled(): boolean {
		return this.enabled;
	}

	/**
	 * Sound when the axe strikes the sacred cypress
	 */
	public playChop(isYoung: boolean = false) {
		if (!this.enabled) return;
		this.initContext();
		if (!this.ctx || !this.masterGain) return;

		const t = this.ctx.currentTime;

		// 1. Thud / Wood Impact (Low-pitch downward frequency sweep)
		const osc = this.ctx.createOscillator();
		const gain = this.ctx.createGain();
		osc.type = isYoung ? "sawtooth" : "triangle";

		// Pitch: young is punchier and crisper
		const startFreq = isYoung ? 240 : 180;
		osc.frequency.setValueAtTime(startFreq, t);
		osc.frequency.exponentialRampToValueAtTime(35, t + 0.12);

		gain.gain.setValueAtTime(0.7, t);
		gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

		osc.connect(gain);
		gain.connect(this.masterGain);
		osc.start(t);
		osc.stop(t + 0.13);

		// 2. Splinter / Noise burst (Crack of wood fibers)
		const bufferSize = this.ctx.sampleRate * 0.06;
		const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
		const data = buffer.getChannelData(0);
		for (let i = 0; i < bufferSize; i++) {
			data[i] = Math.random() * 2 - 1;
		}

		const noise = this.ctx.createBufferSource();
		noise.buffer = buffer;

		const noiseFilter = this.ctx.createBiquadFilter();
		noiseFilter.type = "bandpass";
		noiseFilter.frequency.setValueAtTime(isYoung ? 3200 : 2000, t);
		noiseFilter.Q.setValueAtTime(3, t);

		const noiseGain = this.ctx.createGain();
		noiseGain.gain.setValueAtTime(isYoung ? 0.45 : 0.3, t);
		noiseGain.gain.exponentialRampToValueAtTime(0.001, t + 0.06);

		noise.connect(noiseFilter);
		noiseFilter.connect(noiseGain);
		noiseGain.connect(this.masterGain);

		noise.start(t);
	}

	/**
	 * Sound when Nima transforms into his Young form at 30s
	 */
	public playRejuvenation() {
		if (!this.enabled) return;
		this.initContext();
		if (!this.ctx || !this.masterGain) return;

		const t = this.ctx.currentTime;

		// Ascending mystical harmonic arpeggio (Persian Dastgah Homayoun / Shur flavor)
		const freqs = [330, 440, 554, 659, 880, 1108]; // E - A - C# - E - A - C#
		freqs.forEach((f, index) => {
			if (!this.ctx || !this.masterGain) return;
			const osc = this.ctx.createOscillator();
			const gain = this.ctx.createGain();

			osc.type = "sine";
			osc.frequency.setValueAtTime(f, t + index * 0.06);

			gain.gain.setValueAtTime(0, t + index * 0.06);
			gain.gain.linearRampToValueAtTime(0.3, t + index * 0.06 + 0.02);
			gain.gain.exponentialRampToValueAtTime(0.001, t + index * 0.06 + 0.8);

			osc.connect(gain);
			gain.connect(this.masterGain);

			osc.start(t + index * 0.06);
			osc.stop(t + index * 0.06 + 0.85);
		});

		// Surge bass boom
		const subOsc = this.ctx.createOscillator();
		const subGain = this.ctx.createGain();
		subOsc.type = "triangle";
		subOsc.frequency.setValueAtTime(120, t);
		subOsc.frequency.exponentialRampToValueAtTime(30, t + 0.9);
		subGain.gain.setValueAtTime(0.8, t);
		subGain.gain.exponentialRampToValueAtTime(0.001, t + 0.9);

		subOsc.connect(subGain);
		subGain.connect(this.masterGain);
		subOsc.start(t);
		subOsc.stop(t + 0.95);
	}

	/**
	 * Revert back to old form sound
	 */
	public playRevert() {
		if (!this.enabled) return;
		this.initContext();
		if (!this.ctx || !this.masterGain) return;

		const t = this.ctx.currentTime;
		const osc = this.ctx.createOscillator();
		const gain = this.ctx.createGain();

		osc.type = "sine";
		osc.frequency.setValueAtTime(520, t);
		osc.frequency.exponentialRampToValueAtTime(180, t + 0.6);

		gain.gain.setValueAtTime(0.3, t);
		gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6);

		osc.connect(gain);
		gain.connect(this.masterGain);
		osc.start(t);
		osc.stop(t + 0.65);
	}

	/**
	 * Sound on branch collision or stamina exhaustion (Defeat Gong)
	 */
	public playDeath() {
		if (!this.enabled) return;
		this.initContext();
		if (!this.ctx || !this.masterGain) return;

		const t = this.ctx.currentTime;

		// Heavy crash impact
		const osc = this.ctx.createOscillator();
		const gain = this.ctx.createGain();
		osc.type = "sawtooth";
		osc.frequency.setValueAtTime(90, t);
		osc.frequency.exponentialRampToValueAtTime(20, t + 0.5);

		gain.gain.setValueAtTime(0.9, t);
		gain.gain.exponentialRampToValueAtTime(0.001, t + 0.5);

		osc.connect(gain);
		gain.connect(this.masterGain);
		osc.start(t);
		osc.stop(t + 0.55);

		// Dissonant metallic clang
		const clang = this.ctx.createOscillator();
		const clangGain = this.ctx.createGain();
		clang.type = "square";
		clang.frequency.setValueAtTime(154, t);
		clangGain.gain.setValueAtTime(0.4, t);
		clangGain.gain.exponentialRampToValueAtTime(0.001, t + 0.8);

		clang.connect(clangGain);
		clangGain.connect(this.masterGain);
		clang.start(t);
		clang.stop(t + 0.85);
	}

	/**
	 * Combo celebration chime
	 */
	public playStreak(streakCount: number) {
		if (!this.enabled) return;
		this.initContext();
		if (!this.ctx || !this.masterGain) return;

		const t = this.ctx.currentTime;
		const baseFreq = 440; // A4
		const steps = [0, 2, 4, 7, 9, 12]; // Pentatonic
		const noteIndex = Math.min(Math.floor(streakCount / 10), steps.length - 1);
		const freq = baseFreq * 2 ** (steps[noteIndex] / 12);

		const osc = this.ctx.createOscillator();
		const gain = this.ctx.createGain();

		osc.type = "sine";
		osc.frequency.setValueAtTime(freq, t);

		gain.gain.setValueAtTime(0.35, t);
		gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);

		osc.connect(gain);
		gain.connect(this.masterGain);
		osc.start(t);
		osc.stop(t + 0.35);
	}
}
