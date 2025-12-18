"""Typer commands for verifying solutions against cached answers."""

from __future__ import annotations

from typing import Optional

import typer

from pysleigh.context import get_context
from pysleigh.loader import load_solution

verify_app = typer.Typer(help="Verify cached answers against local solutions.")


@verify_app.command("answers")
def verify_answers(
    year: int = typer.Argument(..., help="AoC year."),
    day: int = typer.Argument(..., help="AoC day."),
    part: Optional[int] = typer.Option(
        None,
        "--part",
        min=1,
        max=2,
        help="Part to verify (1 or 2). If omitted, verifies both.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be verified without executing solution code.",
    ),
) -> None:
    """Compare cached answers with the local solution outputs."""
    paths = get_context().paths

    try:  # allow direct invocation without Typer converting options
        from typer.models import OptionInfo

        if isinstance(part, OptionInfo):
            part = part.default
    except Exception:
        pass

    if dry_run:
        typer.echo(f"(dry-run) Would verify Year {year}, Day {day:02d}, part={part}")
        return

    from pysleigh.commands.solution import _load_expected_answers  # imported lazily for reuse

    expected_1, expected_2 = _load_expected_answers(paths, year, day)
    if expected_1 is None and expected_2 is None:
        typer.echo(f"No cached answers found for Year {year}, Day {day:02d}.")
        raise typer.Exit(code=1)

    solution = load_solution(year, day)

    def puzzle_title() -> str:
        title = getattr(solution, "_title", None)
        if title is not None:
            return str(title)

        article_path = paths.article_path(year, day)
        if not article_path.exists():
            return f"Day {day:02d}"

        with article_path.open("r") as file:
            first_line = file.readline().strip()
        if ":" not in first_line:
            return first_line or f"Day {day:02d}"
        _, remainder = first_line.split(":", 1)
        return remainder.replace("---", "").strip()

    typer.echo(f"--- Year {year} Day {day:02d}: {puzzle_title()} ---")
    actual_1, actual_2 = solution.run(output=False)
    ok = True

    def check(label: str, expected: str | None, actual: str | None) -> None:
        nonlocal ok
        if expected is None:
            typer.echo(f"{label}: skipped (no cached answer).")
            return
        if actual is None:
            typer.echo(f"{label}: missing actual output.")
            ok = False
            return
        if str(actual) == str(expected):
            typer.echo(f"{label}: OK ({actual})")
        else:
            typer.echo(f"{label}: MISMATCH (cached {expected!r} vs actual {actual!r})")
            ok = False

    if part in (1, None):
        check("Part One", expected_1, actual_1)
    if part in (2, None):
        check("Part Two", expected_2, actual_2)

    if not ok:
        raise typer.Exit(code=1)
