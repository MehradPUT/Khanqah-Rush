import { CharacterConfig } from './characterTypes.ts';

export const erfanCharacter: CharacterConfig = {
  id: 'erfan',
  name: 'erfan',
  persianName: 'عرفان',
  title: 'امتیاز ۳ برابر بحرانی (Triple Score Clutch ⚡)',
  description: 'Handsome lumberjack in a blue geometric diamond shirt and jeans. When his stamina/tiredness drops below 50%, he enters an adrenaline rush and his score is TRIPLED (+3 points per chop)!',
  phases: {
    normal: {
      id: 'normal',
      displayName: 'Erfan (امتیاز ۳ برابر)',
      avatarEmoji: '⚡',
      primaryColor: '#2b5c8f',
      auraColor: 'rgba(43, 92, 143, 0.45)',
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
    name: 'Adrenaline Clutch 3X (امتیاز ۳ برابر زیر ۵۰٪ خستگی)',
    chargeDurationSeconds: 1,
    activeDurationSeconds: 0,
    description: 'When tiredness/fatigue drops below 50% (less than half time remaining on the bar), every chop awards 3X score (+3 points)!'
  }
};
