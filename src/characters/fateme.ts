import { CharacterConfig } from './characterTypes.ts';

export const fatemeCharacter: CharacterConfig = {
  id: 'fateme',
  name: 'fateme',
  persianName: 'فاطمه',
  title: 'چوب‌بر اصیل و کلاسیک (Classic Pure Skill 🪵)',
  description: 'Stylish young lumberjack with black glasses, braces smile, vibrant red-and-black hair, light blue hijab, puffy white sleeves, dark buttoned vest, and sneakers. A pure classic character with no special passive abilities—relying 100% on raw woodchopping speed, reflexes, and skill!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Fateme (کلاسیک)',
      avatarEmoji: '🪓',
      primaryColor: '#26a69a',
      auraColor: 'rgba(38, 166, 154, 0.45)',
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
    name: 'Pure Skill (مهارت خالص چوب‌بری)',
    chargeDurationSeconds: 0,
    activeDurationSeconds: 0,
    description: 'بدون قابلیت ویژه! چالش کلاسیک مهارت خالص چوب‌بری و سرعت عمل برای بازیکنان حرفه‌ای.'
  }
};
