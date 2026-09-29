import type {
	CharacterPhase,
	VoicePreset,
} from "../characters/characterTypes.ts";

export class VoiceEngine {
	private enabled: boolean = false;
	private subtitleElement: HTMLElement | null = null;
	private speechTextElement: HTMLElement | null = null;
	private subtitleTimeout: number | null = null;

	constructor() {
		this.subtitleElement = document.getElementById("voiceSubtitle");
		this.speechTextElement = document.getElementById("speechText");
	}

	public setEnabled(enabled: boolean) {
		this.enabled = enabled;
	}

	public isEnabled(): boolean {
		return this.enabled;
	}

	/**
	 * Character sound effects and speech synthesis have been completely removed.
	 */
	public speak(
		_phase: CharacterPhase,
		_voiceConfig: VoicePreset,
		_event:
			| "start"
			| "chop"
			| "streak"
			| "abilityTrigger"
			| "abilityRevert"
			| "death",
		_force: boolean = false,
	) {
		// Custom sound effects and voice synthesis for characters are permanently removed.
		return;
	}

	/**
	 * Display floating subtitle if needed
	 */
	public displaySubtitle(text: string) {
		if (!this.subtitleElement || !this.speechTextElement) return;

		this.speechTextElement.textContent = text;
		this.subtitleElement.classList.remove("hidden");

		if (this.subtitleTimeout) {
			window.clearTimeout(this.subtitleTimeout);
		}

		this.subtitleTimeout = window.setTimeout(() => {
			if (this.subtitleElement) {
				this.subtitleElement.classList.add("hidden");
			}
		}, 1800);
	}
}
