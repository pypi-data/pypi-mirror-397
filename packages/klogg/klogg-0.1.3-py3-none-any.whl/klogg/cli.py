import os
import re
import sys
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

import click
from click_aliases import ClickAliasedGroup

LOG_PATH = os.path.expanduser("~/.config/klogg/default.log")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def ensure_log_path() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def append_log(message: str) -> str:
    """
    Append a timestamped line to the log and return the written line
    (without the trailing newline).
    """
    ensure_log_path()
    timestamp = datetime.now().strftime(TIME_FORMAT)
    line = f"{timestamp}>  {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    return line.rstrip("\n")


def parse_date_arg(arg: str) -> date:
    """
    Parse arg as one of:
      - YYYY-MM-DD
      - MM-DD   (assume current year)
      - DD      (assume current month & year)
    Returns a datetime.date
    """
    today = date.today()

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg):
        # YYYY-MM-DD
        return date.fromisoformat(arg)

    if re.fullmatch(r"\d{1,2}-\d{1,2}", arg):
        # MM-DD
        month_s, day_s = arg.split("-", 1)
        month = int(month_s)
        day = int(day_s)
        return date(today.year, month, day)

    if re.fullmatch(r"\d{1,2}", arg):
        # DD
        day = int(arg)
        return date(today.year, today.month, day)

    raise ValueError(f"Unrecognized date format: {arg}")


def read_lines_for_date(target: date) -> List[str]:
    """
    Read log file and return lines that start with the target date (YYYY-MM-DD).
    """
    if not os.path.exists(LOG_PATH):
        return []

    prefix = target.isoformat()
    matched: List[str] = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for ln in f:
            if ln.startswith(prefix):
                matched.append(ln.rstrip("\n"))
    return matched


def _read_all_lines() -> List[str]:
    """
    Read all lines from the log file and return them without trailing newlines.
    """
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f]


def _write_all_lines(lines: List[str]) -> None:
    """
    Overwrite the log file with the given lines (adds newline after each).
    """
    ensure_log_path()
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(f"{ln}\n")


@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context) -> None:
    """
    klogg - simple work logger

    When run with no subcommand, behave like "ls" and show today's entries.
    Use "add" (or alias "a") to append a log entry:
      klogg add Fixed the widget
      klogg a quick note
    """
    # Default action when no subcommand is provided: show today's entries
    if ctx.invoked_subcommand is None:
        target = date.today()
        lines = read_lines_for_date(target)
        if not lines:
            return
        for ln in lines:
            click.echo(ln)


@main.command("add", aliases=["a"])
@click.argument("message", nargs=-1)
@click.pass_context
def add(ctx: click.Context, message: List[str]) -> None:
    """
    Add a new log entry. Alias: 'a'
    """
    if not message:
        click.echo("Usage: klogg add <message>", err=True)
        ctx.exit(1)
    msg = " ".join(message).strip()
    line = append_log(msg)
    click.echo(f"{line}")


# 'a' is provided as a true alias via click-aliases (see decorator above)


@main.command("pause", aliases=["p"])
def pause_cmd() -> None:
    """
    Record a short pause marker. Alias: 'p'

    This appends the exact string "<pause>" (with angle brackets) as a log entry.
    """
    line = append_log("<pause>")
    click.echo(f"{line}")


@main.command("begin", aliases=["b"])
def begin_cmd() -> None:
    """
    Record a begin marker. Alias: 'b'

    This appends the exact string "<begin>" (with angle brackets) as a log entry.
    """
    line = append_log("<begin>")
    click.echo(f"{line}")


@main.command("end", aliases=["e"])
def end_cmd() -> None:
    """
    Record an end marker. Alias: 'e'

    This appends the exact string "<end>" (with angle brackets) as a log entry.
    """
    line = append_log("<end>")
    click.echo(f"{line}")


@main.command("ls")
@click.argument("when", required=False)
def ls(when: Optional[str]) -> None:
    """
    List entries for today by default.

    If WHEN is provided, it can be:
      - YYYY-MM-DD
      - MM-DD     (assumes current year)
      - DD        (assumes current month & year)
    """
    if when:
        try:
            target = parse_date_arg(when)
        except Exception as e:
            click.echo(f"Error parsing date: {e}", err=True)
            sys.exit(2)
    else:
        target = date.today()

    lines = read_lines_for_date(target)
    if not lines:
        return

    for ln in lines:
        click.echo(ln)


@main.command("rm")
def rm() -> None:
    """
    Remove the last log entry from the log file.

    The command prints the last entry and prompts the user (Y/n) before deleting.
    """
    lines = _read_all_lines()
    if not lines:
        click.echo("No log entries found.", err=True)
        return

    # Find last non-empty line (skip any trailing empty lines)
    idx = len(lines) - 1
    while idx >= 0 and lines[idx] == "":
        idx -= 1

    if idx < 0:
        click.echo("No log entries found.", err=True)
        return

    last_entry = lines[idx]
    click.echo(last_entry)

    if click.confirm("Delete this entry?", default=True):
        # Remove the selected line and write file back
        del lines[idx]
        _write_all_lines(lines)
        click.echo("Deleted.")
    else:
        click.echo("Aborted.")


# Helper: parse individual log lines into timestamp + message
def _parse_log_line(ln: str) -> Optional[Tuple[datetime, str]]:
    """
    Parse a log line of the form:
      2025-12-15 11:15:00>  Message
    Returns (datetime, message) or None if the line doesn't match.
    """
    m = re.match(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})>\s*(?P<msg>.*)$", ln)
    if not m:
        return None
    try:
        ts = datetime.strptime(m.group("ts"), TIME_FORMAT)
    except Exception:
        return None
    return ts, m.group("msg")


def _format_timedelta(td: Optional[timedelta]) -> str:
    if td is None:
        return "-"
    total_seconds = int(td.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


@main.command("time")
@click.argument("when", required=False)
def time_cmd(when: Optional[str] = None) -> None:
    """
    Show log lines for a given day (YYYY-MM-DD) or month (YYYY-MM),
    printing the time spent on each displayed item.

    The time spent for an item is computed as the difference between its
    timestamp and the timestamp of the item before it (the previous entry).
    Special markers "<begin>", "<end>" and "<pause>" are not displayed but
    are used as reference timestamps when computing durations.

    If WHEN is omitted, the command assumes the current date (today).
    """
    # Determine mode: day or month. If no argument is provided, assume today (day).
    if not when:
        mode = "day"
        target_date = date.today()
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", when):
        mode = "day"
        target_date = date.fromisoformat(when)
    elif re.fullmatch(r"\d{4}-\d{2}", when):
        mode = "month"
        year_s, month_s = when.split("-", 1)
        year = int(year_s)
        month = int(month_s)
    else:
        click.echo("Invalid date format. Use YYYY-MM-DD or YYYY-MM", err=True)
        sys.exit(2)

    # Read and parse all log lines (we need previous-entry timestamps even if
    # they fall outside the requested date/month).
    raw_lines = _read_all_lines()
    parsed: List[Tuple[datetime, str]] = []
    for ln in raw_lines:
        parsed_line = _parse_log_line(ln)
        if parsed_line:
            parsed.append(parsed_line)

    if not parsed:
        return

    # Compute durations: for each entry, duration = current.ts - previous.ts
    durations: List[Optional[timedelta]] = []
    prev_ts: Optional[datetime] = None
    for ts, _ in parsed:
        if prev_ts is None:
            durations.append(None)
        else:
            durations.append(ts - prev_ts)
        prev_ts = ts

    # Iterate and print matching, non-special entries and compute total time
    special = {"<begin>", "<end>", "<pause>"}
    found = False
    total_td = timedelta(0)
    total_counted = False  # whether we actually added any non-None durations

    for (ts, msg), dur in zip(parsed, durations):
        if msg in special:
            # markers are used only for timing reference
            continue
        if mode == "day":
            if ts.date() != target_date:
                continue
        else:  # month
            if ts.year != year or ts.month != month:
                continue

        found = True
        time_str = ts.strftime(TIME_FORMAT)
        dur_str = _format_timedelta(dur)
        click.echo(f"{time_str}>  {msg}    ({dur_str})")

        if dur is not None:
            total_td += dur
            total_counted = True

    if not found:
        # nothing matched — exit silently (consistent with other commands)
        return

    # Print total of displayed times
    total_str = _format_timedelta(total_td if total_counted else None)
    click.echo(f"Total: {total_str}")
