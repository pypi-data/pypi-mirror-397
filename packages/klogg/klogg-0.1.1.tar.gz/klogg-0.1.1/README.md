klogg

Simple command-line work logger.

klogg is a tiny CLI tool to append and view single-line timestamped work log entries.

Where logs are stored
  By default logs are written to:
    ~/.config/klogg/default.log

Install
  pipx install klogg
  or for development:
    pipx install --editable .

Usage
  klogg <message>      # append a single-line log entry (alias: klogg add)
  klogg add <message>  # append a single-line log entry
  klogg ls [DATE]      # list entries for today or given date (YYYY-MM-DD, MM-DD or DD)

Notes
  - When run with no subcommand, klogg behaves like "ls" and shows today's entries.
  - Date formats supported for the ls command:
      YYYY-MM-DD  (exact date)
      MM-DD       (assumes current year)
      DD          (assumes current month & year)

Examples
  klogg add Fixed the widget that caused crashes
  klogg ls             # show today's entries
  klogg ls 2025-12-15  # show entries for 2025-12-15
  klogg ls 12-15        # show entries for Dec 15 of current year
  klogg ls 15           # show entries for day 15 of current month

License
  MIT
