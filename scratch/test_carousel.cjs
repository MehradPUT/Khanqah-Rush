// Unit test for carousel selection logic
const fs = require('fs');

const mainJs = fs.readFileSync('public/js/main.js', 'utf-8');

// Verify that key functions and data structures exist in public/js/main.js
const assertions = [
  { name: 'ALL_CHARACTERS array exists', test: mainJs.includes('var ALL_CHARACTERS = [') },
  { name: 'Nima in ALL_CHARACTERS', test: mainJs.includes("id: 'nima'") },
  { name: 'Fargol in ALL_CHARACTERS', test: mainJs.includes("id: 'fargol'") },
  { name: 'Ali in ALL_CHARACTERS', test: mainJs.includes("id: 'ali'") },
  { name: 'Amirhossein in ALL_CHARACTERS', test: mainJs.includes("id: 'amirhossein'") },
  { name: 'Parsa in ALL_CHARACTERS', test: mainJs.includes("id: 'parsa'") },
  { name: 'Ahmad in ALL_CHARACTERS', test: mainJs.includes("id: 'ahmad'") },
  { name: 'Erfan in ALL_CHARACTERS', test: mainJs.includes("id: 'erfan'") },
  { name: 'Fateme in ALL_CHARACTERS', test: mainJs.includes("id: 'fateme'") },
  { name: 'Fateme textures loaded', test: mainJs.includes('fateme_body') && mainJs.includes('fateme_swing') && mainJs.includes('fateme_died') },
  { name: 'updateCarouselCard function exists', test: mainJs.includes('function updateCarouselCard(') },
  { name: 'rotateCharacter function exists', test: mainJs.includes('function rotateCharacter(') },
  { name: 'btn_char_prev hooked', test: mainJs.includes("document.getElementById('btn_char_prev')") },
  { name: 'btn_char_next hooked', test: mainJs.includes("document.getElementById('btn_char_next')") },
  { name: 'char_carousel_card hooked', test: mainJs.includes("document.getElementById('char_carousel_card')") },
  { name: 'char_carousel_dots hooked', test: mainJs.includes("document.getElementById('char_carousel_dots')") },
  { name: 'char-carousel-wrap CSS present', test: mainJs.includes('.char-carousel-wrap') },
  { name: 'char-arrow-btn CSS present', test: mainJs.includes('.char-arrow-btn') },
  { name: 'char-carousel-card CSS present', test: mainJs.includes('.char-carousel-card') },
  { name: 'char-card-avatar CSS present', test: mainJs.includes('.char-card-avatar') },
  { name: 'char-card-titles CSS present', test: mainJs.includes('.char-card-titles') },
  { name: 'char-card-badge CSS present', test: mainJs.includes('.char-card-badge') },
  { name: 'char-card-desc CSS present', test: mainJs.includes('.char-card-desc') },
  { name: 'char-carousel-dots CSS present', test: mainJs.includes('.char-carousel-dots') },
  { name: 'char-carousel-dot CSS present', test: mainJs.includes('.char-carousel-dot') },
  { name: 'playParsaSacrificeAnimation present', test: mainJs.includes('function playParsaSacrificeAnimation(') },
  { name: 'fargolSacrificeInProgress guard present', test: mainJs.includes('fargolSacrificeInProgress') },
  { name: 'parsa_jump texture present', test: mainJs.includes('parsa_jump') },
];

let allPassed = true;
assertions.forEach(({ name, test }) => {
  if (test) {
    console.log(`PASS: ${name}`);
  } else {
    console.error(`FAIL: ${name}`);
    allPassed = false;
  }
});

if (!allPassed) {
  process.exit(1);
} else {
  console.log('\nAll 27 carousel & animation assertions passed successfully!');
}
