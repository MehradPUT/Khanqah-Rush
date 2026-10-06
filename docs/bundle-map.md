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
- KeyCodes: H = 72, L = 76. Synthetic events are out: the bundle flags
  `e.isTrusted === false` (see honeypot note).

## Score submitter (off ~408077)

`qb()` builds `{data, score, token, cheater, reason, cps, duration,
message}` and XHR-POSTs to `KHANQAH_CONFIG.reportUrl || "/api/setScore"`.
Our server contract matches this shape; signed envelopes ride alongside
(see `public/js/score-report.mjs`, which observes instead of patching).

## Branch spawner (off ~406513)

Round init pushes 11 segment pairs via
`da.push(a?-1:1,a?-2:2)` with `a = 500>=Math.floor(1E3*Math.random()+1)`
(≈50/50). **Not** the 0.55/0.35 rules — the sim crate must be realigned
to these exact rules in the sim-alignment phase; its current goldens
mirror our old TS prototype, not this bundle.

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
