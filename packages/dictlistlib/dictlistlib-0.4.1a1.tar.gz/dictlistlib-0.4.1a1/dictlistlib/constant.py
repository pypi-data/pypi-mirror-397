"""
Constants and status codes for dictlistlib.

This module defines enumerated constants used to represent
execution or validation outcomes. The `ECODE` class is implemented
as an `enum.IntFlag`, allowing bitwise operations and comparisons
between status codes.

Classes
-------
ECODE : enum.IntFlag
    Enumeration of execution codes:
    - SUCCESS (0) : Indicates a successful operation.
    - BAD (1)     : Indicates a failed or invalid operation.
    - PASSED      : Alias for SUCCESS.
    - FAILED      : Alias for BAD.

Notes
-----
- Using `IntFlag` allows combining flags with bitwise operators
  (e.g., `ECODE.SUCCESS | ECODE.BAD`).
- Aliases (`PASSED`, `FAILED`) provide semantic clarity when
  checking results in different contexts.
"""

from enum import IntFlag


class ECODE(IntFlag):
    class ECODE(IntFlag):
        """
        Enumeration of execution codes for validation and status reporting.

        This class defines simple success/failure codes using `enum.IntFlag`,
        which allows bitwise operations and comparisons. Aliases are provided
        for semantic clarity in different contexts.

        Members
        -------
        SUCCESS : int
            Code indicating a successful operation (value = 0).
        BAD : int
            Code indicating a failed or invalid operation (value = 1).
        PASSED : int
            Alias for SUCCESS, useful in contexts where "passed" is clearer.
        FAILED : int
            Alias for BAD, useful in contexts where "failed" is clearer.

        Notes
        -----
        - `IntFlag` allows combining flags with bitwise operators, though in
          this case only two states are defined.
        - Aliases (`PASSED`, `FAILED`) improve readability when checking results.
        """
    SUCCESS = 0
    BAD = 1
    PASSED = SUCCESS
    FAILED = BAD
