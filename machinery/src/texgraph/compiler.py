"""
LuaLaTeX compiler for Texgraph.

Invokes ``lualatex`` as a subprocess, captures its output, parses the log
file for errors and warnings, and returns a structured :class:`CompileResult`.

Typical usage::

    from texgraph.compiler import Compiler, CompileResult
    from texgraph.config import CollectionConfig

    config = CollectionConfig.from_yaml("collection.yaml")
    compiler = Compiler(lualatex_path=config.lualatex_path)
    result = compiler.compile(
        tex_path="output/collection.tex",
        output_dir="output/",
        runs=2,
        draft=config.draft_mode,
    )

    if result.success:
        print(f"PDF written to {result.pdf_path}")
    else:
        for err in result.errors:
            print(err)
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class CompileResult:
    """Outcome of a single :meth:`Compiler.compile` call.

    Attributes
    ----------
    success:
        ``True`` if lualatex exited with return code 0 **and** no fatal
        errors were detected in the log.
    pdf_path:
        Path to the generated PDF file, or ``None`` if compilation failed.
    log_path:
        Path to the ``.log`` file produced by lualatex.
    errors:
        List of error strings extracted from the lualatex log.
    warnings:
        List of warning strings extracted from the lualatex log.
    runs_completed:
        How many lualatex runs were actually performed.
    returncode:
        Raw process exit code from the final lualatex invocation.
    """

    success: bool
    pdf_path: Path | None
    log_path: Path | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    runs_completed: int = 0
    returncode: int = 0


# ---------------------------------------------------------------------------
# Log parsing helpers
# ---------------------------------------------------------------------------

# Patterns that indicate a fatal LaTeX error in the log
_ERROR_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^! (.+)$", re.MULTILINE),                         # ! Emergency stop
    re.compile(r"^! LaTeX Error: (.+)$", re.MULTILINE),            # ! LaTeX Error:
    re.compile(r"^! Undefined control sequence\.", re.MULTILINE),
    re.compile(r"^!\s+(.+)$", re.MULTILINE),
]

# Patterns for extractable warnings (non-fatal)
_WARNING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(LaTeX Warning: .+?)(?=\n\n|\Z)", re.DOTALL),
    re.compile(r"(Package \w+ Warning: .+?)(?=\n\n|\Z)", re.DOTALL),
    re.compile(r"(Overfull \\hbox .+)$", re.MULTILINE),
    re.compile(r"(Underfull \\hbox .+)$", re.MULTILINE),
]

# Indicates the run ended with errors
_FATAL_MARKERS: list[str] = [
    "Emergency stop.",
    "==> Fatal error occurred",
    "no output PDF file produced",
]


def _parse_log(log_text: str) -> tuple[list[str], list[str]]:
    """Extract errors and warnings from a lualatex ``.log`` file.

    Parameters
    ----------
    log_text:
        Raw contents of the ``*.log`` file.

    Returns
    -------
    tuple[list[str], list[str]]
        ``(errors, warnings)`` — each a deduplicated list of strings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    def _add(bucket: list[str], msg: str) -> None:
        clean = " ".join(msg.split())  # normalise whitespace
        if clean and clean not in seen:
            seen.add(clean)
            bucket.append(clean)

    for pattern in _ERROR_PATTERNS:
        for match in pattern.finditer(log_text):
            _add(errors, match.group(1) if match.lastindex else match.group(0))

    # Check for fatal markers in case the pattern didn't catch them
    for marker in _FATAL_MARKERS:
        if marker in log_text:
            _add(errors, marker)

    for pattern in _WARNING_PATTERNS:
        for match in pattern.finditer(log_text):
            _add(warnings, match.group(1))

    return errors, warnings


# ---------------------------------------------------------------------------
# Compiler class
# ---------------------------------------------------------------------------

class Compiler:
    """Compile a ``.tex`` file to PDF using LuaLaTeX.

    Parameters
    ----------
    lualatex_path:
        Path or name of the ``lualatex`` binary.  Defaults to ``"lualatex"``,
        which works when TeX Live / MiKTeX is on ``PATH``.
    """

    def __init__(self, lualatex_path: str = "lualatex") -> None:
        self._lualatex = lualatex_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile(
        self,
        tex_path: str | Path,
        output_dir: str | Path,
        *,
        runs: int = 2,
        draft: bool = False,
    ) -> CompileResult:
        """Compile *tex_path* to a PDF inside *output_dir*.

        In non-draft mode, lualatex is run ``runs`` times (default 2) to
        resolve cross-references and generate correct page numbers.  In draft
        mode a single pass is performed and PDF/X metadata injection is
        skipped.

        Parameters
        ----------
        tex_path:
            Path to the ``.tex`` source file.
        output_dir:
            Directory where lualatex should write its output (PDF, log, aux).
        runs:
            Number of lualatex invocations.  Ignored in draft mode (always 1).
        draft:
            When ``True``, run only once and skip PDF/X compliance steps.

        Returns
        -------
        CompileResult
            Structured result with success flag, paths, errors, and warnings.
        """
        tex_path = Path(tex_path).resolve()
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        if not tex_path.exists():
            return CompileResult(
                success=False,
                pdf_path=None,
                log_path=None,
                errors=[f"Source file not found: {tex_path}"],
            )

        actual_runs = 1 if draft else max(1, runs)
        returncode = 0
        runs_completed = 0

        for run_num in range(1, actual_runs + 1):
            returncode, stdout, stderr = self._run_lualatex(
                tex_path=tex_path,
                output_dir=output_dir,
                run_num=run_num,
                total_runs=actual_runs,
            )
            runs_completed += 1

            # Bail early on hard failure (return code != 0) before final run
            if returncode != 0 and run_num < actual_runs:
                # Continue to get the log from the failed run, then break
                break

        # Locate the generated files
        stem = tex_path.stem
        pdf_path = output_dir / f"{stem}.pdf"
        log_path = output_dir / f"{stem}.log"

        # Parse log for diagnostics
        errors: list[str] = []
        warnings: list[str] = []
        if log_path.exists():
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            errors, warnings = _parse_log(log_text)

        # Determine overall success
        success = (returncode == 0) and pdf_path.exists() and not any(
            marker in "\n".join(errors) for marker in _FATAL_MARKERS
        )

        return CompileResult(
            success=success,
            pdf_path=pdf_path if pdf_path.exists() else None,
            log_path=log_path if log_path.exists() else None,
            errors=errors,
            warnings=warnings,
            runs_completed=runs_completed,
            returncode=returncode,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_lualatex(
        self,
        tex_path: Path,
        output_dir: Path,
        run_num: int,
        total_runs: int,
    ) -> tuple[int, str, str]:
        """Execute a single lualatex invocation.

        Returns
        -------
        tuple[int, str, str]
            ``(returncode, stdout_text, stderr_text)``
        """
        cmd = [
            self._lualatex,
            "--interaction=nonstopmode",    # never pause for user input
            "--halt-on-error",              # stop at the first error
            f"--output-directory={output_dir}",
            str(tex_path),
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(tex_path.parent),
            )
        except FileNotFoundError:
            msg = (
                f"lualatex binary not found: '{self._lualatex}'.  "
                "Make sure TeX Live or MiKTeX is installed and on PATH."
            )
            return 127, "", msg
        except OSError as exc:
            return 1, "", f"OS error running lualatex: {exc}"

        return proc.returncode, proc.stdout, proc.stderr

    # ------------------------------------------------------------------
    # Utility: check lualatex availability
    # ------------------------------------------------------------------

    def check_available(self) -> bool:
        """Return ``True`` if the configured lualatex binary is callable."""
        try:
            proc = subprocess.run(
                [self._lualatex, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return proc.returncode == 0
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return False

    def lualatex_version(self) -> str | None:
        """Return the lualatex version string, or ``None`` if unavailable."""
        try:
            proc = subprocess.run(
                [self._lualatex, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if proc.returncode == 0:
                return proc.stdout.splitlines()[0] if proc.stdout else "unknown"
            return None
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return None
