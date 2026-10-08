# Legacy bundle symbol glossary (developers only)

The shipped bundle (`public/js/main.js`, mirrored in `dist/`) stays
minified: readable game code is for developers, never for players.
This file is the key — names below are what to read the minified
identifiers as. Anything marked TBD is unconfirmed; do not rely on it.

## Chop / death pipeline

| Minified | Read as | Role |
| --- | --- | --- |
| `Ca(a, e)` | `chopInput(side, event)` | Key/button chop entry; honeypot `isTrusted` check, then shield → flame → main chop, then per-hero blocks (which run even after `Va()` death) |
| `Va()` | `killPlayer()` | Death processing; Fargol sacrifice and Ahmad shield saves return early (round lives on), otherwise sets `aa=false` and schedules `rb()` |
| `$a(a, c, b)` | `shiftTree(side, visualsOnly?, flag)` | Pair-replenish when odd, then unconditional `da.shift()`; `c` only skips visuals |
| `wa(a, c, b)` | `movePlayer(side, animate?, flag)` | Sets `m`; positions sprites; runs `mb()` when `c` |
| `mb(a)` | `playSwingAnimation()` | Swing visuals only |
| `Ta()` | `frameLoop()` | rAF tick: hero HUD/stamina pins, exhaustion check (`Va()` or Parsa nap) |
| `Fa()` | `renderScore()` | Score display update |
| `Ua()` | `renderFatigueBar()` | Fatigue bar from `(ba-now)/qa` |
| `rb()` | `showResult()` | Delayed (~400 ms) result screen, local board, legacy submit decision |
| `qb()` | `submitScoreLegacy()` | Unsigned legacy score POST (always `recorded:false` on our server) |
| `hb()` / `gb()` | `fetchBoardLegacy()` / `postForm()` | Legacy board GET / form-encoded POST helpers |
| `fb()` | `startRoundFromMenu()` | Space-key round start |
| `pb()` | `initRound()` | Full state reset (counters, timers, `qa/Ga/ca/Ha`, `gameStartTime`) |
| `Ia()` | `showCharacterSelector()` | Character menu setup |
| `nb()` | `levelUp()` | `qa*=.95, Ga*=.95` + banner |
| `Ka(el)` | `hoverElement()` | Cosmetic hover class only |

## Round state

| Minified | Read as | Notes |
| --- | --- | --- |
| `aa` | `alive` | Round-running flag |
| `h` | `inResult` | Result screen showing |
| `Z` | greet/menu flag | Exact polarity TBD; `in_greet` class is `!Z` |
| `m` | `playerSide` | `true` = LEFT; set only via `wa()` (init `false`) |
| `da` | `treeQueue` | Bottom-first segment array (`-1/-2` LEFT, `1/2` RIGHT, `0` none) |
| `ba` | `staminaDeadline` | Timestamp; round init `now+4250` |
| `qa` | `staminaWindow` | Round init `8500`; shrunk by `nb()` |
| `Ga` | `refillStep` | Round init `250`; shrunk by `nb()` |
| `ca` | `score` | `window.score` reads this live (trap-free) |
| `Ha` | `level` | Display only (starts 1) |
| `za` | `fatigueRunning` | Set on first chop; cleared by Parsa nap |
| `pa`, `W` | visual offsets | Cosmetic |
| `l`, `Ba`, `cb` | local board, player name, best score | Legacy board only |
| `R` | share hash | From URL fragment |

## Hero state (all reset in `pb()`)

`selectedCharacter`, `nimaPhase` (`old`/`young`), `isRejuvenated`,
`gameStartTime`, `fargolChops`, `fargolFlameActive`,
`fargolFlameStartTime`, `fargolSacrificeAvailable`,
`fargolSacrificeInProgress`, `aliChops`, `aliFlurryActive`,
`isFlurryChop`, `aliFlurryRemaining`, `aliFlurryTimer`,
`parsaSleepCount`, `parsaSleeping`, `parsaWaitingForChop`,
`parsaSleepStartTime`, `parsaSleepTimer`, `ahmadChops`,
`ahmadShieldCount`, `ahmadShieldActive`.

These names are already readable; the sim mirrors them 1:1
(see `wasm/sim/src/lib.rs`, `shared/sim.js`).

## Honeypot (stays live, decision D3)

`_honeypot_cheated`, `_honeypot_reason`, `_shadow_score`
(`ca ^ 0x5F3759DF`), `_chop_count`, `_game_start_time`,
`_recent_chops`, `_syncShadowScore()`, `_onCheatScoreInput()`,
`generateScoreToken()`. Reads of `window.score`/`window.game.score`/
`window.Lumberjack.getScore()` are side-effect-free; every *write*
path flags the round.

## Companion hooks (`window.khanqahGame`, `window.__rng50`)

Already readable: `getCharacter()`, `isAliFlurryActive()`,
`isParsaSleeping()`, `isFargolSacrificeInProgress()` (surgical patch),
`getTree()`, `getPlayerSide()`, `isAlive()`, `isInResult()`. The
companion gates trace recording on these so both sides agree
per input. `window.__rng50()` / `window.__rngReset()` seed the two
spawn draws (surgical patch).

## Annotated `chopInput` (Ca) flow

```
on input(side):
  honeypot: untrusted event? -> flag (still processes)
  if sacrifice cinematic running: ignore
  if fargol and flame active:
    first-chop grace if needed
    lethal? -> survive (+1, extra shift), stamina full; else normal chop
  if ali and flurry active and not a flurry chop: ignore
  if parsa and sleeping: ignore
  ahmad with shields and lethal: absorb (+1, extra shift), shield--
  first chop? -> stamina = now + 4250
  lethal? -> shatter-if-small, then killPlayer()
      (fargol sacrifice / death; falls through below either way)
  else -> shift once, stamina += refill (cap now+window), score +1
  per-hero progress (runs on lethal chops too):
    fargol (not flaming): counter++, flame at %100
    ali (not flurrying): counter++, flurry at %50
    amirhossein: score +1 again
    erfan: stamina ratio < 0.5 -> score +2
    ahmad: counter++, shield at %100
```

Exhaustion never kills inside `chopInput` — only the frame loop
(`Ta`) calls `killPlayer()` on deadline (Parsa naps instead while
blankets remain).
