# ismk

ismk is a lightweight fork of Snakemake (v9.14) that makes workflows fileless by design.
Instead of forcing you to create a Snakefile on disk, ismk lets you define and run workflows directly from Python strings, entirely in-process.

This is especially handy for programmatic or dynamic workflow generation—think “build the Snakefile on the fly, run it immediately, and leave no files behind.”

Updates will be aligned with upstream major releases when needed, rather than tracking every minor version bump.

## What's different from upstream

### Added

- StringSourceFile class (sourcecache.py:105–142)
  - A SourceFile implementation that keeps Snakefile content in memory
  - Enables workflows to be sourced straight from strings

- Workflow.include_string() method (workflow.py:1667–1710)
  - Load Snakefile content directly from a string
  - Full Snakemake/Snakefile syntax supported
  - Optional debug mode to print compiled code for easier inspection

- Bug fix (api.py:610–612)
  - Fixes missing initialization of scheduler_settings when using scheduler='greedy' directly

### Removed

To stay focused on the core library experience, ismk strips out:

- Docs (Please read the official snakemake online docs)
- Some development tooling configs

Note: The tests/ module itself is kept to support Snakemake’s built-in testing features.

### Others

Performed some code formatting and minor refactoring.

## License

MIT License — same as upstream Snakemake.
