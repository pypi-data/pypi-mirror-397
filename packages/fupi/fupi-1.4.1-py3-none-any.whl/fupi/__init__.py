"""fupi package initializer.

Behavior:
- A plain `import fupi` will automatically run the path-adding side-effect
  (preserves existing behavior).
- A `from fupi import manual_config` (or any `from fupi import ...`) will
  suppress the automatic run so the user can configure manually.
- You can also set environment variables FUPI_ADD_DIR_NAMES and FUPI_SKIP_DIR_PATTERNS 
  to extend the default directory names and skip patterns used by either 
  manual or automatic runs.

This implements a small, best-effort detection by inspecting the importer's
call-site context. It's lightweight and intentionally conservative: if we
can't detect a `from fupi import` invocation (very rare) we default to 
auto-running to preserve backwards-compatibility.
"""

import os

try:
    # import the implementation module
    from .fupi import ManualFupi, DEFAULT_ADD_DIR_NAMES, DEFAULT_SKIP_DIR_PATTERNS, shortest_path
    __all__ = ['ManualFupi', 'shortest_path', 'DEFAULT_ADD_DIR_NAMES', 'DEFAULT_SKIP_DIR_PATTERNS']
    shortest_path = []

    # Lightweight heuristic to detect `from fupi import ...` vs `import fupi`.
    # We scan the import call stack for a textual `from fupi import` occurrence.
    # If found, suppress auto-run. If we can't find such a pattern we default
    # to auto-running to preserve existing behaviour.
    def _import_was__from__style() -> bool:
        """Return True if the import appears to be a `from fupi import ...` call.

        Heuristic: scan the call stack frames. If a source line containing
        `from fupi import` is found, return True. If a source line containing
        a plain `import fupi` is found before any `from` hint, return False.

        If we can't find any useful calling source, default to False (i.e.
        allow autorun) to preserve backwards-compatibility.
        """
        try:
            import inspect
            for frame_info in inspect.stack():
                ctx = frame_info.code_context
                joined = None
                if ctx:
                    joined = ''.join(ctx).strip()
                else:
                    # attempt to read the source file line if code_context is missing
                    try:
                        fn = frame_info.filename
                        ln = frame_info.lineno
                        if fn and fn != '<string>' and fn != '<stdin>' and os.path.exists(fn):
                            with open(fn, 'r') as _f:
                                lines = _f.readlines()
                                if 0 < ln <= len(lines):
                                    joined = lines[ln-1].strip()
                    except Exception:
                        joined = None

                if not joined:
                    continue

                # look for explicit patterns
                # Catch both `from fupi import` and `from fupi.X import` (e.g., `from fupi.fupi import`)
                if 'from fupi' in joined and 'import' in joined:
                    return True
                if 'import fupi' in joined and 'from' not in joined:
                    return False
        except Exception:
            # Be conservative: if stack inspection fails, allow autorun
            return False

        # no clear evidence of a `from`-style import
        return False

    # if `from fupi import ManualFupi` style detected, skip autorun:
    was__FROM__import = _import_was__from__style()
    if not was__FROM__import:
        try:
            AutoFupi = ManualFupi(autorun=True)
            shortest_path = AutoFupi.shortest_path()

            pass # module exits after this point, in normal operations
        except Exception as e:
            import traceback, sys as _sys
            print(f"Error importing or running fupi: {e}", file=_sys.stderr)
            traceback.print_exc()

except Exception as e:
    import traceback, sys as _sys
    print(f"Error importing fupi package: {e}", file=_sys.stderr)
    traceback.print_exc()
