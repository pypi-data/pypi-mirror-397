"""Exception classes for dictlistlib.

This module defines a collection of custom exception classes used
throughout the dictlistlib application. Each exception type is
specialized to capture and report errors in specific components,
such as list operations, query execution, validation, predicates,
and utility functions. By using these custom exceptions, the
application provides clearer error handling and more descriptive
feedback to developers and users.
"""


class ListError(Exception):
    """Base exception for errors related to `List` instances."""


class ListIndexError(ListError):
    """Raised when an invalid index is accessed in a `List` instance."""


class ResultError(Exception):
    """Raised when an error occurs while handling a `Result` instance."""


class LookupClsError(Exception):
    """Raised when an error occurs in a `LookupObject` instance."""


class ObjectArgumentError(Exception):
    """Raised when invalid arguments are passed to an `Object` class."""


class ArgumentError(Exception):
    """Base exception for argument-related errors."""


class ArgumentValidationError(ArgumentError):
    """Raised when argument validation fails."""


class DLQueryError(Exception):
    """Base exception for errors related to `DLQuery` instances."""


class DLQueryDataTypeError(DLQueryError):
    """Raised when a query uses an unsupported data type."""


class PredicateError(Exception):
    """Base exception for errors related to predicates."""


class PredicateParameterDataTypeError(PredicateError):
    """Raised when a predicate receives parameters of an invalid data type."""


class ValidationError(Exception):
    """Base exception for validation-related errors."""


class ValidationIpv6PrefixError(ValidationError):
    """Raised when an IPv6 prefix fails validation."""


class ValidationOperatorError(ValidationError):
    """Raised when an operator is misused during validation."""


class ParsedTimezoneError(Exception):
    """Raised when parsing a custom datetime fails due to timezone issues."""


class UtilsError(Exception):
    """Base exception for utility-related errors."""


class RegexConversionError(UtilsError):
    """Raised when a regular expression conversion fails."""
