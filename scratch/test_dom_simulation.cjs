// Simulation test for Carousel DOM events & Mobile Touch
const fs = require('fs');

// Create mock DOM environment
const elements = {};

function createElement(tag) {
  return {
    tagName: tag.toUpperCase(),
    children: [],
    style: {},
    className: '',
    innerText: '',
    innerHTML: '',
    attributes: {},
    listeners: {},
    hasChildNodes: function() { return this.children.length > 0; },
    appendChild: function(child) { this.children.push(child); },
    setAttribute: function(k, v) { this.attributes[k] = v; },
    getAttribute: function(k) { return this.attributes[k]; },
    addEventListener: function(evt, handler) {
      this.listeners[evt] = this.listeners[evt] || [];
      this.listeners[evt].push(handler);
      this['on' + evt] = handler;
    },
    dispatchEvent: function(evtType, evtObj = {}) {
      if (this.listeners[evtType]) {
        this.listeners[evtType].forEach(fn => fn(evtObj));
      } else if (this['on' + evtType]) {
        this['on' + evtType](evtObj);
      }
    },
    classList: {
      add: function(c) {},
      remove: function(c) {}
    }
  };
}

elements['btn_char_prev'] = createElement('button');
elements['btn_char_next'] = createElement('button');
elements['char_carousel_card'] = createElement('div');
elements['char_carousel_dots'] = createElement('div');
elements['char_card_avatar'] = createElement('span');
elements['char_card_name'] = createElement('span');
elements['char_card_badge'] = createElement('span');
elements['char_card_desc'] = createElement('div');

const mockLocalStorage = {
  store: {},
  getItem: function(k) { return this.store[k] || null; },
  setItem: function(k, v) { this.store[k] = String(v); }
};

global.document = {
  getElementById: function(id) { return elements[id] || null; },
  createElement: createElement,
  querySelectorAll: function(sel) {
    if (sel === '.char-carousel-dot') return elements['char_carousel_dots'].children;
    return [];
  }
};
global.localStorage = mockLocalStorage;
global.window = {
  Telegram: { WebApp: { HapticFeedback: { impactOccurred: function() {} } } }
};
global.triggerTelegramHaptic = function() {};
global.selectedCharacter = 'nima';

// Load code
const mainJs = fs.readFileSync('public/js/main.js', 'utf-8');

// Extract ALL_CHARACTERS, updateCarouselCard, selectCharacter, rotateCharacter, initCharacterSelector
const funcCode = mainJs.slice(
  mainJs.indexOf('var ALL_CHARACTERS = ['),
  mainJs.indexOf('window.khanqahGame = {')
);

// Execute in this context
eval(funcCode);

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function runTests() {
  console.log('Testing Carousel Initialization...');
  initCharacterSelector();

  console.log('Initial character:', selectedCharacter);
  if (elements['char_carousel_dots'].children.length !== 8) {
    console.error(`FAIL: Expected 8 dots, got ${elements['char_carousel_dots'].children.length}`);
    process.exit(1);
  }
  console.log('PASS: 8 indicator dots successfully built');

  // Test 1: Next button via mobile touchstart
  console.log('\nTesting Next Button via touchstart (mobile tap)...');
  await sleep(300);
  elements['btn_char_next'].dispatchEvent('touchstart', { stopPropagation: () => {}, preventDefault: () => {}, cancelable: true });
  console.log('Character after Next touchstart:', selectedCharacter);
  if (selectedCharacter !== 'fargol') {
    console.error(`FAIL: Expected fargol, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Selected character rotated to Fargol via mobile touchstart');
  console.log('Avatar text:', elements['char_card_avatar'].innerText);
  console.log('Name text:', elements['char_card_name'].innerText);
  console.log('Desc text:', elements['char_card_desc'].innerText);

  // Test 2: Next button via click (desktop or synthetic)
  console.log('\nTesting Next Button via click (desktop click)...');
  await sleep(300);
  elements['btn_char_next'].dispatchEvent('click', { stopPropagation: () => {}, preventDefault: () => {} });
  console.log('Character after 2nd Next (click):', selectedCharacter);
  if (selectedCharacter !== 'ali') {
    console.error(`FAIL: Expected ali, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Selected character rotated to Ali via click');

  // Test 3: Prev button via mobile touchstart
  console.log('\nTesting Prev Button via touchstart...');
  await sleep(300);
  elements['btn_char_prev'].dispatchEvent('touchstart', { stopPropagation: () => {}, preventDefault: () => {}, cancelable: true });
  console.log('Character after Prev:', selectedCharacter);
  if (selectedCharacter !== 'fargol') {
    console.error(`FAIL: Expected fargol, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Selected character rotated back to Fargol');

  // Test 4: Card mobile clean tap (touchstart + touchend with dx=0, dy=0)
  console.log('\nTesting Card clean tap on mobile (advance forward)...');
  await sleep(300);
  elements['char_carousel_card'].dispatchEvent('touchstart', {
    touches: [{ clientX: 100, clientY: 100 }],
    stopPropagation: () => {}
  });
  await sleep(50);
  elements['char_carousel_card'].dispatchEvent('touchend', {
    changedTouches: [{ clientX: 102, clientY: 101 }],
    stopPropagation: () => {},
    preventDefault: () => {},
    cancelable: true
  });
  console.log('Character after Card tap:', selectedCharacter);
  if (selectedCharacter !== 'ali') {
    console.error(`FAIL: Expected ali, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Card clean mobile tap rotated forward to Ali');

  // Test 5: Card mobile horizontal swipe left (advance next)
  console.log('\nTesting Card swipe left on mobile (dx = -50px)...');
  await sleep(300);
  elements['char_carousel_card'].dispatchEvent('touchstart', {
    touches: [{ clientX: 150, clientY: 100 }],
    stopPropagation: () => {}
  });
  await sleep(50);
  elements['char_carousel_card'].dispatchEvent('touchend', {
    changedTouches: [{ clientX: 90, clientY: 102 }],
    stopPropagation: () => {},
    preventDefault: () => {},
    cancelable: true
  });
  console.log('Character after swipe left:', selectedCharacter);
  if (selectedCharacter !== 'amirhossein') {
    console.error(`FAIL: Expected amirhossein, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Card swipe left rotated to Amirhossein');

  // Test 6: Card mobile horizontal swipe right (rotate prev)
  console.log('\nTesting Card swipe right on mobile (dx = +50px)...');
  await sleep(300);
  elements['char_carousel_card'].dispatchEvent('touchstart', {
    touches: [{ clientX: 100, clientY: 100 }],
    stopPropagation: () => {}
  });
  await sleep(50);
  elements['char_carousel_card'].dispatchEvent('touchend', {
    changedTouches: [{ clientX: 160, clientY: 101 }],
    stopPropagation: () => {},
    preventDefault: () => {},
    cancelable: true
  });
  console.log('Character after swipe right:', selectedCharacter);
  if (selectedCharacter !== 'ali') {
    console.error(`FAIL: Expected ali, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Card swipe right rotated back to Ali');

  // Test 7: Dot 7 tap (Fateme) via mobile touchstart
  console.log('\nTesting Dot 7 tap (Fateme) via touchstart...');
  await sleep(300);
  elements['char_carousel_dots'].children[7].dispatchEvent('touchstart', {
    stopPropagation: () => {},
    preventDefault: () => {},
    cancelable: true
  });
  console.log('Character after Dot tap:', selectedCharacter);
  if (selectedCharacter !== 'fateme') {
    console.error(`FAIL: Expected fateme, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Directly jumped to Fateme via indicator dot touchstart');
  console.log('Fateme Avatar:', elements['char_card_avatar'].innerText);
  console.log('Fateme Name:', elements['char_card_name'].innerText);
  console.log('Fateme Badge:', elements['char_card_badge'].innerText);
  console.log('Fateme Desc:', elements['char_card_desc'].innerText);

  // Test 8: LocalStorage persistence
  if (mockLocalStorage.getItem('khanqah_character') !== 'fateme') {
    console.error('FAIL: localStorage did not persist fateme');
    process.exit(1);
  }
  console.log('PASS: LocalStorage correctly saved "fateme"');

  // Test 9: Loop back around from Fateme to Nima
  console.log('\nTesting Next from Fateme (carousel loop test)...');
  await sleep(300);
  elements['btn_char_next'].dispatchEvent('touchstart', { stopPropagation: () => {}, preventDefault: () => {}, cancelable: true });
  console.log('Character after Next from Fateme:', selectedCharacter);
  if (selectedCharacter !== 'nima') {
    console.error(`FAIL: Expected nima, got ${selectedCharacter}`);
    process.exit(1);
  }
  console.log('PASS: Carousel correctly looped back from Fateme (8) to Nima (1)');

  console.log('\nALL 8-HERO CAROUSEL MOBILE TOUCH & DESKTOP INTERACTIONS VERIFIED 100% WORKING!');
}

runTests().catch(err => {
  console.error(err);
  process.exit(1);
});
