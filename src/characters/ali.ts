import type { CharacterConfig } from "./characterTypes.ts";

export const aliCharacter: CharacterConfig = {
	id: "ali",
	name: "ali",
	persianName: "علی",
	title: "10-Log Flurry Burst (رگبار ۱۰ کنده بعد از ۵۰ ضربه 🪓⚡)",
	description:
		"Chief Architect of the Khanqah. After every 50 chops, he unleashes an automatic 10-log flurry combo (+10 score, full stamina refill) that rapidly and safely cleaves through logs!",
	phases: {
		normal: {
			id: "normal",
			displayName: "Ali (تمرکز تبر)",
			avatarEmoji: "👓",
			primaryColor: "#3498db",
			auraColor: "rgba(52, 152, 219, 0.45)",
			staminaDrainMultiplier: 1.0,
			voice: {
				pitch: 1.05,
				rate: 1.15,
				speechLines: {
					start: [
						"تبر آماده رگباره! 🪓",
						"تمرکز برای ۵۰ ضربه! ⚡",
						"شمارش آغاز شد! ✨",
					],
					chop: [
						"یک ضربه نزدیک‌تر!",
						"هدف بعدی! 🎯",
						"ریتم بی‌نقص! 📐",
						"محاسبه شد! ⚡",
						"بزن!",
					],
					streak: ["شمارش به اوج رسید!", "نزدیک رگباریم!", "انرژی پر شد!"],
					abilityTrigger: [
						"🪓⚡ رگبار ۱۰ کنده فعال شد! +10 💥",
						"🔥 طوفان تبر علی! ده کنده در ثانیه! 🔥",
						"⚡ آماده باش، ۱۰ ضربه رگباری! ⚡",
					],
					death: ["💀 ریتم ضربات شکست...", "💀 خطای محاسباتی در شمارش..."],
				},
			},
		},
		flurry: {
			id: "flurry",
			displayName: "Flurry Burst (رگبار خودکار)",
			avatarEmoji: "⚡",
			primaryColor: "#ff9800",
			auraColor: "rgba(255, 152, 0, 0.85)",
			staminaDrainMultiplier: 0.0,
			voice: {
				pitch: 1.2,
				rate: 1.3,
				speechLines: {
					start: ["طوفان ۱۰ کنده! 💥"],
					chop: [
						"یک!",
						"دو!",
						"سه!",
						"چهار!",
						"پنج!",
						"شش!",
						"هفت!",
						"هشت!",
						"نه!",
						"ده!",
					],
					streak: ["رگبار کامل شد! 🔥", "۱۰ کنده روی هوا!"],
					abilityTrigger: ["🪓⚡ رگبار ۱۰ کنده! +10 💥"],
					abilityRevert: [
						"مسیر کاملاً پاکسازی شد! ✨",
						"رگبار با موفقیت نشست! 🪓",
					],
					death: ["💀 رگبار متوقف شد..."],
				},
			},
		},
	},
	ability: {
		name: "10-Log Flurry Burst (رگبار ۱۰ کنده بعد از ۵۰ ضربه)",
		chargeDurationSeconds: 50, // 50 chops
		activeDurationSeconds: 10, // 10 logs auto-chopped
		description:
			"After every 50 chops, Ali automatically executes a rapid 10-log combo (+10 score, full stamina refill) in 0.6 seconds with safe branch clearance!",
	},
};
