# Legacy bundle map (`public/js/main.js`)

Reverse-engineered landmarks for surgical work. The bundle is Browserify +
PIXI output (~494 KB); **never reformat it** — string-level edits only,
mirrored byte-identically into `dist/js/main.js`.

Conventions: `off:` = byte offset, `line:` = 1-based line in the committed
file. All offsets verified against SHA-256
`see commit messages` (recorded per patch commit).

## Game keyboard handler (off 492599, line 2768)

```js
N(M,"keydown",function(a){a.preventDefault();a=a.which||a.keyCode;aa?(37==a&&(Ka(La),Ca(!0)),39==a&&(Ka(jb),Ca(!1))):(37==a?rotateCharacter(-1):(39==a?rotateCharacter(1):(Z&&!h||32!=a||(Ka(La),fb()))))});
```

- `aa` truthy = PLAYING branch (`Ca(!0)`/`Ca(!1)` = chop left/right).
  Falsy = menu branch (carousel rotate, Space starts).
- Play-branch targets (each occurs exactly once):
  `37==a&&(Ka(La),Ca(!0))` and `39==a&&(Ka(jb),Ca(!1))`.
- H/L patch: parenthesize — `(37==a||72==a)&&(…)` — a bare
  `37==a||72==a&&(...)` would short-circuit past the action.
  Menu ternaries take the keys bare (`(37==a||72==a)?…` — no trap there).
- Menu-branch targets (each occurs exactly once):
  `37==a?rotateCharacter(-1)` and `39==a?rotateCharacter(1)`.
- KeyCodes: arrows 37/39, A = 65, D = 68, H = 72, L = 76 (A/D were
  documented in the README but never wired — fixed by the same patches).
  Synthetic events are out: the bundle flags `e.isTrusted === false`
  (see honeypot note).

## Score submitter (off ~408077)

`qb()` builds `{data, score, token, cheater, reason, cps, duration,
message}` and XHR-POSTs to `KHANQAH_CONFIG.reportUrl || "/api/setScore"`.
Our server contract matches this shape; signed envelopes ride alongside
(see `public/js/score-report.mjs`, which observes instead of patching).

## Branch spawner (off ~406513, init) and chop refill (off ~390100)

Init: `da=[0,0]`, then `for(...;11>da.length;)` pushes pairs
(queue settles at even length 12).
Patched: both spawn draws now call `window.__rng50()` (from
`public/js/seeded-rng.js`, loaded before the bundle) instead of inline
`Math.random()` — one seeded draw per pair, stream-identical to the sim.
Unseeded opens fall back to legacy behavior (local-only play).
`(a?-1:1, a?-2:2)` with `a = 500>=Math.floor(1E3*Math.random()+1)` —
a single 50/50 draw per pair. Entries encode side AND magnitude:
`-1/-2` = LEFT, `1/2` = RIGHT, `0` = none. Magnitude matters:
collision code treats `|x|===1` (shatterable) and `|x|===2`
differently, with per-character ability interactions (fargol flame,
ali flurry, ahmad shield, parsa sacrifice).
Chop (`$a`, off ~390100): if `da.length` is odd, push a fresh pair;
`shift()` one entry per chop.

## Honeypot (off ~379502, DECISION D3: stays live)

`ANTI-CHEAT HONEYPOT SENSORS & CONSOLE BAIT` block (`window.score`
getter/setter traps, shadow-score XOR, `FLAGGED_` tokens,
`untrusted_event`). Left untouched by decision: harmless under server
authority, zero bundle risk. Note `window.score` *reads* are trap-free —
the companion reporter relies on that.

## Game-over observability

`ma(T,"in_result",h)` toggles the `in_result` class on `#page_wrap`
(`h` truthy = round over). The companion reporter watches this plus
`window.score`; no bundle hooks required.
