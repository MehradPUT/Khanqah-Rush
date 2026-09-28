import { CharacterConfig } from './characterTypes.ts';

export const ahmadCharacter: CharacterConfig = {
  id: 'ahmad',
  name: 'ahmad',
  persianName: 'احمد',
  title: 'سپر پولادین پشته‌ای (Stacking Steel Shield 🛡️)',
  description: 'Strong lumberjack with a dark beard and taupe sweatshirt. After every 100 chops, he gains a stackable steel shield (e.g. 200 chops = 2 shields) that completely protects him from lethal obstacles or fatigue death!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Ahmad (سپر پولادین)',
      avatarEmoji: '🛡️',
      primaryColor: '#2980b9',
      auraColor: 'rgba(41, 128, 185, 0.45)',
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
    name: 'Stacking Steel Shield (سپر محافظ پشته‌ای ۱۰۰ ضربه)',
    chargeDurationSeconds: 0,
    activeDurationSeconds: 0,
    description: 'Every 100 chops grants a protective shield that stacks indefinitely (e.g. 200 chops = 2 shields, 300 chops = 3 shields). Each shield absorbs 1 lethal collision or fatigue exhaustion.'
  }
};
