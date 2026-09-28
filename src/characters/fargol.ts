import { CharacterConfig } from './characterTypes.ts';

export const fargolCharacter: CharacterConfig = {
  id: 'fargol',
  name: 'fargol',
  persianName: 'فرگل',
  title: 'Sultan of the Khanqah (سلطان)',
  description: 'The crowned Sultan of the realm. Every 100 chops ignites her invincible flame form, and a loyal ally sacrifices themselves to grant her a second life!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Fargol (سلطان)',
      avatarEmoji: '👑',
      primaryColor: '#8ec5ad',
      auraColor: 'rgba(142, 197, 173, 0.4)',
      staminaDrainMultiplier: 1.0,
      voice: {
        pitch: 1.3,
        rate: 1.1,
        speechLines: {
          start: [
            'به نام سلطان! 👑',
            'تبر در دستان من است!',
            'آماده فتح درخشانم!'
          ],
          chop: [
            'یا حق!',
            'کنار برو! 🗡️',
            'بشکن! 💥',
            'به فرمان من! 👑'
          ],
          streak: [
            'قدرت سلطان را ببینید!',
            'عالیه!',
            'بی‌نظیره!'
          ],
          death: [
            '💀 تخت سلطنت شکست...',
            '💀 ضربه نامردی بود...'
          ]
        }
      }
    },
    flame: {
      id: 'flame',
      displayName: 'Flaming Sultan (شعله‌ور)',
      avatarEmoji: '🔥',
      primaryColor: '#ff3d00',
      auraColor: 'rgba(255, 61, 0, 0.8)',
      staminaDrainMultiplier: 0.0, // Invincible, stamina locked
      voice: {
        pitch: 1.35,
        rate: 1.25,
        speechLines: {
          start: [
            'شعله‌ور شدم! 🔥'
          ],
          chop: [
            'بسوز و بشکن! 🔥',
            'آتش سلطان! 💥',
            'کی جلودار منه؟! 👑',
            'بزن بریم! ⚡'
          ],
          streak: [
            'طوفان آتش به پا شد!',
            'خاکستر شدی!'
          ],
          abilityTrigger: [
            '🔥 آتش سلطان به پا شد! 🔥',
            '👑 شکست‌ناپذیر شدم! 👑',
            '💥 خشم سلطنتی! 💥'
          ],
          abilityRevert: [
            'شعله‌ها فروکش کرد...'
          ],
          death: [
            '💀 شعله خاموش شد...'
          ]
        }
      }
    }
  },
  ability: {
    name: 'Sultan Flame & Royal Protection (آتش سلطان و فداکاری پارسا)',
    chargeDurationSeconds: 100, // Triggered every 100 chops
    activeDurationSeconds: 5,   // 5s of invincible flame
    description: 'Chop 100 logs to unleash Invincible Flame for 5s. If struck by a lethal branch, Parsa leaps in to sacrifice himself and grant her a second life!'
  }
};
