# Fix remaining whole-repo Biome diffs

- STATUS: CLOSED
- PRIORITY: 60
- TAGS: dx, lint

npx biome check . still fails on pre-existing files (e.g. tsconfig.json spacing vs the tab-indent config); only newly added files are clean. Work through the remaining diagnostics incrementally (biome check --write on safe paths, manual fixes where formatting changes semantics), keeping each fix in its own small commit so the diff stays reviewable. Goal: npm run lint passes on the whole repo.
