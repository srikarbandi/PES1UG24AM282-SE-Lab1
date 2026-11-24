# Lab 5: Issues Found and Fixed

File analysed: `hotel_booking_system.py`
Tools: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.5.0 (Python 3.13)

Line numbers below refer to the **original** file, as analysed in
`reports/before/`. The reports after the fixes are in `reports/after/`.

## Summary

| Tool | Before | After |
|------|--------|-------|
| Pylint | 22 messages, score **5.32/10** | 0 messages, score **10.00/10** |
| Flake8 | 7 issues | 0 issues (empty report) |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low) | 0 issues |

The 35 tool messages come down to 18 distinct problems. 16 were found by the
tools and 2 (rows 5 and 9) were found by reading the code and the program output.

## Issue table

Security issues first (High, then Medium, then Low), then bugs, then quality
and style.

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | Weak MD5 hash | Security (High) | 47 | `hashlib.md5` is used to hash the guest ID. MD5 is broken and collision-prone. Bandit B324. | Replaced with `hashlib.sha256`. The digest is now 64 hex characters instead of 32. |
| 2 | Shell command built from input | Security (High) | 58 | `os.system("echo ... " + filename)` starts a shell, so a filename such as `x; rm -rf ~` would be executed. Bandit B605. | Removed the shell call. The message is printed with `print()`, with the same output. |
| 3 | `eval()` on a caller-supplied string | Security (Medium) | 42 | `eval(rate_expr)` runs arbitrary Python, for example `__import__('os').system(...)`. Bandit B307, Pylint W0123. | Replaced with an `ast`-based evaluator that allows only numbers, `base_price` and `+ - * /`. Anything else raises `ValueError`. Tested with injection strings; all were rejected. |
| 4 | Hardcoded secret key | Security (Low) | 62 | The admin token is a string literal in the source code. Bandit B105. | Read from the `HOTEL_SECRET_KEY` environment variable instead. |
| 5 | Secret printed to the console | Security (not flagged) | 70 | `main()` prints the secret key, so it ends up in terminal output and logs. No tool reports this. | Prints only whether a key is configured (`True` or `False`). |
| 6 | Predictable random numbers | Security (Low) | 51 | `random.randint` is not suitable for values that should be hard to guess. Bandit B311. | Use `secrets.randbelow(9000) + 1000`, giving the same 1000 to 9999 range. |
| 7 | Bare `except` with `pass` | Bug / Security (Low) | 24-27 | Catches every exception, including `KeyboardInterrupt`, and silently ignores it. An unknown room number fails without any signal. Bandit B110, Flake8 E722, Pylint W0702. | Look the room up with `.get()`. `cancel_booking` returns `False` for an unknown room and `True` otherwise. |
| 8 | Mutable default argument | Bug | 15, 19 | `booking_log=[]` is created once and shared by every call. Pylint W0102. | Default changed to `None`, with a new list created inside the function on each call. |
| 9 | `main()` runs on import | Bug (not flagged) | 73 | `main()` is called at module level, so importing the module books a room, writes `hotel_ledger.txt` and prints. This breaks any test that imports it. | Wrapped in `if __name__ == "__main__":`. |
| 10 | File handling | Bug / Quality | 55-57 | `open()` and `close()` with no `with`, so the file leaks if `write` fails, and no encoding is given. Pylint R1732, W1514. | `with open(filename, "w", encoding="utf-8")`. |
| 11 | Unused import | Style | 6 | `import math` is never used. Flake8 F401, Pylint W0611. | Removed. |
| 12 | Unused local variables | Quality | 31, 41 | `cleaning_deposit` is dead code. `base_price` was read only implicitly by `eval`. Flake8 F841, Pylint W0612 (two each). | Removed `cleaning_deposit`. `base_price` is now passed to the evaluator explicitly. |
| 13 | Comparison to `None` with `==` | Style | 32 | Flake8 E711, Pylint C0121. | Changed to an identity check (`is None`, and `is not None` after the row 14 simplification). |
| 14 | Redundant `if`/`else` returning booleans | Quality | 34-37 | Pylint R1703, R1705. | `check_room_status` now returns `room is not None and not room["is_booked"]`. |
| 15 | Function not in snake_case | Style | 15 | `bookRoom`. Pylint C0103. | Renamed to `book_room` and updated the call in `main()`. |
| 16 | `%` formatting and an over-long line | Style | 19 | The line is 80 characters, over the 79 limit. Flake8 E501, Pylint C0209. | Wrapped over two lines in the Flake8 commit, then rewritten as a one-line f-string in the Pylint commit. |
| 17 | Missing docstrings | Quality | 15, 23, 30, 40, 46, 50, 54, 61 | Eight functions have no docstring. Pylint C0116 (8 messages). | Added a docstring to every function, including the new evaluator. |
| 18 | No newline at end of file | Style | 73 | Flake8 W292, Pylint C0304. | Newline added. |

## Behaviour changes

The program does the same job after the fixes. Running it gives the same output
except for two lines, and these differences are deliberate:

- `Guest Hash` is now a SHA-256 digest (row 1).
- `Secret key active:` prints `False`, or `True` once `HOTEL_SECRET_KEY` is set, instead of the key itself (rows 4 and 5).

`Booking Reference` is still a random four-digit number on every run. It now
comes from `secrets` instead of `random` (row 6).

Other notes:

- The booking log in `book_room` is only recorded when the caller passes a list in.
  The original shared list was never read by anything, so nothing is lost (row 8).
- `cancel_booking` now returns `False` for an unknown room, where it used to do nothing.
  `main()` ignores the return value, so the program's behaviour is unchanged (row 7).

## Where the fixes are

| Commit | What it fixes |
|--------|---------------|
| Fix all Bandit findings | rows 1 to 7 |
| Fix all Flake8 findings | rows 11, 12 (`cleaning_deposit`), 13, 16 (line length), 18 |
| Fix Pylint findings | rows 8 to 10, 14, 15, 16 (f-string), 17 |
