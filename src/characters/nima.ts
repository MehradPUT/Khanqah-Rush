import { CharacterConfig } from './characterTypes.ts';

export const nimaCharacter: CharacterConfig = {
  id: 'nima',
  name: 'nima',
  persianName: 'نیما',
  title: 'Master Woodcutter of the Khanqah',
  description: 'A devoted master woodcutter wearing his iconic tricolor shirt. In moments of supreme focus, his youth awakens!',
  phases: {
    old: {
      id: 'old',
      displayName: 'Old Nima (پیر)',
      avatarEmoji: '🧔🏻‍♂️',
      primaryColor: '#7f8c8d',
      auraColor: 'rgba(245, 176, 65, 0.3)',
      staminaDrainMultiplier: 1.0, // Normal drain
      voice: {
        pitch: 0.75, // Deep, raspy elder voice
        rate: 0.92,
        speechLines: {
          start: [
            'یا پیر مدد!',
            'به نام حق، دست به تبر می‌بریم...',
            'هنوز دستم گرمه!'
          ],
          chop: [
            'هو!',
            'یا حق!',
            'یا علی!',
            'ها!'
          ],
          streak: [
            'دست مریزاد!',
            'برکت به این تبر!',
            'آهسته و پیوسته...'
          ],
          death: [
            'آه... نفسم گرفت!',
            'کمرم شکست!',
            'دیگه رمقی نموند...'
          ]
        }
      }
    },
    young: {
      id: 'young',
      displayName: 'Young Nima (جوان)',
      avatarEmoji: '⚡',
      primaryColor: '#e74c3c',
      auraColor: 'rgba(231, 76, 60, 0.7)',
      staminaDrainMultiplier: 0.0, // 0.0 = Never gets tired (Infinite stamina)
      voice: {
        pitch: 1.25, // Energetic, sharp, roaring youth
        rate: 1.2,
        speechLines: {
          start: [
            'بریم که تبر در دست من آتشه!',
            'آماده‌ام!'
          ],
          chop: [
            'های!',
            'هوی!',
            'بشکن!',
            'بزن بریم!'
          ],
          streak: [
            'طوفان به پا کردم!',
            'کی جلودارمه؟!',
            'آتش شدم!'
          ],
          abilityTrigger: [
            'جوانی کجایی که یادت بخیر!',
            'طوفان اومد!',
            'خون جوانی در رگ‌هام جوشید!'
          ],
          abilityRevert: [
            'آخ... دوباره پیر شدم!'
          ],
          death: [
            'نه! غافلگیر شدم!',
            'عجب ضربه‌ای...'
          ]
        }
      }
    }
  },
  ability: {
    name: 'Youth Rejuvenation (اکسیر جوانی)',
    chargeDurationSeconds: 30, // Activates after 30s
    activeDurationSeconds: 5,  // Lasts for 5s
    description: 'After 30s of survival, Nima rejuvenates into his young form for 5s: stamina never drains, chop speed increases, and glowing fire trails surround his axe.'
  }
};
