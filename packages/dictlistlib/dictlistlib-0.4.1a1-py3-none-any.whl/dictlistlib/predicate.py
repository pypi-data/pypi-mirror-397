"""Predicate logic for dictlistlib.

This module provides utility functions and the `Predicate` class
for evaluating conditions against dictionary-based records. It
supports validation using regular expressions, operators, custom
rules, version comparisons, and datetime checks. Predicates are
used internally by dictlistlib to filter and query data in a
flexible, SQL-like manner.

Classes
-------
Predicate
    Provides class methods for validating conditions such as equality,
    inequality, pattern matching, containment, membership, and type-specific
    comparisons.

Functions
---------
get_value(data, key)
    Safely retrieve a value from a dictionary or dict-like object.
"""

import logging
from dictlistlib.validation import RegexValidation
from dictlistlib.validation import OpValidation
from dictlistlib.validation import CustomValidation
from dictlistlib.validation import VersionValidation
from dictlistlib.validation import DatetimeValidation

from dictlistlib.exceptions import PredicateParameterDataTypeError

logger = logging.getLogger(__file__)


def get_value(data, key):
    """
    Safely retrieve a value from a dictionary or dict-like object.

    This function attempts to access the value associated with the
    given key. If the input is not a dictionary, a
    `PredicateParameterDataTypeError` is raised. If an unexpected
    error occurs during retrieval, a warning is logged and a
    sentinel string `"__EXCEPTION__"` is returned.

    Parameters
    ----------
    data : dict
        A dictionary or dict-like instance.
    key : str
        The key whose value should be retrieved.

    Returns
    -------
    Any
        The value associated with the key if found, otherwise
        `"__EXCEPTION__"` if an error occurs.

    Raises
    ------
    PredicateParameterDataTypeError
        If `data` is not a dictionary.
    """
    if not isinstance(data, dict):
        msg = 'data must be instance of dict (?? {} ??).'.format(type(data))
        raise PredicateParameterDataTypeError(msg)
    try:
        value = data.get(key)
        return value
    except Exception as ex:
        msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
        logger.warning(msg)
        return '__EXCEPTION__'


class Predicate:
    """
    Predicate-based validation utilities for dictlistlib.

    The `Predicate` class provides a collection of class methods
    for evaluating conditions against dictionary-based records.
    These methods support equality checks, pattern matching,
    containment, membership, and type-specific comparisons such
    as numeric, version, and datetime validations.

    Methods
    -------
    is_(data, key='', custom='', on_exception=True) -> bool
        Return True if the value matches the custom validation.
    isnot(data, key='', custom='', on_exception=True) -> bool
        Return True if the value does not match the custom validation.
    match(data, key='', pattern='', on_exception=True) -> bool
        Return True if the value matches the regex pattern.
    notmatch(data, key='', pattern='', on_exception=True) -> bool
        Return True if the value does not match the regex pattern.
    compare_number(data, key='', op='', other='', on_exception=True) -> bool
        Compare numeric values using the given operator.
    compare(data, key='', op='', other='', on_exception=True) -> bool
        Compare values using the given operator.
    contain(data, key='', other='', on_exception=True) -> bool
        Return True if the value contains the given substring.
    notcontain(data, key='', other='', on_exception=True) -> bool
        Return True if the value does not contain the given substring.
    belong(data, key='', other='', on_exception=True) -> bool
        Return True if the value belongs to the given collection.
    notbelong(data, key='', other='', on_exception=True) -> bool
        Return True if the value does not belong to the given collection.
    true(data) -> bool
        Always return True (useful for unconditional predicates).
    false(data) -> bool
        Always return False (useful for unconditional predicates).
    """
    @classmethod
    def is_(cls, data, key='', custom='', on_exception=True):
        """
        Validate whether a value satisfies a custom condition.

        This method acts as the `is` keyword for expression validation.
        It retrieves the value associated with the given key from a
        dictionary-like object and applies a custom validation rule.
        The validation is performed using `CustomValidation.validate`.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be validated. Default is an empty string.
        custom : str, optional
            A custom keyword or rule to validate against. Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value satisfies the custom validation condition,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails.
        """
        value = get_value(data, key)
        result = CustomValidation.validate(
            custom, value, on_exception=on_exception
        )
        return result

    @classmethod
    def isnot(cls, data, key='', custom='', on_exception=True):
        """
        Validate whether a value does *not* satisfy a custom condition.

        This method acts as the `isnot` (or `is_not`) keyword for expression
        validation. It retrieves the value associated with the given key from
        a dictionary-like object and applies a custom validation rule, returning
        True if the value does **not** meet the condition.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be validated. Default is an empty string.
        custom : str, optional
            A custom keyword or rule to validate against. Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value does not satisfy the custom validation condition,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails.
        """

        value = get_value(data, key)
        result = CustomValidation.validate(
            custom, value, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def match(cls, data, key='', pattern='', on_exception=True):
        """
        Validate whether a value matches a regular expression pattern.

        This method acts as the `match` keyword for expression validation.
        It retrieves the value associated with the given key from a
        dictionary-like object and applies a regular expression check
        using `RegexValidation.match`.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be validated. Default is an empty string.
        pattern : str, optional
            A regular expression pattern to test against the value.
            Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value matches the regular expression pattern,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and regex validation fails.
        """
        value = get_value(data, key)
        result = RegexValidation.match(
            pattern, value, on_exception=on_exception
        )
        return result

    @classmethod
    def notmatch(cls, data, key='', pattern='', on_exception=True):
        """
        Validate whether a value does *not* match a regular expression pattern.

        This method acts as the `notmatch` (or `not_match`) keyword for
        expression validation. It retrieves the value associated with the
        given key from a dictionary-like object and applies a regular
        expression check using `RegexValidation.match`. The result is True
        if the value does **not** match the given pattern.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be validated. Default is an empty string.
        pattern : str, optional
            A regular expression pattern to test against the value.
            Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value does not match the regular expression pattern,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and regex validation fails.
        """
        value = get_value(data, key)
        result = RegexValidation.match(
            pattern, value, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_number(cls, data, key='', op='', other='', on_exception=True):
        """
        Compare a numeric value against another number using a relational operator.

        This method acts as the `compare_number` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and applies a numeric comparison using the specified operator.

        Supported operators
        -------------------
        - ``lt`` : less than
        - ``le`` : less than or equal to
        - ``gt`` : greater than
        - ``ge`` : greater than or equal to
        - ``eq`` : equal to
        - ``ne`` : not equal to

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose numeric value should be compared. Default is an empty string.
        op : str, optional
            The comparison operator (e.g., ``lt``, ``gt``, ``eq``). Default is an empty string.
        other : int, float, or str, optional
            The number to compare against. Can be provided as a string or numeric type.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value satisfies the operator comparison with `other`,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and comparison fails due to invalid input.
        """
        value = get_value(data, key)
        result = OpValidation.compare_number(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare(cls, data, key='', op='', other='', on_exception=True):
        """
        Compare a value against another using an equality or inequality operator.

        This method acts as the `compare` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and applies a comparison using the specified operator.

        Supported operators
        -------------------
        - ``eq`` : equal to
        - ``ne`` : not equal to

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be compared. Default is an empty string.
        op : str, optional
            The comparison operator (``eq`` or ``ne``). Default is an empty string.
        other : str, optional
            The value to compare against.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value satisfies the operator comparison with `other`,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and comparison fails due to invalid input.
        """
        value = get_value(data, key)
        result = OpValidation.compare(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_version(cls, data, key='', op='', other='', on_exception=True):
        """
        Compare a version string against another using relational operators.

        This method acts as the `compare_version` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and applies a semantic version comparison using the specified operator.

        Supported operators
        -------------------
        - ``lt`` : less than
        - ``le`` : less than or equal to
        - ``gt`` : greater than
        - ``ge`` : greater than or equal to
        - ``eq`` : equal to
        - ``ne`` : not equal to

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose version string should be compared. Default is an empty string.
        op : str, optional
            The comparison operator (e.g., ``lt``, ``gt``, ``eq``). Default is an empty string.
        other : str, optional
            The version string to compare against (e.g., "1.2.3").
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the version satisfies the operator comparison with `other`,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and comparison fails due to invalid input.
        """
        value = get_value(data, key)
        result = VersionValidation.compare_version(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_semantic_version(cls, data, key='', op='', other='', on_exception=True):
        """
        Compare a semantic version string against another using relational operators.

        This method acts as the `compare_semantic_version` keyword for expression
        validation. It retrieves the value associated with the given key from a
        dictionary-like object and applies a semantic version comparison using
        the specified operator. Semantic versions are expected to follow the
        standard dot-separated format (e.g., "MAJOR.MINOR.PATCH").

        Supported operators
        -------------------
        - ``lt`` : less than
        - ``le`` : less than or equal to
        - ``gt`` : greater than
        - ``ge`` : greater than or equal to
        - ``eq`` : equal to
        - ``ne`` : not equal to

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose semantic version string should be compared. Default is an empty string.
        op : str, optional
            The comparison operator (e.g., ``lt``, ``gt``, ``eq``). Default is an empty string.
        other : str, optional
            The semantic version string to compare against (e.g., "2.1.0").
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the semantic version satisfies the operator comparison with `other`,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and comparison fails due to invalid input or malformed version.
        """
        value = get_value(data, key)
        result = VersionValidation.compare_semantic_version(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def compare_datetime(cls, data, key='', op='', other='', on_exception=True):
        """
        Compare a datetime value against another using relational operators.

        This method acts as the `compare_datetime` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and applies a datetime comparison using the specified operator.

        Supported operators
        -------------------
        - ``lt`` : less than
        - ``le`` : less than or equal to
        - ``gt`` : greater than
        - ``ge`` : greater than or equal to
        - ``eq`` : equal to
        - ``ne`` : not equal to

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose datetime value should be compared. Default is an empty string.
        op : str, optional
            The comparison operator (e.g., ``lt``, ``gt``, ``eq``). Default is an empty string.
        other : str, optional
            The datetime value to compare against. Expected format is an ISO 8601 string
            (e.g., "2025-12-15T13:30:00").
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the datetime satisfies the operator comparison with `other`,
            otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and comparison fails due to invalid input or
            malformed datetime string.
        """
        value = get_value(data, key)
        result = DatetimeValidation.compare_datetime(
            value, op, other, on_exception=on_exception
        )
        return result

    @classmethod
    def contain(cls, data, key='', other='', on_exception=True):
        """
        Check whether a value contains a given substring or element.

        This method acts as the `contain` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and evaluates whether that value contains the specified `other`
        string or element.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be checked. Default is an empty string.
        other : str, optional
            The substring or element to check for within the value. Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value contains `other`, otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails due to invalid input.
        """
        value = get_value(data, key)
        result = OpValidation.contain(
            value, other, on_exception=on_exception
        )
        return result

    @classmethod
    def notcontain(cls, data, key='', other='', on_exception=True):
        """
        Check whether a value does *not* contain a given substring or element.

        This method acts as the `notcontain` (or `not_contain`) keyword for
        expression validation. It retrieves the value associated with the given
        key from a dictionary-like object and evaluates whether that value does
        **not** contain the specified `other` string or element.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be checked. Default is an empty string.
        other : str, optional
            The substring or element to check for absence within the value.
            Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value does not contain `other`, otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails due to invalid input.
        """
        value = get_value(data, key)
        result = OpValidation.contain(
            value, other, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def belong(cls, data, key='', other='', on_exception=True):
        """
        Check whether a value belongs to a given collection.

        This method acts as the `belong` keyword for expression validation.
        It retrieves the value associated with the given key from a dictionary-like
        object and evaluates whether that value is a member of the specified
        `other` collection (e.g., list, tuple, set, or string).

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be checked. Default is an empty string.
        other : str or iterable, optional
            The collection or string to check membership against. Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value belongs to `other`, otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails due to invalid input.
        """
        value = get_value(data, key)
        result = OpValidation.belong(
            value, other, on_exception=on_exception
        )
        return result

    @classmethod
    def notbelong(cls, data, key='', other='', on_exception=True):
        """
        Check whether a value does *not* belong to a given collection.

        This method acts as the `notbelong` (or `not_belong`) keyword for
        expression validation. It retrieves the value associated with the given
        key from a dictionary-like object and evaluates whether that value is
        **not** a member of the specified `other` collection (e.g., list, tuple,
        set, or string).

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance containing the data.
        key : str, optional
            The key whose value should be checked. Default is an empty string.
        other : str or iterable, optional
            The collection or string to check membership against. Default is an empty string.
        on_exception : bool, optional
            If True, raise an Exception when validation fails. If False,
            return False instead. Default is True.

        Returns
        -------
        bool
            True if the value does not belong to `other`, otherwise False.

        Raises
        ------
        PredicateParameterDataTypeError
            If `data` is not a dictionary.
        Exception
            If `on_exception=True` and validation fails due to invalid input.

        See Also
        --------
        Predicate.belong : Complementary method that checks if a value *does* belong to `other`.
        """
        value = get_value(data, key)
        result = OpValidation.belong(
            value, other, valid=False, on_exception=on_exception
        )
        return result

    @classmethod
    def true(cls, data, on_exception=True):     # noqa
        """
        Always return True, regardless of input.

        This method acts as the `true` keyword for expression validation.
        It ignores both the provided `data` and `on_exception` arguments
        and unconditionally returns True. This can be useful as a default
        predicate or when an unconditional truth value is required in
        validation logic.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance. Ignored by this method.
        on_exception : bool, optional
            Flag indicating whether to raise an exception on failure.
            Ignored by this method. Default is True.

        Returns
        -------
        bool
            Always returns True.

        Notes
        -----
        Both `data` and `on_exception` are ignored because this method
        unconditionally returns True.
        """
        return True

    @classmethod
    def false(cls, data, on_exception=True):    # noqa
        """
        Always return False, regardless of input.

        This method acts as the `false` keyword for expression validation.
        It ignores both the provided `data` and `on_exception` arguments
        and unconditionally returns False. This can be useful as a default
        predicate or when an unconditional false value is required in
        validation logic.

        Parameters
        ----------
        data : dict
            A dictionary or dict-like instance. Ignored by this method.
        on_exception : bool, optional
            Flag indicating whether to raise an exception on failure.
            Ignored by this method. Default is True.

        Returns
        -------
        bool
            Always returns False.

        Notes
        -----
        Both `data` and `on_exception` are ignored because this method
        unconditionally returns False.
        """
        return False
