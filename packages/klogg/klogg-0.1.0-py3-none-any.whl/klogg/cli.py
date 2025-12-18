import os
import re
import sys
from datetime import datetime, date
from typing import List, Optional

import click

LOG_PATH = os.path.expanduser("~/.config/klogg/default.log")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def ensure_log_path() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def append_log(message: str) -> None:
    ensure_log_path()
    timestamp = datetime.now().strftime(TIME_FORMAT)
    line = f"{timestamp}>  {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)


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


@click.group(invoke_without_command=True)
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


@main.command("add")
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
    append_log(msg)


# register alias 'a' for convenience
main.add_command(add, name="a")


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
