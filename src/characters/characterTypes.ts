export type CharacterPhase = 'old' | 'young' | 'normal' | 'flame' | string;

export interface VoicePreset {
  pitch: number;
  rate: number;
  speechLines: {
    start: string[];
    chop: string[];
    streak: string[];
    abilityTrigger?: string[];
    abilityRevert?: string[];
    death: string[];
  };
}

export interface CharacterPhaseConfig {
  id: string;
  displayName: string;
  avatarEmoji: string;
  primaryColor: string;
  auraColor: string;
  staminaDrainMultiplier: number; // 1.0 for normal, 0.0 for infinite stamina
  voice: VoicePreset;
}

export interface CharacterConfig {
  id: string;
  name: string;
  persianName: string;
  title: string;
  description: string;
  phases: Record<string, CharacterPhaseConfig>;
  ability: {
    name: string;
    chargeDurationSeconds: number; // seconds or chops
    activeDurationSeconds: number; // 5 seconds
    description: string;
  };
}

