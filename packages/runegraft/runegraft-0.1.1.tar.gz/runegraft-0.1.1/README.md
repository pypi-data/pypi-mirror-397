# Runegraft

Runegraft is a small Python CLI framework that combines:

Docs at [https://runegraft.codesft.dev](https://runegraft.codesft.dev)

- Flask-ish *route patterns* for commands: `@cli.command("install <url:str>")`
- Type-hint driven conversion and validation
- An interactive shell (REPL) with:
  - tab completion (fuzzy)
  - persistent history
  - fish-style autosuggestions
  - built-in commands like `help`, `history`, `clear`, `exit`