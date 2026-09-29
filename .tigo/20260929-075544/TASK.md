# Push cleanup branch, add upstream remote, open PR

- STATUS: OPEN
- PRIORITY: 80
- TAGS: git

The chore/repo-cleanup branch (.gitignore, README, Vitest, Biome, anticheat removal, AGENTS.md, CHANGELOG) is local-only. Push it with git push -u origin chore/repo-cleanup, add the friend's original repo as upstream (git remote add upstream <url>), and open a PR against upstream main. Verify CI-less checks manually before opening: npm test, npm run check, npx biome check on changed files.
