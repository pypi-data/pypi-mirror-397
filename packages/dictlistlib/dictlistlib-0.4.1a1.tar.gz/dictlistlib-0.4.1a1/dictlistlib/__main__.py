"""
__main__.py

Entry point for the DictListLib command-line interface (CLI).

This module initializes and runs the CLI application by importing
the `Cli` class from `dictlistlib.main`. When executed, it creates
a console instance and starts the interactive command-line session.

Usage
-----
Run the package directly from the command line:

    python -m dictlistlib

This will invoke the CLI and allow users to interact with the
DictListLib library through supported commands.

Workflow
--------
1. Import the `Cli` class from `dictlistlib.main`.
2. Instantiate a `Cli` object (`console`).
3. Call `console.run()` to start the CLI loop.

Classes
-------
Cli : dictlistlib.main.Cli
    The command-line interface class that defines available commands,
    options, and execution flow.

Notes
-----
- This file serves as the executable entry point when the package
  is run as a module.
- All CLI logic is encapsulated in `dictlistlib.main.Cli`.
"""

from dictlistlib.main import Cli

console = Cli()
console.run()
