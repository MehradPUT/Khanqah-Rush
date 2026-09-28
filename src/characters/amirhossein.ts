import { CharacterConfig } from './characterTypes.ts';

export const amirhosseinCharacter: CharacterConfig = {
  id: 'amirhossein',
  name: 'amirhossein',
  persianName: 'امیرحسین',
  title: 'Double Points Multiplier (امتیاز دوبل / ۲ برابر ⚡)',
  description: 'Stylish youth with curly hair and blue streetwear tee. His passive 2X multiplier awards double points (+2 score) for every single log chopped!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Amirhossein (امتیاز دوبل)',
      avatarEmoji: '🧢',
      primaryColor: '#2980b9',
      auraColor: 'rgba(41, 128, 185, 0.45)',
      staminaDrainMultiplier: 1.0,
      voice: {
        pitch: 1.1,
        rate: 1.15,
        speechLines: {
          start: [
            'امیرحسین وارد بازی شد! ⚡',
            'هر ضربه، دو برابر امتیاز! 🔥',
            'آماده برای رکورد دوبل! 🚀'
          ],
          chop: [
            'دوبل!',
            'دو تا دو تا! ⚡',
            'ضرب در دو!',
            'امتیاز دوبل! 🪙',
            'بشکن!'
          ],
          streak: [
            'امتیاز داره منفجر میشه! 💥',
            'سرعت دوبل، امتیاز دوبل!',
            'کی به این رکورد می‌رسه؟! ⚡'
          ],
          death: [
            '💀 ای وای، تبر افتاد...',
            '💀 رکورد پرید...'
          ]
        }
      }
    }
  },
  ability: {
    name: 'Double Points Passive (امتیاز ۲ برابر مداوم)',
    chargeDurationSeconds: 1, // Passive, always active
    activeDurationSeconds: 0,
    description: 'Every chop awards +2 points instead of +1, accelerating your score at 2x speed!'
  }
};
