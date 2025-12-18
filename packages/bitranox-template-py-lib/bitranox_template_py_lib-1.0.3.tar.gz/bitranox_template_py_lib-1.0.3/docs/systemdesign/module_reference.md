# Feature Documentation: CLI Behavior Scaffold

## Status

Complete

## Links & References
**Feature Requirements:** Scaffold requirements (ad-hoc)
**Task/Ticket:** None documented
**Pull Requests:** Pending current refactor
**Related Files:**

* src/bitranox_template_py_lib/behaviors.py
* src/bitranox_template_py_lib/cli.py
* src/bitranox_template_py_lib/__main__.py
* src/bitranox_template_py_lib/__init__.py
* src/bitranox_template_py_lib/__init__conf__.py
* tests/test_cli.py
* tests/test_module_entry.py
* tests/test_behaviors.py
* tests/test_scripts.py

---

## Problem Statement

The original scaffold concentrated the greeting, failure trigger, and CLI
orchestration inside a single module, making it harder to explain module intent
and to guarantee that the console script and ``python -m`` execution paths stay
behaviourally identical. We needed clearer module boundaries and shared helpers
for traceback preferences without introducing the full domain/application
separation that would be overkill for this minimal template.

## Solution Overview

* Extracted the behaviour helpers into ``behaviors.py`` so both CLI and library
  consumers have a single cohesive module documenting the temporary domain.
* Simplified ``cli.py`` to import the behaviour helpers, with all imports at
  module top for better readability and static analysis.
* Added helper functions ``_exit_code_from()`` and ``_print_error()`` to handle
  exit code extraction and error formatting with clear single responsibilities.
* Used modern type hints (``X | None`` syntax) and explicit ``__all__`` exports
  for clear public API surface.
* Reduced ``__main__.py`` to a thin wrapper delegating to the CLI helper.
* Re-exported the helpers through ``__init__.py`` so CLI and library imports
  draw from the same source.
* Documented the responsibilities in this module reference so future refactors
  have an authoritative baseline.

---

## Architecture Integration

**App Layer Fit:** This package remains a CLI-first utility; all modules live in
the transport/adapter layer, with ``behaviors.py`` representing the small
stand-in domain.

**Data Flow:**
1. CLI parses options with rich-click.
2. Rich traceback is installed by default (``--no-traceback`` disables it).
3. Commands delegate to behaviour helpers.
4. Exceptions are caught and formatted via ``_print_error()``.
5. Exit codes are extracted via ``_exit_code_from()`` for proper shell integration.

**System Dependencies:**
* ``rich_click`` for CLI UX with beautiful output
* ``rich`` for enhanced tracebacks and console output
* ``importlib.metadata`` via ``__init__conf__`` to present package metadata

---

## Core Components

### behaviors.emit_greeting

* **Purpose:** Write the canonical greeting used in smoke tests and
  documentation.
* **Input:** Optional text stream (defaults to ``sys.stdout``).
* **Output:** Writes ``"Hello World\n"`` to the stream and flushes if possible.
* **Location:** src/bitranox_template_py_lib/behaviors.py

### behaviors.raise_intentional_failure

* **Purpose:** Provide a deterministic failure hook for error-handling tests.
* **Input:** None.
* **Output:** Raises ``RuntimeError('I should fail')``.
* **Location:** src/bitranox_template_py_lib/behaviors.py

### behaviors.noop_main

* **Purpose:** Placeholder entry for transports expecting a ``main`` callable.
* **Input:** None.
* **Output:** Returns ``None``.
* **Location:** src/bitranox_template_py_lib/behaviors.py

### cli._exit_code_from

* **Purpose:** Extract integer exit code from SystemExit exceptions.
* **Input:** SystemExit exception instance.
* **Output:** Integer exit code (the code itself if int, 1 if truthy, 0 if falsy).
* **Location:** src/bitranox_template_py_lib/cli.py

### cli._print_error

* **Purpose:** Print error to console with or without full traceback.
* **Input:** Exception instance and boolean show_traceback flag.
* **Output:** Prints rich traceback (with locals) or simple error message to console.
* **Location:** src/bitranox_template_py_lib/cli.py

### cli.main

* **Purpose:** Entry point for console scripts and module execution, handling
  exit codes and exception propagation.
* **Input:** Optional argv sequence (defaults to sys.argv[1:]).
* **Output:** Integer exit code (0 for success, non-zero for errors).
* **Location:** src/bitranox_template_py_lib/cli.py

### cli.cli_info / cli.cli_hello / cli.cli_fail

* **Purpose:** Subcommands for displaying metadata, greeting, and triggering
  intentional failures for testing error handling.
* **Input:** None (commands receive Click context automatically).
* **Output:** None (execute their respective behaviors).
* **Location:** src/bitranox_template_py_lib/cli.py

### __main__

* **Purpose:** Provide ``python -m bitranox_template_py_lib`` entry point by
  delegating directly to ``cli.main()``.
* **Input:** None (reads from sys.argv).
* **Output:** System exit with code from ``cli.main()``.

### __init__conf__.print_info

* **Purpose:** Render the statically-defined project metadata for the CLI ``info`` command.
* **Input:** None.
* **Output:** Writes the hard-coded metadata block to ``stdout``.
* **Location:** src/bitranox_template_py_lib/__init__conf__.py

### Package Exports

* ``__init__.py`` re-exports behaviour helpers and ``print_info`` for library
  consumers via explicit ``__all__`` declaration. No legacy compatibility layer
  remains; new code should import from the canonical module paths.
* ``cli.py`` exports its public API via ``__all__``: ``CLICK_CONTEXT_SETTINGS``,
  ``cli``, ``cli_fail``, ``cli_hello``, ``cli_info``, ``console``, ``main``.

---

## Implementation Details

**Dependencies:**

* External: ``rich_click``, ``rich`` (for Console and traceback)
* Internal: ``behaviors`` module, ``__init__conf__`` static metadata constants

**Key Configuration:**

* No environment variables required.
* Traceback preferences controlled via CLI ``--traceback`` flag.

**Database Changes:**

* None.

**Error Handling Strategy:**

* Rich tracebacks are installed by default; ``--no-traceback`` suppresses them.
* Click runs with ``standalone_mode=False`` so exceptions are caught by ``main()``.
* ``_exit_code_from()`` extracts proper exit codes from SystemExit exceptions.
* ``_print_error()`` formats exceptions as rich tracebacks or simple error messages.
* Exit codes are returned via ``raise SystemExit(main())`` for proper shell integration.

---

## Testing Approach

**Manual Testing Steps:**

1. ``bitranox_template_py_lib`` → prints CLI help (no default action).
2. ``bitranox_template_py_lib hello`` → prints greeting.
3. ``bitranox_template_py_lib fail`` → prints full rich traceback (default).
4. ``bitranox_template_py_lib --no-traceback fail`` → prints simple error message.
5. ``python -m bitranox_template_py_lib fail`` → matches console script behavior.

**Automated Tests:**

* ``tests/test_cli.py`` exercises the help-first behaviour, failure path,
  metadata output, and invalid command handling for the click surface.
* ``tests/test_module_entry.py`` ensures ``python -m`` entry mirrors the console
  script, including traceback behaviour.
* ``tests/test_behaviors.py`` verifies greeting/failure helpers against custom
  streams.
* ``tests/test_scripts.py`` validates the automation entry points via the shared
  scripts CLI.
* ``tests/test_cli.py`` and ``tests/test_module_entry.py`` now introduce
  structured recording helpers (``CapturedRun`` and ``PrintedTraceback``) so the
  assertions read like documented scenarios.
* Doctests embedded in behaviour and CLI helpers provide micro-regression tests
  for argument handling.

**Edge Cases:**

* Running without subcommand shows CLI help (default behavior).
* Running with ``--traceback`` flag explicitly (no subcommand) delegates to ``noop_main``.
* Traceback preference is determined per-invocation from argv; no global state.

**Test Data:**

* No fixtures required; tests rely on built-in `CliRunner` and monkeypatching.

---

## Known Issues & Future Improvements

**Current Limitations:**

* Behaviour module still contains placeholder logic; real logging helpers will
  replace it in future iterations.

**Future Enhancements:**

* Introduce structured logging once the logging stack lands.
* Expand the module reference when new commands or behaviours are added.

---

## Risks & Considerations

**Technical Risks:**

* Traceback formatting depends on Rich's traceback module; updates may change
  the appearance of error output.

**User Impact:**

* None expected; CLI surface and public imports remain backward compatible.

---

## Documentation & Resources

**Internal References:**

* README.md – usage examples
* INSTALL.md – installation options
* DEVELOPMENT.md – developer workflow

**External References:**

* rich-click documentation: https://github.com/ewels/rich-click
* rich documentation: https://rich.readthedocs.io/

---

**Created:** 2025-09-26 by Codex (automation)
**Last Updated:** 2025-12-15 by Claude Code
**Review Cycle:** Evaluate during next logging feature milestone

---

## Instructions for Use

1. Trigger this document whenever CLI behaviour helpers change.
2. Keep module descriptions in sync with code during future refactors.
3. Extend with new components when additional commands or behaviours ship.
