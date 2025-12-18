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
    prefix = "[verify/answers]"

    try:  # allow direct invocation without Typer converting options
        from typer.models import OptionInfo

        if isinstance(part, OptionInfo):
            part = part.default
    except Exception:
        pass

    if dry_run:
        typer.echo(f"{prefix} (dry-run) Would verify Year {year}, Day {day:02d}, part={part}")
        return

    from pysleigh.commands.solution import _load_expected_answers  # imported lazily for reuse

    expected_1, expected_2 = _load_expected_answers(paths, year, day)
    if expected_1 is None and expected_2 is None:
        typer.echo(f"{prefix} No cached answers found for Year {year}, Day {day:02d}.")
        raise typer.Exit(code=1)

    solution = load_solution(year, day)
    actual_1, actual_2 = solution.run(output=False)
    ok = True

    def check(label: str, expected: str | None, actual: str | None) -> None:
        nonlocal ok
        if expected is None:
            typer.echo(f"{prefix} {label}: skipped (no cached answer).")
            return
        if actual is None:
            typer.echo(f"{prefix} {label}: missing actual output.")
            ok = False
            return
        if str(actual) == str(expected):
            typer.echo(f"{prefix} {label}: OK ({actual})")
        else:
            typer.echo(
                f"{prefix} {label}: MISMATCH (cached {expected!r} vs actual {actual!r})"
            )
            ok = False

    if part in (1, None):
        check("Part 1", expected_1, actual_1)
    if part in (2, None):
        check("Part 2", expected_2, actual_2)

    if not ok:
        raise typer.Exit(code=1)
