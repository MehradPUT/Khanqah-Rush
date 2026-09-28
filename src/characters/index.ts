export * from './characterTypes.ts';
export * from './nima.ts';
export * from './fargol.ts';
export * from './ali.ts';
export * from './amirhossein.ts';
export * from './parsa.ts';
export * from './ahmad.ts';
export * from './erfan.ts';
export * from './fateme.ts';

import { nimaCharacter } from './nima.ts';
import { fargolCharacter } from './fargol.ts';
import { aliCharacter } from './ali.ts';
import { amirhosseinCharacter } from './amirhossein.ts';
import { parsaCharacter } from './parsa.ts';
import { ahmadCharacter } from './ahmad.ts';
import { erfanCharacter } from './erfan.ts';
import { fatemeCharacter } from './fateme.ts';

export const allCharacters = [
  nimaCharacter,
  fargolCharacter,
  aliCharacter,
  amirhosseinCharacter,
  parsaCharacter,
  ahmadCharacter,
  erfanCharacter,
  fatemeCharacter
];

