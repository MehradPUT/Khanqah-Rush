# AGENTS.md

## Verification workflow

Always verify and test everything.

## Task Management (Tigo)

Tasks are tracked with [Tigo](https://gitlab.com/CodeWriter21/tigo) in `.tigo/`.
Tasks are proper issues/tickets with well explained descriptions.
Tasks can be referenced in other tasks' description with this syntax: `Task(TASK_ID)`
**Tasks (titles and descriptions) are written in English**, matching the
app's English user-facing strings and docs.
A commit convention is to include a Task-ID if the commit is related to a
specific task and to use `tigo(TASK-ID): ...` messages if a commit is only about
creating or modifying tasks; if it does more, choose the proper prefix.
Tasks should be committed after their creation and they should be closed and committed
in the same commit that completes them.

```bash
# List open tasks (sorted by priority)
tigo -c list

# Show task details
tigo -c show <id>

# Create a task
tigo -c create "Title" --priority 80 --tags "tag1,tag2" --description "Description"

# Close/opens a task
tigo -c close <id>
tigo -c open <id>

# Edit a task
tigo -c edit <id> --priority 90 --status closed

# Search tasks
tigo -c search <query>

# Filter by tag
tigo -c list --tag phase1
```

## Conventions

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`...), one
  logical change per commit.
- [CHANGELOG.md](CHANGELOG.md) follows Keep a Changelog 1.1.0; update
  it in the same commit as the change it describes.
- Docs live in `docs/`; keep them concise and non-duplicative — link to
  the submodules' docs instead of copying them.
- Never commit secrets
- Temp/scratch files go in `tmp/` (gitignored).
- Always make sure the docs stay up to date with the codebase.
- The agent may always consult the user for decisions and ask to add more
  suggested changes to make the more improvement; no matter how little the
  improvement might be.
- Prefer separate commits to one commit jammed with different changes.
