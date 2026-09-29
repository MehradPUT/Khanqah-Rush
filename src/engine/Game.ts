import { SoundEngine } from "../audio/SoundEngine.ts";
import { VoiceEngine } from "../audio/VoiceEngine.ts";
import type {
	CharacterConfig,
	CharacterPhase,
} from "../characters/characterTypes.ts";
import { nimaCharacter } from "../characters/nima.ts";
import { TmaBridge } from "../telegram/tma.ts";
import { ParticleSystem } from "./Particles.ts";
import { Pillar } from "./Pillar.ts";

export type GameState = "MENU" | "PLAYING" | "GAME_OVER";

export class Game {
	private canvas: HTMLCanvasElement;
	private ctx: CanvasRenderingContext2D;
	private width: number = 400;
	private height: number = 700;
	private state: GameState = "MENU";

	// Systems
	private pillar: Pillar;
	private particles: ParticleSystem;
	private soundEngine: SoundEngine;
	private voiceEngine: VoiceEngine;
	private tma: TmaBridge;

	// Character & Phases
	private character: CharacterConfig = nimaCharacter;
	private currentPhase: CharacterPhase = "old";
	private playerSide: "LEFT" | "RIGHT" = "LEFT";
	private swingTimer: number = 0;

	// Gameplay Variables
	private score: number = 0;
	private highScore: number = 0;
	private stamina: number = 1.0;
	private survivalTime: number = 0.0;
	private rejuvenationCount: number = 0;
	private rejuvenationCooldown: number = 0; // 0 to 30s
	private rejuvenationActiveTimer: number = 0; // 5s to 0s

	// Timing
	private lastFrameTime: number = 0;

	// DOM Elements
	private hudElement: HTMLElement | null = null;
	private scoreDisplay: HTMLElement | null = null;
	private bestScoreDisplay: HTMLElement | null = null;
	private staminaFill: HTMLElement | null = null;
	private abilityIndicator: HTMLElement | null = null;
	private phaseAvatar: HTMLElement | null = null;
	private phaseTag: HTMLElement | null = null;
	private gaugeTitle: HTMLElement | null = null;
	private gaugeTime: HTMLElement | null = null;
	private gaugeFill: HTMLElement | null = null;
	private vfxOverlay: HTMLElement | null = null;
	private startMenu: HTMLElement | null = null;
	private gameOverMenu: HTMLElement | null = null;

	constructor(canvas: HTMLCanvasElement) {
		this.canvas = canvas;
		const context = canvas.getContext("2d");
		if (!context) throw new Error("Could not get 2D canvas context");
		this.ctx = context;

		this.pillar = new Pillar();
		this.particles = new ParticleSystem();
		this.soundEngine = new SoundEngine();
		this.voiceEngine = new VoiceEngine();
		this.tma = TmaBridge.getInstance();

		this.loadHighScore();
		this.bindDomElements();
		this.bindEvents();
		this.resize();

		window.addEventListener("resize", () => this.resize());
	}

	private loadHighScore() {
		try {
			const saved = localStorage.getItem("khanqah_rush_highscore");
			this.highScore = saved ? parseInt(saved, 10) || 0 : 0;
		} catch {
			this.highScore = 0;
		}
	}

	private saveHighScore() {
		try {
			localStorage.setItem("khanqah_rush_highscore", this.highScore.toString());
		} catch {
			// Ignore storage errors
		}
	}

	private bindDomElements() {
		this.hudElement = document.getElementById("hud");
		this.scoreDisplay = document.getElementById("scoreDisplay");
		this.bestScoreDisplay = document.getElementById("bestScoreDisplay");
		this.staminaFill = document.getElementById("staminaFill");
		this.abilityIndicator = document.getElementById("abilityIndicator");
		this.phaseAvatar = document.getElementById("phaseAvatar");
		this.phaseTag = document.getElementById("phaseTag");
		this.gaugeTitle = document.getElementById("gaugeTitle");
		this.gaugeTime = document.getElementById("gaugeTime");
		this.gaugeFill = document.getElementById("gaugeFill");
		this.vfxOverlay = document.getElementById("vfxOverlay");
		this.startMenu = document.getElementById("startMenu");
		this.gameOverMenu = document.getElementById("gameOverMenu");

		if (this.bestScoreDisplay) {
			this.bestScoreDisplay.textContent = this.highScore.toString();
		}
	}

	private bindEvents() {
		// Keyboard inputs
		window.addEventListener("keydown", (e) => {
			if (this.state === "PLAYING") {
				if (e.code === "ArrowLeft" || e.code === "KeyA" || e.code === "KeyH") {
					this.handleChop("LEFT");
				} else if (
					e.code === "ArrowRight" ||
					e.code === "KeyD" ||
					e.code === "KeyL"
				) {
					this.handleChop("RIGHT");
				}
			} else if (
				this.state === "MENU" &&
				(e.code === "Space" || e.code === "Enter")
			) {
				this.startGame();
			} else if (
				this.state === "GAME_OVER" &&
				(e.code === "Space" || e.code === "Enter")
			) {
				this.restartGame();
			}
		});

		// Touch zones
		const btnLeft = document.getElementById("btnChopLeft");
		const btnRight = document.getElementById("btnChopRight");

		const handleLeft = (e: Event) => {
			e.preventDefault();
			if (this.state === "PLAYING") this.handleChop("LEFT");
		};

		const handleRight = (e: Event) => {
			e.preventDefault();
			if (this.state === "PLAYING") this.handleChop("RIGHT");
		};

		btnLeft?.addEventListener("pointerdown", handleLeft);
		btnRight?.addEventListener("pointerdown", handleRight);

		// Menu Buttons
		document
			.getElementById("btnStartGame")
			?.addEventListener("click", () => this.startGame());
		document
			.getElementById("btnPlayAgain")
			?.addEventListener("click", () => this.restartGame());
		document
			.getElementById("btnShareTelegram")
			?.addEventListener("click", () => {
				this.tma.shareScore(
					this.score,
					this.character.name,
					`${this.survivalTime.toFixed(1)}s`,
				);
			});

		// Audio Toggles
		const soundToggle = document.getElementById("btnToggleSound");
		const voiceToggle = document.getElementById("btnToggleVoice");

		soundToggle?.addEventListener("click", () => {
			const enabled = !this.soundEngine.isEnabled();
			this.soundEngine.setEnabled(enabled);
			const icon = document.getElementById("soundIcon");
			const status = document.getElementById("soundStatus");
			if (icon) icon.textContent = enabled ? "🔊" : "🔇";
			if (status) status.textContent = enabled ? "ON" : "OFF";
		});

		voiceToggle?.addEventListener("click", () => {
			const enabled = !this.voiceEngine.isEnabled();
			this.voiceEngine.setEnabled(enabled);
			const icon = document.getElementById("voiceIcon");
			const status = document.getElementById("voiceStatus");
			if (icon) icon.textContent = enabled ? "🎙️" : "🔇";
			if (status) status.textContent = enabled ? "ON" : "OFF";
		});
	}

	public resize() {
		const dpr = window.devicePixelRatio || 1;
		const rect = this.canvas.parentElement?.getBoundingClientRect() || {
			width: 400,
			height: 700,
		};

		this.width = rect.width;
		this.height = rect.height;

		this.canvas.width = this.width * dpr;
		this.canvas.height = this.height * dpr;

		this.ctx.resetTransform();
		this.ctx.scale(dpr, dpr);
	}

	public startLoop() {
		this.lastFrameTime = performance.now();
		requestAnimationFrame((t) => this.gameLoop(t));
	}

	private gameLoop(time: number) {
		const dt = Math.min((time - this.lastFrameTime) / 1000, 0.1);
		this.lastFrameTime = time;

		this.update(dt);
		this.draw();

		requestAnimationFrame((t) => this.gameLoop(t));
	}

	public startGame() {
		this.state = "PLAYING";
		this.score = 0;
		this.stamina = 1.0;
		this.survivalTime = 0.0;
		this.rejuvenationCount = 0;
		this.rejuvenationCooldown = 0.0;
		this.rejuvenationActiveTimer = 0.0;
		this.currentPhase = "old";
		this.playerSide = "LEFT";
		this.swingTimer = 0;

		this.pillar.reset();

		// UI visibility
		this.startMenu?.classList.add("hidden");
		this.gameOverMenu?.classList.add("hidden");
		this.hudElement?.classList.remove("hidden");

		this.updateHud();

		// Play start voice line
		this.voiceEngine.speak(
			this.currentPhase,
			this.character.phases[this.currentPhase].voice,
			"start",
			true,
		);
	}

	public restartGame() {
		this.startGame();
	}

	private handleChop(side: "LEFT" | "RIGHT") {
		if (this.state !== "PLAYING") return;

		this.playerSide = side;
		this.swingTimer = 0.14; // swing animation duration

		const trunkCenterX = this.width / 2;
		const trunkBaseY = this.height * 0.72;

		const isYoung = this.currentPhase === "young";

		// 1. Play Sound & Haptic
		this.soundEngine.playChop(isYoung);
		this.tma.triggerHaptic(isYoung ? "medium" : "light");

		// 2. Splinter Particles & Shake
		const playerX = side === "LEFT" ? trunkCenterX - 55 : trunkCenterX + 55;
		this.particles.addSplinters(playerX, trunkBaseY - 30, side, isYoung);
		this.particles.triggerShake(isYoung ? 6 : 3.5);

		// 3. Chop bottom segment
		this.pillar.chop(side, trunkCenterX, trunkBaseY - 50);
		this.score++;

		// 4. Voice chop grunt
		this.voiceEngine.speak(
			this.currentPhase,
			this.character.phases[this.currentPhase].voice,
			"chop",
		);

		// 5. Refill Stamina slightly on chop
		if (this.currentPhase === "old") {
			this.stamina = Math.min(1.0, this.stamina + 0.065);
		} else {
			// In Young phase, stamina is locked at full!
			this.stamina = 1.0;
		}

		// 6. Streak celebration sound on multiples of 25
		if (this.score > 0 && this.score % 25 === 0) {
			this.soundEngine.playStreak(this.score);
			this.voiceEngine.speak(
				this.currentPhase,
				this.character.phases[this.currentPhase].voice,
				"streak",
				true,
			);
		}

		// 7. Check immediate collision with new bottom branch
		const incomingBranch = this.pillar.segments[0];
		if (incomingBranch === this.playerSide) {
			this.triggerGameOver("branch_hit");
			return;
		}

		this.updateHud();
	}

	private update(dt: number) {
		this.pillar.update(dt);
		this.particles.update(dt);

		if (this.swingTimer > 0) {
			this.swingTimer -= dt;
		}

		if (this.state === "PLAYING") {
			this.survivalTime += dt;

			// Handle Rejuvenation Cycle
			if (this.currentPhase === "old") {
				this.rejuvenationCooldown += dt;

				// Has reached 30 seconds -> Activate Young Phase!
				if (
					this.rejuvenationCooldown >=
					this.character.ability.chargeDurationSeconds
				) {
					this.activateRejuvenation();
				}
			} else if (this.currentPhase === "young") {
				this.rejuvenationActiveTimer -= dt;

				// Lock stamina at 100% (he does not get tired!)
				this.stamina = 1.0;

				// Has expired after 5 seconds -> Revert to Old Phase!
				if (this.rejuvenationActiveTimer <= 0) {
					this.revertToOldPhase();
				}
			}

			// Handle Stamina Drain
			if (this.currentPhase === "old") {
				// Decay accelerates gradually with score
				const baseDrain = 0.16 + Math.min(this.score * 0.0012, 0.22);
				this.stamina -= baseDrain * dt;

				if (this.stamina <= 0) {
					this.stamina = 0;
					this.triggerGameOver("exhaustion");
					return;
				}
			}

			this.updateHud();
		}
	}

	/**
	 * Activates Nima's Young Rejuvenation phase
	 */
	private activateRejuvenation() {
		this.currentPhase = "young";
		this.rejuvenationActiveTimer = this.character.ability.activeDurationSeconds; // 5 seconds
		this.rejuvenationCooldown = 0.0;
		this.rejuvenationCount++;

		// Audio & Haptics
		this.soundEngine.playRejuvenation();
		this.tma.triggerHaptic("heavy");
		this.tma.triggerHapticNotification("success");

		// Voice trigger
		this.voiceEngine.speak(
			"young",
			this.character.phases.young.voice,
			"abilityTrigger",
			true,
		);

		// Particle Burst & Shake
		const trunkCenterX = this.width / 2;
		const trunkBaseY = this.height * 0.72;
		const playerX =
			this.playerSide === "LEFT" ? trunkCenterX - 85 : trunkCenterX + 85;
		this.particles.addRejuvenationBurst(playerX, trunkBaseY - 40);
		this.particles.triggerShake(14);

		// Visual Flash
		if (this.vfxOverlay) {
			this.vfxOverlay.className = "vfx-overlay flash-rejuvenate";
			setTimeout(() => {
				if (this.vfxOverlay) this.vfxOverlay.className = "vfx-overlay";
			}, 450);
		}
	}

	/**
	 * Reverts Nima back to his Old phase
	 */
	private revertToOldPhase() {
		this.currentPhase = "old";
		this.rejuvenationActiveTimer = 0.0;
		this.rejuvenationCooldown = 0.0;

		this.soundEngine.playRevert();
		this.voiceEngine.speak(
			"young",
			this.character.phases.young.voice,
			"abilityRevert",
			true,
		);
	}

	private triggerGameOver(reason: "branch_hit" | "exhaustion") {
		this.state = "GAME_OVER";

		this.soundEngine.playDeath();
		this.tma.triggerHapticNotification("error");

		// Death voice line
		this.voiceEngine.speak(
			this.currentPhase,
			this.character.phases[this.currentPhase].voice,
			"death",
			true,
		);

		// Screen flash red
		if (this.vfxOverlay) {
			this.vfxOverlay.className = "vfx-overlay flash-hit";
			setTimeout(() => {
				if (this.vfxOverlay) this.vfxOverlay.className = "vfx-overlay";
			}, 350);
		}

		if (this.score > this.highScore) {
			this.highScore = this.score;
			this.saveHighScore();
		}

		// Populate Game Over Menu
		const finalScoreEl = document.getElementById("finalScore");
		const finalSurvivalEl = document.getElementById("finalSurvivalTime");
		const finalRejuvenationEl = document.getElementById(
			"finalRejuvenationCount",
		);
		const bestScoreFinalEl = document.getElementById("bestScoreFinal");
		const defeatSpeechEl = document.getElementById("defeatSpeech");

		if (finalScoreEl) finalScoreEl.textContent = this.score.toString();
		if (finalSurvivalEl)
			finalSurvivalEl.textContent = `${this.survivalTime.toFixed(1)}s`;
		if (finalRejuvenationEl)
			finalRejuvenationEl.textContent = this.rejuvenationCount.toString();
		if (bestScoreFinalEl)
			bestScoreFinalEl.textContent = this.highScore.toString();

		if (defeatSpeechEl) {
			defeatSpeechEl.textContent =
				reason === "branch_hit"
					? '"عجب شاخه‌ای بود... کمرم شکست!"'
					: '"آه... نفسم گرفت!"';
		}

		this.gameOverMenu?.classList.remove("hidden");
	}

	private updateHud() {
		if (this.scoreDisplay)
			this.scoreDisplay.textContent = this.score.toString();
		if (this.bestScoreDisplay)
			this.bestScoreDisplay.textContent = this.highScore.toString();

		// Update Stamina Bar
		if (this.staminaFill) {
			this.staminaFill.style.width = `${Math.max(0, Math.min(100, this.stamina * 100))}%`;
			if (this.currentPhase === "young") {
				this.staminaFill.classList.add("frozen");
			} else {
				this.staminaFill.classList.remove("frozen");
			}
		}

		// Update Phase & Rejuvenation Gauge
		const isYoung = this.currentPhase === "young";

		if (this.abilityIndicator) {
			if (isYoung) {
				this.abilityIndicator.classList.add("active-rejuvenation");
			} else {
				this.abilityIndicator.classList.remove("active-rejuvenation");
			}
		}

		if (this.phaseAvatar) {
			const avatarIcon = this.phaseAvatar.querySelector(".avatar-icon");
			if (avatarIcon) {
				avatarIcon.textContent = isYoung ? "🧔🏻" : "👴";
			}
		}

		if (this.phaseTag) {
			this.phaseTag.textContent = isYoung ? "YOUNG" : "OLD";
		}

		if (this.gaugeTitle) {
			this.gaugeTitle.textContent = isYoung
				? "🔥 YOUTH FRENZY (TIRED: NO)"
				: "YOUTH REJUVENATION";
		}

		if (this.gaugeTime) {
			if (isYoung) {
				this.gaugeTime.textContent = `${Math.max(0, this.rejuvenationActiveTimer).toFixed(1)}s / 5s`;
			} else {
				this.gaugeTime.textContent = `${Math.floor(this.rejuvenationCooldown)}s / 30s`;
			}
		}

		if (this.gaugeFill) {
			if (isYoung) {
				const pct = (this.rejuvenationActiveTimer / 5.0) * 100;
				this.gaugeFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
			} else {
				const pct = (this.rejuvenationCooldown / 30.0) * 100;
				this.gaugeFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
			}
		}
	}

	private draw() {
		this.ctx.save();
		this.ctx.clearRect(0, 0, this.width, this.height);

		// Apply Screen Shake
		this.particles.applyShake(this.ctx);

		// 1. Draw Background (Persian Night Sky & Mosque Silhouettes)
		this.drawBackground();

		// 2. Draw Pillar / Sacred Cypress
		const trunkWidth = 84;
		const trunkX = (this.width - trunkWidth) / 2;
		const baseY = this.height * 0.72;
		const isYoung = this.currentPhase === "young";

		this.pillar.draw(this.ctx, trunkX, baseY, trunkWidth, isYoung);

		// 3. Draw Ground / Khanqah Courtyard Base
		this.drawGround(baseY, trunkX, trunkWidth);

		// 4. Draw Character (Nima in Old or Young phase)
		this.drawNima(baseY, trunkX, trunkWidth, isYoung);

		// 5. Draw Particles
		this.particles.draw(this.ctx);

		this.ctx.restore();
	}

	private drawBackground() {
		// Sky gradient
		const sky = this.ctx.createLinearGradient(0, 0, 0, this.height);
		sky.addColorStop(0, "#040710");
		sky.addColorStop(0.5, "#0b162c");
		sky.addColorStop(1, "#13233a");
		this.ctx.fillStyle = sky;
		this.ctx.fillRect(0, 0, this.width, this.height);

		// Mystical Persian Crescent Moon
		this.ctx.save();
		const moonX = this.width * 0.82;
		const moonY = this.height * 0.15;
		this.ctx.fillStyle = "#fffae6";
		this.ctx.shadowColor = "rgba(255, 245, 200, 0.6)";
		this.ctx.shadowBlur = 18;
		this.ctx.beginPath();
		this.ctx.arc(moonX, moonY, 20, 0, Math.PI * 2);
		this.ctx.fill();

		// Cutout to form crescent
		this.ctx.fillStyle = "#070f1e";
		this.ctx.shadowBlur = 0;
		this.ctx.beginPath();
		this.ctx.arc(moonX + 8, moonY - 4, 17, 0, Math.PI * 2);
		this.ctx.fill();
		this.ctx.restore();

		// Mosque / Dome Silhouettes in background
		this.ctx.fillStyle = "rgba(7, 13, 24, 0.75)";
		this.ctx.beginPath();
		const domeBaseY = this.height * 0.65;
		// Left dome
		this.ctx.arc(this.width * 0.2, domeBaseY, 60, Math.PI, 0);
		// Right dome
		this.ctx.arc(this.width * 0.78, domeBaseY + 10, 50, Math.PI, 0);
		this.ctx.fill();

		// Minaret spires
		this.ctx.fillRect(this.width * 0.08, domeBaseY - 100, 14, 100);
		this.ctx.fillRect(this.width * 0.88, domeBaseY - 80, 12, 80);
	}

	private drawGround(baseY: number, trunkX: number, trunkWidth: number) {
		const groundHeight = this.height - baseY;
		const grad = this.ctx.createLinearGradient(0, baseY, 0, this.height);
		grad.addColorStop(0, "#1a1008");
		grad.addColorStop(0.3, "#100a05");
		grad.addColorStop(1, "#050302");

		this.ctx.fillStyle = grad;
		this.ctx.fillRect(0, baseY, this.width, groundHeight);

		// Decorative Persian Courtyard Stone Tiles
		this.ctx.strokeStyle = "rgba(245, 176, 65, 0.2)";
		this.ctx.lineWidth = 1.5;
		this.ctx.beginPath();
		this.ctx.moveTo(0, baseY);
		this.ctx.lineTo(this.width, baseY);
		this.ctx.stroke();

		// Stone Pedestal at Tree Base
		this.ctx.fillStyle = "#2c1e14";
		this.ctx.fillRect(trunkX - 12, baseY - 12, trunkWidth + 24, 16);
		this.ctx.strokeStyle = "#d4af37";
		this.ctx.strokeRect(trunkX - 12, baseY - 12, trunkWidth + 24, 16);
	}

	private drawNima(
		baseY: number,
		trunkX: number,
		trunkWidth: number,
		isYoung: boolean,
	) {
		const sideOffset = 64;
		const charX =
			this.playerSide === "LEFT"
				? trunkX - sideOffset
				: trunkX + trunkWidth + sideOffset;
		const charY = baseY - 20;
		const dir = this.playerSide === "LEFT" ? 1 : -1;

		this.ctx.save();
		this.ctx.translate(charX, charY);
		this.ctx.scale(dir, 1);

		// 1. Youth Aura (when in Young phase)
		if (isYoung) {
			this.ctx.save();
			this.ctx.shadowColor = "#e74c3c";
			this.ctx.shadowBlur = 25;
			this.ctx.fillStyle = "rgba(231, 76, 60, 0.25)";
			this.ctx.beginPath();
			this.ctx.arc(0, -35, 45, 0, Math.PI * 2);
			this.ctx.fill();
			this.ctx.restore();
		}

		// 2. Character Body / Robe
		this.ctx.fillStyle = isYoung ? "#c0392b" : "#34495e";
		this.ctx.beginPath();
		// Robe trapezoid
		this.ctx.moveTo(-18, 0);
		this.ctx.lineTo(18, 0);
		this.ctx.lineTo(12, -45);
		this.ctx.lineTo(-12, -45);
		this.ctx.closePath();
		this.ctx.fill();

		// Persian Waist Sash
		this.ctx.fillStyle = isYoung ? "#f1c40f" : "#d4af37";
		this.ctx.fillRect(-14, -26, 28, 6);

		// 3. Head & Beard
		// Head circle
		this.ctx.fillStyle = "#f5cd79";
		this.ctx.beginPath();
		this.ctx.arc(0, -56, 14, 0, Math.PI * 2);
		this.ctx.fill();

		if (isYoung) {
			// Young Nima: Trim black beard and athletic hair
			this.ctx.fillStyle = "#1e272e";
			this.ctx.beginPath();
			this.ctx.arc(0, -55, 15, Math.PI * 0.9, Math.PI * 2.1);
			this.ctx.fill();

			// Chin beard
			this.ctx.beginPath();
			this.ctx.moveTo(-6, -46);
			this.ctx.lineTo(6, -46);
			this.ctx.lineTo(0, -38);
			this.ctx.closePath();
			this.ctx.fill();

			// Red Warrior Headband
			this.ctx.fillStyle = "#e74c3c";
			this.ctx.fillRect(-15, -64, 30, 5);
		} else {
			// Old Nima: Long white wisdom beard & Sufi felt hat (Sikke)
			// Sikke (tall felt hat)
			this.ctx.fillStyle = "#95a5a6";
			this.ctx.beginPath();
			this.ctx.moveTo(-10, -66);
			this.ctx.lineTo(10, -66);
			this.ctx.lineTo(7, -84);
			this.ctx.lineTo(-7, -84);
			this.ctx.closePath();
			this.ctx.fill();

			// Long white beard
			this.ctx.fillStyle = "#ecf0f1";
			this.ctx.beginPath();
			this.ctx.moveTo(-9, -50);
			this.ctx.lineTo(9, -50);
			this.ctx.lineTo(4, -30);
			this.ctx.lineTo(0, -24);
			this.ctx.lineTo(-4, -30);
			this.ctx.closePath();
			this.ctx.fill();
		}

		// 4. Arms & Axe (with swing rotation animation)
		const isSwinging = this.swingTimer > 0;
		const swingAngle = isSwinging ? 0.85 : -0.35;

		this.ctx.save();
		this.ctx.translate(6, -38); // Shoulder pivot
		this.ctx.rotate(swingAngle);

		// Axe Handle
		this.ctx.fillStyle = "#795548";
		this.ctx.fillRect(0, -6, 42, 5);

		// Axe Blade (Persian Tabarzin / Crescent Axe)
		this.ctx.fillStyle = isYoung ? "#e74c3c" : "#bdc3c7";
		if (isYoung) {
			this.ctx.shadowColor = "#f39c12";
			this.ctx.shadowBlur = 12;
		}
		this.ctx.beginPath();
		this.ctx.arc(36, -3, 14, -Math.PI / 2, Math.PI / 2, false);
		this.ctx.lineTo(30, -3);
		this.ctx.closePath();
		this.ctx.fill();

		// Golden Inlay on Blade
		this.ctx.fillStyle = "#f1c40f";
		this.ctx.beginPath();
		this.ctx.arc(34, -3, 5, 0, Math.PI * 2);
		this.ctx.fill();

		this.ctx.restore();

		this.ctx.restore();
	}
}
