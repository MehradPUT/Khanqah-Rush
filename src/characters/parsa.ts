import { CharacterConfig } from './characterTypes.ts';

export const parsaCharacter: CharacterConfig = {
  id: 'parsa',
  name: 'parsa',
  persianName: 'پارسا',
  title: 'خواب و پتو (Cozy Blanket Nap 💤)',
  description: 'Stocky lumberjack in a sherpa-lined plaid jacket and glasses. When he dies of tiredness, he wraps in a warm blanket and sleeps to fully restore stamina (works 2 times per game)!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Parsa (پتو و خواب)',
      avatarEmoji: '🛌',
      primaryColor: '#9b59b6',
      auraColor: 'rgba(155, 89, 182, 0.45)',
      staminaDrainMultiplier: 1.0,
      voice: {
        pitch: 1.0,
        rate: 1.0,
        speechLines: {
          start: [],
          chop: [],
          streak: [],
          death: []
        }
      }
    }
  },
  ability: {
    name: 'Blanket Power Nap (تجدید قوا با پتو)',
    chargeDurationSeconds: 0,
    activeDurationSeconds: 1.2,
    description: 'Automatically restores 100% stamina upon timer exhaustion up to 2 times per game.'
  }
};
