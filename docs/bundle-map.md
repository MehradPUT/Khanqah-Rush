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

## Surgical patches (string-level only, mirrored public/ ↔ dist/)

- H/L + A/D keys, seeded `__rng50()` spawns (see git history).
- `window.khanqahGame.isFargolSacrificeInProgress()` (line ~1665):
  exposes the sacrifice cinematic flag so the companion skips inputs
  the bundle ignores. SHA-256 `174C1917…4AE5B` (both copies).

## Hero mechanics (sim contract)

Roster (`ALL_CHARACTERS`, line ~1222): nima, fargol, ali, amirhossein,
parsa, ahmad, erfan, fateme. Per-chop core (line 2632): first chop sets
`ba=now+4250`; lethal branch kills via `Va()`; survived chops do
`ba+=Ga` capped at `now+qa`, `ca++`. Round init sets
`ba=now+4250, qa=8500, Ga=250, ca=0, Ha=1`. Every `ca%20===0` after an
increment fires `nb()`: `qa*=.95, Ga*=.95` (float64 chain — the JS and
Rust sims replicate the exact op order).

- Nima: 20 s cycle from `gameStartTime`, `ba` pinned while pos ≥ 15 s.
- Fargol: chop counter (non-flame chops); `%100===0` starts 5 s flame
  (stamina pinned, lethal branches survive with +1 and a shift).
  Lethal with sacrifice left: survive, 880 ms cinematic (inputs
  ignored), branch cleanup +1 at ~420 ms. Once per round.
- Ali: counter (non-flurry chops); `%50===0` starts 10 auto safe chops
  at 95 ms cadence (stamina pinned, manual inputs ignored). Counter
  never resets (next at 100, 150, …).
- Ahmad: counter; `%100===0` earns a stacking shield. Lethal with a
  shield: survive with +1 and shifts. Exhaustion with a shield: survive
  with cleanup shift +1. Blocked chops don't advance the counter.
- Parsa: exhaustion with < 2 naps: 3 s sleep then wait-for-chop, both
  stamina-pinned (exhaustion check skipped); next chop resumes full.
- Amirhossein: +1 extra per survived chop (2 total).
- Erfan: post-chop stamina ratio `(ba-now)/qa < 0.5` scores +2 extra
  (3 total).
- Fateme: no abilities.
- Lethal on a `|bottom|===1` branch shifts the queue (shatter `$a`);
  post-death queue state is unobservable except via survival saves.
- Death only via the rAF loop (`Va()` on deadline, chop-time checks
  excluded) or branch chops; the 400 ms `setTimeout(rb,400)` delays
  `in_result`.

## Stamina and Nima rejuvenation (sim-critical)

Stamina is a deadline timestamp (`ba`): first chop sets `now + 4250 ms`,
each survived chop adds 250 ms capped at `now + 8500 ms`; passing the
deadline without chopping ends the round. Nima's cycle runs on a 20 s
period: while the cycle position sits at >= 15 s, `ba` is pinned to
`now + qa` (full window) every frame, so a round alive at 15 s carries
through to ~28.5 s even idle. Other heroes' abilities (fargol flame,
ali flurry, ahmad shield, parsa sacrifice) interact with the`|x| === 1`
shatter path and are not yet modeled in the sim.
