# Runegraft

Runegraft is a small Python CLI framework that combines:

Docs at [runegraft.codesft.dev](runegraft.codesft.dev)

- Flask-ish *route patterns* for commands: `@cli.command("install <url:str>")`
- Type-hint driven conversion and validation
- An interactive shell (REPL) with:
  - tab completion (fuzzy)
  - persistent history
  - fish-style autosuggestions
  - built-in commands like `help`, `history`, `clear`, `exit`

## Try it

From the project root:

```bash
python -m runegraft
```

Or run a command directly:

```bash
python -m runegraft install https://example.com/pkg.whl --optional-flag 3
```

Inside the shell, type `help`.
