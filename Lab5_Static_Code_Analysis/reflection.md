# Lab 5: Reflection

## 1. What each tool found, and what it missed

The three tools barely overlapped on what they were good at.

| Tool | Messages | What it was good at | Found only by this tool |
|------|----------|--------------------|-------------------------|
| Bandit | 6 | Security | MD5 hash, shell command, hardcoded secret, predictable random numbers |
| Pylint | 22 | Code quality and design | Mutable default argument, missing `with`/encoding, redundant `if`/`else`, naming, docstrings |
| Flake8 | 7 | PEP 8 style | The 80-character line (Pylint's limit is 100, so it let it pass) |

Some problems were reported by more than one tool: `eval` (Bandit and Pylint),
the bare `except` (all three), the unused import and variables (Flake8 and
Pylint), and `== None` (Flake8 and Pylint). Fixing that one line therefore
cleared messages in several reports at once.

Two real problems were reported by none of them. `main()` printed the secret
key to the console, and `main()` ran every time the module was imported. I only
found those by running the program and reading its output and code.

## 2. How I prioritised

I started with security, in order of severity: the two High findings (MD5 and
the shell call), then the Medium one (`eval`), then the Low ones. After that
came bugs, then style. I committed the fixes tool by tool, Bandit first, so each
commit has one purpose and can be reviewed on its own. Several fixes overlapped,
so the Flake8 commit had only five issues left to fix out of the original seven.

Severity ratings did not always match real risk. Bandit rated the hardcoded
secret only Low, yet printing that secret on screen was the most direct leak in
the file, and no tool flagged the `print` at all.

## 3. Limits and false alarms

- **Judgement calls.** MD5 was used here to turn a guest ID into an identifier,
  not to store a password. Bandit still rates it High, and its own suggestion is
  to add `usedforsecurity=False`. I switched to SHA-256 instead, because a guest
  identifier is personal data and the change costs nothing. The `random` finding
  for a four-digit booking reference is similar: low risk, but trivial to fix.
- **Side effects.** `base_price` was reported as unused only because `eval` read
  it implicitly. The tools could not see that, and the real problem was the `eval`.
- **A score is not correctness.** 8 of Pylint's 22 messages were missing
  docstrings. Adding them lifted the score a lot without changing how the
  program behaves. The 10.00/10 result says the code follows the rules, not that
  it is right. For example, a tool cannot tell me whether `cancel_booking`
  should report an unknown room, so I had to decide that myself.
- **Fixes can change behaviour.** Replacing MD5 changed the guest hash, and
  hiding the secret changed one line of output. I documented both in `issues.md`.

## 4. How I would use static analysis in future

I would run all three tools before every commit, or in a pre-commit hook, so
problems are fixed while the change is still small. Bandit and Flake8 are cheap
to keep at zero issues, and I would set a Pylint score threshold. I would not
silence findings with `# nosec` or `# pylint: disable` unless I could explain
why the finding is wrong. And I would pair the tools with tests and with
actually running and importing the program, because the two problems the tools
missed here only showed up that way.
