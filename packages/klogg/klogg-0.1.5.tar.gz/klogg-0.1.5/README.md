klogg — simple command line work logger
======================================

klogg is a small command-line tool for keeping simple timestamped work logs. It's designed to be minimal and friction-free: append entries with a single command and view per-day or per-month summaries including durations.

Project
-------
- Name: klogg

- Author: Predrag Mandic <predrag@nul.one>
- License: MIT

Installation
------------
From the project root you can install locally:

- Editable install (for development):
  pip install -e .

- Or build and install:
  pip install .

klogg exposes a console script named `klogg` (entry point: klogg.cli:main).

Log files and layout
--------------------
- Default log directory: /home/peja/.config/klogg
- Monthly log files are named YYYY-MM.log (for example: /home/peja/.config/klogg/2025-12.log).
- There is also legacy support for `default.log`.

Log line format
---------------
Each log line is written with a timestamp and the message:

YYYY-MM-DD HH:MM:SS>  <message>

Example:
2025-12-15 11:15:00>  Fixed the widget

Special markers
---------------
- <start> — marks the start of a session (the line itself is not shown in summaries; it acts as a starting timestamp for the next entry).
- <break> — marks a short break. Break entries are excluded from total time calculations.

Commands
--------
When you run `klogg` without a subcommand it behaves like `klogg day` and shows today's entries.

Common commands:

- klogg --help
  Show usage and available commands and options.

- klogg --version
  Print the installed klogg version.

- klogg add <message> (alias: klogg a <message>)
  Append a timestamped log line with the given message.
  Example:
    klogg add Fixed the widget

- klogg break [message] (aliases: b, p)
  Append a break entry. If you pass a message it becomes: "<break> <message>"
  Example:
    klogg break grabbed coffee

- klogg start (alias: s)
  Append the literal "<start>" marker.

- klogg ls [WHEN]
  Print raw log lines for a month.
  WHEN formats accepted:
    - YYYY-MM (exact month)
    - MM     (assumes current year)
  If omitted, shows the current month's raw lines.

- klogg day [WHEN] (alias: d)
  Show parsed entries for a day with durations and totals.
  WHEN accepted:
    - YYYY-MM-DD
    - MM-DD    (assumes current year)
    - DD       (assumes current month & year)
  Output format:
    YYYY-MM-DD HH:MM:SS [HH:MM]>  MARKER_AND_DESCRIPTION
  The total excludes entries that begin with "<break>".

- klogg month [WHEN] (alias: m)
  Show parsed entries for a month and a total.
  WHEN accepted:
    - YYYY-MM
    - MM (assumes current year)

- klogg rm
  Remove the last log entry from the most recent log file. The command prints the last entry and asks for confirmation before deleting.

Behavior notes
--------------
- Each appended entry uses the current timestamp as the "end time" for the task. Durations are computed as the difference between an entry's timestamp and the previous entry's timestamp.
- The "<start>" line is not printed in day/month summaries; it only sets the "previous timestamp" for the next entry.
- Breaks ("<break>") are printed but excluded from the totals.

Development notes
-----------------
- Python: requires >=3.8
- Dependencies:
  - click >= 8.0
  - click-aliases >= 1.0

Relevant files
--------------
- CLI implementation: src/klogg/cli.py
- Package metadata: pyproject.toml

License
-------
MIT

Contributing
------------
Bug reports and pull requests are welcome. Keep changes small and focused.
