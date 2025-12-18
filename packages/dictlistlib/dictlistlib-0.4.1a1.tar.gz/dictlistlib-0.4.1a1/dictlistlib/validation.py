"""
Validation Utilities Module
===========================

This module provides a comprehensive set of utilities for validating,
parsing, and comparing different types of data. It centralizes common
validation logic for IP addresses, network interfaces, operators,
regular expressions, custom keywords, versions, and datetime values.

Features
--------
- **IP Address Validation**
  - Parse and validate IPv4/IPv6 addresses and prefixes.
  - Handle exceptions gracefully or raise them explicitly.

- **Network Interface Validation**
  - Verify interface names against expected patterns (e.g., Ethernet,
    Loopback, PortChannel).

- **Exception Handling**
  - Utility to raise or suppress exceptions based on configuration.

- **Regex Validation**
  - Match values against regular expressions with configurable error
    handling.

- **Operator Validation**
  - Compare numbers and values using operators.
  - Check containment and membership relationships.

- **Custom Validation**
  - Validate IP/MAC addresses, interface types, booleans, emptiness,
    and date/time formats.
  - Support for optional empty values and keyword-based checks.

- **Version Validation**
  - Compare software versions and semantic versions using operators.

- **Datetime Validation**
  - Parse and compare datetime values.
  - Support ISO formats, custom parsing options, and timezone handling.

Classes
-------
- RegexValidation : Provides regex-based validation.
- OpValidation : Handles operator-based comparisons.
- CustomValidation : Implements keyword-based validation (IP, MAC,
  interfaces, booleans, dates).
- VersionValidation : Compares versions and semantic versions.
- DatetimeResult : Stores results of custom datetime parsing.
- DatetimeValidation : Provides datetime parsing and comparison logic.

Exceptions
----------
- ValidationIpv6PrefixError : Raised for invalid IPv6 prefix validation.
- ValidationOperatorError : Raised for invalid operator usage.
- ParsedTimezoneError : Raised for invalid timezone parsing.

Logging
-------
A logger is provided (`logger`) for debugging and tracing validation
operations. Debugging can be enabled by setting `DEBUG = 1`.

"""

import operator
import re
from ipaddress import ip_address
# import functools
import traceback
import logging
from datetime import datetime
from compare_versions.core import verify_list as version_compare
from dateutil.parser import parse
from dateutil.parser import isoparse
from dateutil.tz import gettz
from dateutil.tz import UTC

from dictlistlib.exceptions import ValidationIpv6PrefixError
from dictlistlib.exceptions import ValidationOperatorError
from dictlistlib.exceptions import ParsedTimezoneError


DEBUG = 0
logger = logging.getLogger(__file__)


def get_ip_address(addr, is_prefix=False, on_exception=True):
    """
    Parse and validate an IP address string.

    This function attempts to convert the given string into an
    `ipaddress.IPv4Address` or `ipaddress.IPv6Address` object. It can
    optionally handle prefix notation (e.g., "192.168.1.1/24") and
    provides configurable exception handling.

    Parameters
    ----------
    addr : str
        The IP address string to parse. Can be IPv4 or IPv6, and may
        include a prefix if `is_prefix=True`.
    is_prefix : bool, optional
        If True, the function expects the input to include a prefix
        (e.g., "2001:db8::/64") and returns both the address and prefix.
        Default is False.
    on_exception : bool, optional
        If True, raises an exception when parsing fails.
        If False, returns None instead. Default is True.

    Returns
    -------
    ipaddress.IPv4Address or ipaddress.IPv6Address
        A validated IP address object if parsing succeeds.
    tuple
        If `is_prefix=True`, returns a tuple of (IPAddress, prefix length).
    None
        Returned if parsing fails and `on_exception=False`.

    Raises
    ------
    ValueError
        If the input is not a valid IP address and `on_exception=True`.
    ValidationIpv6PrefixError
        If an invalid IPv6 prefix is provided when `is_prefix=True`.
    """
    try:
        value, *grp = re.split(r'[/%]', str(addr).strip(), maxsplit=1)
        if grp:
            prefix = grp[0].strip()
            chk1 = not prefix.isdigit()
            chk2 = prefix.isdigit() and int(prefix) >= 128
            if chk1 or chk2:
                msg = '{} address containing invalid prefix.'.format(value)
                logger.warning(msg)
                raise ValidationIpv6PrefixError(msg)
        else:
            prefix = None

        if '.' in value:
            octets = value.split('.')
            if len(octets) == 4:
                if value.startswith('0'):
                    value = '.'.join(str(int(i, 8)) for i in octets)
                else:
                    len_chk = list(set(len(i) for i in octets)) == [2]
                    hex_chk = re.search(r'(?i)[a-f]', value)
                    if len_chk and hex_chk:
                        value = '.'.join(str(int(i, 16)) for i in octets)
        ip_addr = ip_address(str(value))
        return (ip_addr, prefix) if is_prefix else ip_addr
    except Exception as ex:  # noqa
        if on_exception:
            raise ex
        return (None, None) if is_prefix else None


def validate_interface(iface_name, pattern='', valid=True, on_exception=True):
    """
    Validate whether a given string represents a valid network interface name.

    This function checks if the provided interface name matches expected
    naming conventions (e.g., Ethernet, Loopback, PortChannel). An optional
    sub-pattern can be supplied to further restrict validation. Behavior on
    failure can be controlled by the `valid` and `on_exception` flags.

    Parameters
    ----------
    iface_name : str
        The network interface name to validate (e.g., "GigabitEthernet0/1").
    pattern : str, optional
        A sub-pattern to match within the interface name. Default is an empty
        string, meaning no additional restriction.
    valid : bool, optional
        Expected validation outcome. If True (default), the function checks
        that the interface name is valid. If False, it checks that the name
        is invalid.
    on_exception : bool, optional
        If True, raises an exception when validation fails.
        If False, returns False instead. Default is True.

    Returns
    -------
    bool
        True if the interface name matches the expected pattern and validity
        rules, False otherwise.

    Raises
    ------
    ValueError
        If the interface name does not match the expected pattern and
        `on_exception=True`.

    Notes
    -----
    - Common interface types include:
        * Loopback
        * FastEthernet
        * GigabitEthernet
        * TenGigabitEthernet
        * HundredGigabitEthernet
        * PortChannel / Bundle-Ether
    - The `pattern` argument allows fine-grained matching (e.g., enforcing
      "GigabitEthernet" only).
    """
    iface_name = str(iface_name)

    if iface_name.upper() == '__EXCEPTION__':
        return False

    try:
        pattern = r'\b' + pattern + r' *[0-9]+(/[0-9]+)?([.][0-9]+)?\b'
        result = bool(re.match(pattern, iface_name, re.I))
        return result if valid else not result
    except Exception as ex:
        result = raise_exception_if(ex, on_exception=on_exception)
        return result


# def false_on_exception_for_classmethod(func):
#     """Wrap the classmethod and return False on exception.
#
#     Parameters
#     ----------
#     func (function): a callable function
#
#     Notes
#     -----
#     DO NOT nest this decorator.
#     """
#     @functools.wraps(func)
#     def wrapper_func(*args, **kwargs):
#         """A Wrapper Function"""
#         chk = str(args[1]).upper()
#         if chk == '__EXCEPTION__':
#             return False
#         try:
#             result = func(*args, **kwargs)
#             return result if kwargs.get('valid', True) else not result
#         except Exception as ex:
#             if DEBUG:
#                 traceback.print_exc()
#             else:
#                 msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
#                 logger.warning(msg)
#             is_called_exception = kwargs.get('on_exception', False)
#             if is_called_exception:
#                 raise ex
#             else:
#                 return False if kwargs.get('valid', True) else True
#     return wrapper_func


def raise_exception_if(ex, on_exception=True):
    """
    Conditionally raise an exception or suppress it.

    This utility function provides a consistent way to handle exceptions
    based on the `on_exception` flag. If `on_exception=True`, the given
    exception is raised immediately. If `on_exception=False`, the function
    suppresses the exception and returns False instead.

    Parameters
    ----------
    ex : Exception
        The exception instance to raise if required.
    on_exception : bool, optional
        Controls whether the exception should be raised.
        - True (default): raise the provided exception.
        - False: suppress the exception and return False.

    Returns
    -------
    bool
        Returns False if `on_exception=False`. No value is returned if
        the exception is raised.

    Raises
    ------
    Exception
        The provided exception `ex` is raised if `on_exception=True`.

    Notes
    -----
    - This function is typically used in validation routines where
      exception handling behavior should be configurable.
    - It allows switching between strict validation (raise) and
      permissive validation (suppress).
    """
    if DEBUG:
        traceback.print_exc()
    else:
        msg = 'Warning *** {}: {}'.format(type(ex).__name__, ex)
        logger.warning(msg)
    if on_exception:
        raise ex
    return False


class RegexValidation:
    """
    A utility class for validating values against regular expressions.

    The `RegexValidation` class provides methods to check whether a given
    string matches a specified regex pattern. It supports configurable
    validation outcomes and exception handling, making it useful for
    flexible input validation scenarios.

    Methods
    -------
    match(pattern, value, valid=True, on_exception=True) -> bool
        Test whether `value` matches the given regex `pattern`.
        - If `valid=True`, returns True when the value matches.
        - If `valid=False`, returns True when the value does *not* match.
        - If `on_exception=True`, raises an exception on invalid input.
          Otherwise, returns False.

    Notes
    -----
    - Useful for validating structured strings such as email addresses,
      phone numbers, or custom identifiers.
    - The `valid` flag allows inversion of the check (e.g., ensuring a
      value does *not* match a pattern).
    - The `on_exception` flag controls whether errors are raised or
      suppressed.
    """
    @classmethod
    def match(cls, pattern, value, valid=True, on_exception=True):
        """
        Test whether a given value matches a regular expression pattern.

        This method applies the provided regex `pattern` to the input `value`
        and evaluates the result based on the `valid` flag. It supports
        configurable exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        pattern : str
            A regular expression pattern to match against.
        value : str
            The input string to validate.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the value matches the pattern.
            - If False, returns True when the value does *not* match.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when the regex is invalid or
              matching fails unexpectedly.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined
            by `valid`. False otherwise.

        Raises
        ------
        re.error
            If the regex pattern is invalid and `on_exception=True`.
        ValueError
            If validation fails and `on_exception=True`.

        Notes
        -----
        - This method is useful for validating structured strings such as
          identifiers, usernames, or formatted input.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value does *not* match a pattern).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = bool(re.match(pattern, str(value)))
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class OpValidation:
    """
    A utility class for validating values using comparison and membership operators.

    The `OpValidation` class provides methods to perform operator-based
    validation on numbers, strings, and collections. It supports configurable
    validation outcomes and exception handling, making it useful for flexible
    rule enforcement in data validation pipelines.

    Methods
    -------
    compare_number(value, op, other, valid=True, on_exception=True) -> bool
        Compare two numeric values using the given operator (e.g., >, <, ==).
    compare(value, op, other, valid=True, on_exception=True) -> bool
        Compare two values (numeric or non-numeric) using the given operator.
    contain(value, other, valid=True, on_exception=True) -> bool
        Check whether `other` is contained within `value` (e.g., substring or element).
    belong(value, other, valid=True, on_exception=True) -> bool
        Check whether `value` belongs to `other` (e.g., membership in a list or set).

    Parameters (shared across methods)
    ----------
    value : Any
        The primary value to validate.
    op : str
        The operator to apply (e.g., "==", "!=", ">", "<", ">=", "<=").
    other : Any
        The secondary value to compare against.
    valid : bool, optional
        Expected validation outcome. Default is True.
        - If True, returns True when the operator condition is satisfied.
        - If False, returns True when the operator condition is *not* satisfied.
    on_exception : bool, optional
        Controls exception behavior. Default is True.
        - If True, raises an exception when validation fails or operator is invalid.
        - If False, suppresses exceptions and returns False.

    Returns
    -------
    bool
        True if the validation outcome matches the expectation defined by `valid`.
        False otherwise.

    Raises
    ------
    ValidationOperatorError
        If an invalid operator is provided and `on_exception=True`.
    ValueError
        If comparison fails unexpectedly and `on_exception=True`.

    Notes
    -----
    - Provides a consistent interface for operator-based validation.
    - Useful for enforcing rules such as "value must be greater than X"
      or "item must belong to a given set".
    - The `valid` flag allows inversion of checks for negative validation cases.
    """
    @classmethod
    def compare_number(cls, value, op, other, valid=True, on_exception=True):
        """
        Compare two numeric values using a specified operator.

        This method evaluates whether the given `value` satisfies the comparison
        against `other` using the provided operator. It supports both symbolic
        (e.g., `<`, `>=`, `==`) and textual (e.g., `lt`, `ge`, `eq`) operator
        representations. Validation outcome and exception handling can be
        configured via the `valid` and `on_exception` flags.

        Parameters
        ----------
        value : int or float
            The primary numeric value to validate.
        op : str
            The comparison operator. Supported values include:
            - Textual: ``lt``, ``le``, ``gt``, ``ge``, ``eq``, ``ne``
            - Symbolic: ``<``, ``<=``, ``>``, ``>=``, ``==``, ``!=``
        other : int or float
            The secondary numeric value to compare against.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the comparison condition is satisfied.
            - If False, returns True when the comparison condition is *not* satisfied.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when an invalid operator is provided
              or comparison fails unexpectedly.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the comparison outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValidationOperatorError
            If an unsupported operator is provided and `on_exception=True`.
        ValueError
            If comparison fails unexpectedly and `on_exception=True`.

        Notes
        -----
        - Both `value` and `other` must be numeric types (int or float).
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value does *not* satisfy the operator condition).
        - This method is useful for enforcing numeric rules such as
          "value must be greater than X" or "value must not equal Y".
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating number.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            v, o = str(value).lower(), str(other).lower()
            value = True if v == 'true' else False if v == 'false' else value
            other = True if o == 'true' else False if o == 'false' else other
            num = float(other)
            value = float(value)
            result = getattr(operator, op)(value, num)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def compare(cls, value, op, other, valid=True, on_exception=True):
        """
        Compare two string values using equality or inequality operators.

        This method evaluates whether the given `value` satisfies the comparison
        against `other` using the specified operator. It supports both symbolic
        (``==``, ``!=``) and textual (``eq``, ``ne``) operator representations.
        Validation outcome and exception handling can be configured via the
        `valid` and `on_exception` flags.

        Parameters
        ----------
        value : str
            The primary string value to validate.
        op : str
            The comparison operator. Supported values include:
            - Textual: ``eq`` (equal), ``ne`` (not equal)
            - Symbolic: ``==`` (equal), ``!=`` (not equal)
        other : str
            The secondary string value to compare against.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the comparison condition is satisfied.
            - If False, returns True when the comparison condition is *not* satisfied.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when an invalid operator is provided
              or comparison fails unexpectedly.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the comparison outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValidationOperatorError
            If an unsupported operator is provided and `on_exception=True`.
        ValueError
            If comparison fails unexpectedly and `on_exception=True`.

        Notes
        -----
        - This method is intended for string equality/inequality checks only.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          two values are *not* equal).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            op = str(op).lower().strip()
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('eq', 'ne')
            if op not in valid_ops:
                fmt = ('Invalid {!r} operator for checking equal '
                       'or via versa.  It MUST be {}.')
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            result = getattr(operator, op)(value, other)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def contain(cls, value, other, valid=True, on_exception=True):
        """
        Check whether a given value contains another value.

        This method evaluates whether the string `value` contains the substring
        `other`. It supports configurable validation outcomes and exception
        handling, allowing either strict validation (raise on failure) or
        permissive validation (return False).

        Parameters
        ----------
        value : str
            The primary string to search within.
        other : str
            The substring to check for inside `value`.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` contains `other`.
            - If False, returns True when `value` does *not* contain `other`.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails unexpectedly.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the containment check matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If containment validation fails and `on_exception=True`.

        Notes
        -----
        - This method is intended for substring checks in strings.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a substring is *not* present).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = operator.contains(value, other)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def belong(cls, value, other, valid=True, on_exception=True):
        """
        Check whether a given value belongs to another collection or container.

        This method evaluates whether `value` is a member of `other`. It supports
        configurable validation outcomes and exception handling, allowing either
        strict validation (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        value : Any
            The item to check for membership (e.g., a string, number, or object).
        other : Iterable
            The container or collection to check against (e.g., list, set, tuple, dict keys).
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` belongs to `other`.
            - If False, returns True when `value` does *not* belong to `other`.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when membership validation fails unexpectedly.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the membership check matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If membership validation fails and `on_exception=True`.

        Notes
        -----
        - This method is intended for membership checks in collections such as
          lists, sets, tuples, or dictionary keys.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value is *not* present in the collection).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            result = operator.contains(other, value)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class CustomValidation:
    """
    A utility class for performing keyword-based validation checks.

    The `CustomValidation` class provides a wide range of specialized
    validation methods for common data types and patterns, including
    IP addresses, MAC addresses, network interfaces, boolean values,
    and date/time formats. Each method supports configurable validation
    outcomes and exception handling, making it suitable for flexible
    rule enforcement in data validation pipelines.

    Methods
    -------
    validate(case, value, valid=True, on_exception=True) -> bool
        Dispatch validation based on a keyword case (e.g., "ip", "date").
    is_ip_address(addr, valid=True, on_exception=True) -> bool
        Check whether the given address is a valid IPv4 or IPv6 address.
    is_ipv4_address(addr, valid=True, on_exception=True) -> bool
        Validate that the given address is a valid IPv4 address.
    is_ipv6_address(addr, valid=True, on_exception=True) -> bool
        Validate that the given address is a valid IPv6 address.
    is_mac_address(addr, valid=True, on_exception=True) -> bool
        Validate that the given address is a valid MAC address.
    is_loopback_interface(iface_name, valid=True, on_exception=True) -> bool
        Check whether the interface name represents a loopback interface.
    is_bundle_ether(iface_name, valid=True, on_exception=True) -> bool
        Check whether the interface name represents a Bundle-Ether interface.
    is_port_channel_interface(iface_name, valid=True, on_exception=True) -> bool
        Check whether the interface name represents a PortChannel interface.
    is_hundred_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
        Validate HundredGigabitEthernet interface names.
    is_ten_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
        Validate TenGigabitEthernet interface names.
    is_gigabit_ethernet(iface_name, valid=True, on_exception=True) -> bool
        Validate GigabitEthernet interface names.
    is_fast_ethernet(iface_name, valid=True, on_exception=True) -> bool
        Validate FastEthernet interface names.
    is_empty(value, valid=True, on_exception=True) -> bool
        Check whether the given value is empty.
    is_optional_empty(value, valid=True, on_exception=True) -> bool
        Check whether the given value is empty or optional.
    is_true(value, valid=True, on_exception=True) -> bool
        Validate that the given value represents a boolean True.
    is_false(value, valid=True, on_exception=True) -> bool
        Validate that the given value represents a boolean False.
    is_date(value, valid=True, on_exception=True) -> bool
        Validate that the given value is a valid date.
    is_datetime(value, valid=True, on_exception=True) -> bool
        Validate that the given value is a valid datetime.
    is_time(value, valid=True, on_exception=True) -> bool
        Validate that the given value is a valid time.
    is_isodate(value, valid=True, on_exception=True) -> bool
        Validate that the given value is a valid ISO 8601 date.

    Raises
    ------
    ValueError
        If validation fails unexpectedly and `on_exception=True`.
    ValidationIpv6PrefixError
        For invalid IPv6 prefix validation.
    ParsedTimezoneError
        For invalid timezone parsing in date/time validation.

    Notes
    -----
    - Provides a unified interface for diverse validation checks.
    - Useful for enforcing rules in networking, configuration, and data parsing.
    - The `valid` flag allows inversion of checks for negative validation cases.
    """

    @classmethod
    def validate(cls, case, value, valid=True, on_exception=True):
        """
        Dispatch and execute a custom validation method by keyword.

        This method dynamically looks up and invokes a corresponding
        `CustomValidation` classmethod based on the provided `case`
        keyword. It supports configurable validation outcomes and
        exception handling, allowing either strict validation (raise
        on failure) or permissive validation (return False).

        Parameters
        ----------
        case : str
            The custom validation keyword that maps to a classmethod
            (e.g., "is_ip_address", "is_date", "is_mac_address").
        value : Any
            The input data to validate (string, number, or object depending
            on the chosen validation method).
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the validation condition is satisfied.
            - If False, returns True when the validation condition is *not* satisfied.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when the validation method fails
              or the keyword does not exist.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        NotImplementedError
            If the specified `case` keyword does not correspond to an existing
            validation method.
        ValueError
            If validation fails unexpectedly and `on_exception=True`.

        Notes
        -----
        - This method acts as a dispatcher for keyword-based validation.
        - Useful when validation type is determined dynamically at runtime.
        - The `valid` flag allows inversion of checks for negative validation cases.
        """
        case = str(case).lower()
        name = 'is_{}'.format(case)
        method = getattr(cls, name, None)
        if callable(method):
            return method(value, valid=valid, on_exception=on_exception)
        else:
            msg = 'Need to implement this case {}'.format(case)
            raise NotImplementedError(msg)

    @classmethod
    def is_ip_address(cls, addr, valid=True, on_exception=True):
        """
        Validate whether a given string is a valid IP address.

        This method checks if the provided `addr` is a valid IPv4 or IPv6
        address. It supports configurable validation outcomes and exception
        handling, allowing either strict validation (raise on failure) or
        permissive validation (return False).

        Parameters
        ----------
        addr : str
            The input string to validate as an IP address.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `addr` is a valid IP address.
            - If False, returns True when `addr` is *not* a valid IP address.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined
            by `valid`. False otherwise.

        Raises
        ------
        ValueError
            If `addr` is not a valid IP address and `on_exception=True`.

        Notes
        -----
        - Supports both IPv4 and IPv6 address formats.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value is *not* a valid IP address).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr else False
            if not chk:
                logger.info('{!r} is not an IP address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_ipv4_address(cls, addr, valid=True, on_exception=True):
        """
        Validate whether a given string is a valid IPv4 address.

        This method checks if the provided `addr` conforms to the IPv4
        address format (e.g., "192.168.0.1"). It supports configurable
        validation outcomes and exception handling, allowing either strict
        validation (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        addr : str
            The input string to validate as an IPv4 address.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `addr` is a valid IPv4 address.
            - If False, returns True when `addr` is *not* a valid IPv4 address.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined
            by `valid`. False otherwise.

        Raises
        ------
        ValueError
            If `addr` is not a valid IPv4 address and `on_exception=True`.

        Notes
        -----
        - IPv4 addresses consist of four decimal octets separated by dots,
          each ranging from 0 to 255 (e.g., "10.0.0.1").
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value is *not* a valid IPv4 address).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr and ip_addr.version == 4 else False   # noqa
            if not chk:
                logger.info('{!r} is not an IPv4 address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_ipv6_address(cls, addr, valid=True, on_exception=True):
        """
        Validate whether a given string is a valid IPv6 address.

        This method checks if the provided `addr` conforms to the IPv6
        address format (e.g., "2001:db8::1"). It supports configurable
        validation outcomes and exception handling, allowing either strict
        validation (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        addr : str
            The input string to validate as an IPv6 address.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `addr` is a valid IPv6 address.
            - If False, returns True when `addr` is *not* a valid IPv6 address.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined
            by `valid`. False otherwise.

        Raises
        ------
        ValueError
            If `addr` is not a valid IPv6 address and `on_exception=True`.

        Notes
        -----
        - IPv6 addresses are represented as eight groups of four hexadecimal
          digits separated by colons, with support for shorthand notation
          (e.g., "::1" for loopback).
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value is *not* a valid IPv6 address).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            ip_addr = get_ip_address(addr, on_exception=on_exception)
            chk = True if ip_addr and ip_addr.version == 6 else False   # noqa
            if not chk:
                logger.info('{!r} is not an IPv6 address.'.format(addr))
            return chk if valid else not chk
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result if valid else not result

    @classmethod
    def is_mac_address(cls, addr, valid=True, on_exception=True):
        """
        Validate whether a given string is a valid MAC address.

        This method checks if the provided `addr` conforms to the standard
        MAC address format. It supports configurable validation outcomes
        and exception handling, allowing either strict validation (raise on
        failure) or permissive validation (return False).

        Parameters
        ----------
        addr : str
            The input string to validate as a MAC address. Supported formats include:
            - Colon-separated (e.g., "00:1A:2B:3C:4D:5E")
            - Hyphen-separated (e.g., "00-1A-2B-3C-4D-5E")
            - Continuous hex string (e.g., "001A2B3C4D5E")
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `addr` is a valid MAC address.
            - If False, returns True when `addr` is *not* a valid MAC address.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined
            by `valid`. False otherwise.

        Raises
        ------
        ValueError
            If `addr` is not a valid MAC address and `on_exception=True`.

        Notes
        -----
        - A MAC address consists of 12 hexadecimal digits (0–9, A–F).
        - Common formats include colon-separated, hyphen-separated, or
          continuous hex strings.
        - The `valid` flag allows inversion of the check (e.g., ensuring
          a value is *not* a valid MAC address).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(addr).upper() == '__EXCEPTION__':
            return False

        try:
            addr = str(addr)
            patterns = [
                r'\b[0-9a-f]{2}([-: ])([0-9a-f]{2}\1){4}[0-9a-f]{2}\b',
                r'\b[a-f0-9]{4}[.][a-f0-9]{4}[.][a-f0-9]{4}\b'
            ]
            for pattern in patterns:
                result = re.match(pattern, addr, re.I)
                if result:
                    return True if valid else False
            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    # @classmethod
    # def is_network_interface(cls, iface_name, valid=True, on_exception=True):
    #     """Verify a provided data is a network interface.
    #
    #     Parameters
    #     ----------
    #     iface_name (str): a network interface
    #     valid (bool): check for a valid result.  Default is True.
    #     on_exception (bool): raise Exception if it is True, otherwise, return None.
    #
    #     Returns
    #     -------
    #     bool: True if iface_name is a network interface, otherwise, False.
    #     """
    #     pattern = r'[a-z]+(-?[a-z0-9]+)?'
    #     result = validate_interface(iface_name, pattern=pattern,
    #                                 valid=valid, on_exception=on_exception)
    #     return result

    @classmethod
    def is_loopback_interface(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a loopback interface.

        This method checks if the provided `iface_name` corresponds to a loopback
        interface (commonly named "Loopback" followed by an index, e.g., "Loopback0").
        It supports configurable validation outcomes and exception handling, allowing
        either strict validation (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "Loopback0").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a loopback interface.
            - If False, returns True when `iface_name` is *not* a loopback interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a loopback interface and `on_exception=True`.

        Notes
        -----
        - Loopback interfaces are virtual interfaces used primarily for testing,
          diagnostics, and management purposes.
        - Typical naming convention: "Loopback" followed by a numeric identifier
          (e.g., "Loopback0", "Loopback1").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a loopback interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = r'lo(opback)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_bundle_ethernet(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a Bundle-Ethernet interface.

        This method checks if the provided `iface_name` follows the naming convention
        for a Bundle-Ethernet interface (commonly used in link aggregation or port
        channel configurations, e.g., "Bundle-Ether1"). It supports configurable
        validation outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "Bundle-Ether1").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a Bundle-Ethernet interface.
            - If False, returns True when `iface_name` is *not* a Bundle-Ethernet interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a Bundle-Ethernet interface and `on_exception=True`.

        Notes
        -----
        - Bundle-Ethernet interfaces are logical interfaces that aggregate multiple
          physical links into a single logical channel for redundancy and load balancing.
        - Typical naming convention: "Bundle-Ether" followed by a numeric identifier
          (e.g., "Bundle-Ether1", "Bundle-Ether10").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a Bundle-Ethernet interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = r'bundle-ether|be'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_port_channel(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a Port-Channel interface.

        This method checks if the provided `iface_name` follows the naming convention
        for a Port-Channel interface (commonly used in link aggregation, e.g.,
        "Port-Channel1"). It supports configurable validation outcomes and exception
        handling, allowing either strict validation (raise on failure) or permissive
        validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "Port-Channel1").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a Port-Channel interface.
            - If False, returns True when `iface_name` is *not* a Port-Channel interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a Port-Channel interface and `on_exception=True`.

        Notes
        -----
        - Port-Channel interfaces are logical interfaces that aggregate multiple
          physical links into a single logical channel for redundancy and load balancing.
        - Typical naming convention: "Port-Channel" followed by a numeric identifier
          (e.g., "Port-Channel1", "Port-Channel10").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a Port-Channel interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = r'po(rt-channel)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_hundred_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a HundredGigabitEthernet interface.

        This method checks if the provided `iface_name` follows the naming convention
        for HundredGigabitEthernet interfaces (e.g., "HundredGigE1/0/0"). It supports
        configurable validation outcomes and exception handling, allowing either strict
        validation (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "HundredGigE1/0/0").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a HundredGigabitEthernet interface.
            - If False, returns True when `iface_name` is *not* a HundredGigabitEthernet interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a HundredGigabitEthernet interface and `on_exception=True`.

        Notes
        -----
        - HundredGigabitEthernet interfaces are high-speed network interfaces
          typically used in backbone or data center environments.
        - Typical naming convention: "HundredGigE" followed by slot/port identifiers
          (e.g., "HundredGigE0/0/0").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a HundredGigabitEthernet interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = 'Hu(ndredGigE)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_ten_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a TenGigabitEthernet interface.

        This method checks if the provided `iface_name` follows the naming convention
        for TenGigabitEthernet interfaces (e.g., "TenGigE0/1/0"). It supports configurable
        validation outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "TenGigE0/1/0").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a TenGigabitEthernet interface.
            - If False, returns True when `iface_name` is *not* a TenGigabitEthernet interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a TenGigabitEthernet interface and `on_exception=True`.

        Notes
        -----
        - TenGigabitEthernet interfaces are high-speed network interfaces commonly
          used in enterprise and data center environments.
        - Typical naming convention: "TenGigE" or "TenGigabitEthernet" followed by
          slot/port identifiers (e.g., "TenGigE0/0/1").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a TenGigabitEthernet interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = 'Te(nGigE)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_gigabit_ethernet(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a GigabitEthernet interface.

        This method checks if the provided `iface_name` follows the naming convention
        for GigabitEthernet interfaces (e.g., "GigabitEthernet0/1"). It supports configurable
        validation outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "GigabitEthernet0/1").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a GigabitEthernet interface.
            - If False, returns True when `iface_name` is *not* a GigabitEthernet interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a GigabitEthernet interface and `on_exception=True`.

        Notes
        -----
        - GigabitEthernet interfaces provide 1 Gbps network connectivity and are widely
          used in enterprise and access networks.
        - Typical naming convention: "GigabitEthernet" followed by slot/port identifiers
          (e.g., "GigabitEthernet0/0/1").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a GigabitEthernet interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = 'Gi(gabitEthernet)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_fast_ethernet(cls, iface_name, valid=True, on_exception=True):
        """
        Validate whether a given interface name represents a FastEthernet interface.

        This method checks if the provided `iface_name` follows the naming convention
        for FastEthernet interfaces (e.g., "FastEthernet0/1"). It supports configurable
        validation outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        iface_name : str
            The interface name to validate (e.g., "FastEthernet0/1").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `iface_name` is a FastEthernet interface.
            - If False, returns True when `iface_name` is *not* a FastEthernet interface.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `iface_name` is not a FastEthernet interface and `on_exception=True`.

        Notes
        -----
        - FastEthernet interfaces provide 100 Mbps network connectivity and were
          widely used in legacy enterprise and access networks.
        - Typical naming convention: "FastEthernet" followed by slot/port identifiers
          (e.g., "FastEthernet0/0/1").
        - The `valid` flag allows inversion of the check (e.g., ensuring a name
          is *not* a FastEthernet interface).
        - The `on_exception` flag provides flexibility in error handling.
        """
        pattern = r'fa(stethernet)?'
        result = validate_interface(iface_name, pattern=pattern,
                                    valid=valid, on_exception=on_exception)
        return result

    @classmethod
    def is_empty(cls, value, valid=True, on_exception=True):    # noqa
        """
        Validate whether a given string is empty.

        This method checks if the provided `value` is an empty string (`""`).
        It supports configurable validation outcomes and exception handling,
        allowing either strict validation (raise on failure) or permissive
        validation (return False).

        Parameters
        ----------
        value : str
            The string to validate.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is an empty string.
            - If False, returns True when `value` is *not* an empty string.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` does not meet the empty string condition and `on_exception=True`.

        Notes
        -----
        - This method only checks for exact emptiness (`""`), not whitespace-only strings.
        - The `valid` flag allows inversion of the check (e.g., ensuring a string
          is *not* empty).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value == ''
        return result if valid else not result

    @classmethod
    def is_optional_empty(cls, value, valid=True, on_exception=True):   # noqa
        """
        Validate whether a given string is empty or considered optional.

        This method checks if the provided `value` is either an empty string (`""`)
        or meets the criteria for being treated as "optional" (e.g., `None` or
        missing input depending on implementation). It supports configurable
        validation outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        value : str or None
            The string to validate. May also be `None` if treated as optional.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is empty or optional.
            - If False, returns True when `value` is *not* empty or optional.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` does not meet the optional empty condition and `on_exception=True`.

        Notes
        -----
        - This method differs from `is_empty` by allowing `None` or other optional
          representations to be treated as valid empty values.
        - The `valid` flag allows inversion of the check (e.g., ensuring a value
          is *not* empty or optional).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = bool(re.match(r'\s+$', value))
        return result if valid else not result

    @classmethod
    def is_true(cls, value, valid=True, on_exception=True):     # noqa
        """
        Validate whether a given value represents boolean True.

        This method checks if the provided `value` is logically equivalent
        to True. It supports both boolean values (`True`) and common string
        representations (e.g., "true", "yes", "1"). Validation outcome and
        exception handling can be configured via the `valid` and `on_exception`
        flags.

        Parameters
        ----------
        value : bool or str
            The input data to validate. Supported values include:
            - Boolean: ``True``
            - String equivalents: "true", "yes", "1" (case-insensitive)
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` represents True.
            - If False, returns True when `value` does *not* represent True.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` does not meet the True condition and `on_exception=True`.

        Notes
        -----
        - String comparisons are case-insensitive (e.g., "TRUE" and "true" are valid).
        - Numeric string "1" may also be treated as True depending on implementation.
        - The `valid` flag allows inversion of the check (e.g., ensuring a value
          is *not* True).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value.lower() == 'true'
        return result if valid else not result

    @classmethod
    def is_false(cls, value, valid=True, on_exception=True):    # noqa
        """
        Validate whether a given value represents boolean False.

        This method checks if the provided `value` is logically equivalent
        to False. It supports both boolean values (`False`) and common string
        representations (e.g., "false", "no", "0"). Validation outcome and
        exception handling can be configured via the `valid` and `on_exception`
        flags.

        Parameters
        ----------
        value : bool or str
            The input data to validate. Supported values include:
            - Boolean: ``False``
            - String equivalents: "false", "no", "0" (case-insensitive)
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` represents False.
            - If False, returns True when `value` does *not* represent False.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` does not meet the False condition and `on_exception=True`.

        Notes
        -----
        - String comparisons are case-insensitive (e.g., "FALSE" and "false" are valid).
        - Numeric string "0" may also be treated as False depending on implementation.
        - The `valid` flag allows inversion of the check (e.g., ensuring a value
          is *not* False).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        value = str(value)
        result = value.lower() == 'false'
        return result if valid else not result

    @classmethod
    def is_date(cls, value, valid=True, on_exception=True):
        """
        Validate whether a given string represents a valid date.

        This method checks if the provided `value` can be interpreted as a valid
        calendar date. It supports configurable validation outcomes and exception
        handling, allowing either strict validation (raise on failure) or permissive
        validation (return False).

        Parameters
        ----------
        value : str
            The input string to validate as a date (e.g., "2025-12-15", "15/12/2025").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is a valid date.
            - If False, returns True when `value` is *not* a valid date.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` is not a valid date and `on_exception=True`.

        Notes
        -----
        - Supported formats depend on the underlying implementation (commonly ISO 8601
          or locale-specific formats).
        - The `valid` flag allows inversion of the check (e.g., ensuring a string
          is *not* a valid date).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)

            if matched_time:
                return False if valid else True

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return True if valid else False

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return True if valid else False

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return True if valid else False

            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_datetime(cls, value, valid=True, on_exception=True):
        """
        Validate whether a given string represents a valid datetime.

        This method checks if the provided `value` can be interpreted as a valid
        datetime (date and time combination). It supports configurable validation
        outcomes and exception handling, allowing either strict validation (raise
        on failure) or permissive validation (return False).

        Parameters
        ----------
        value : str
            The input string to validate as a datetime (e.g., "2025-12-15 14:30:00",
            "15/12/2025 14:30").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is a valid datetime.
            - If False, returns True when `value` is *not* a valid datetime.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` is not a valid datetime and `on_exception=True`.

        Notes
        -----
        - Supported formats depend on the underlying implementation (commonly ISO 8601
          or locale-specific formats).
        - The `valid` flag allows inversion of the check (e.g., ensuring a string
          is *not* a valid datetime).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)

            if not matched_time:
                return False if valid else True

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return True if valid else False

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return True if valid else False

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return True if valid else False

            return False if valid else True
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_time(cls, value, valid=True, on_exception=True):
        """
        Validate whether a given string represents a valid time.

        This method checks if the provided `value` can be interpreted as a valid
        time of day. It supports configurable validation outcomes and exception
        handling, allowing either strict validation (raise on failure) or permissive
        validation (return False).

        Parameters
        ----------
        value : str
            The input string to validate as a time (e.g., "14:30:00", "02:45 PM").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is a valid time.
            - If False, returns True when `value` is *not* a valid time.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` is not a valid time and `on_exception=True`.

        Notes
        -----
        - Supported formats depend on the underlying implementation (commonly
          24-hour format "HH:MM[:SS]" or 12-hour format with AM/PM).
        - The `valid` flag allows inversion of the check (e.g., ensuring a string
          is *not* a valid time).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            parse(value, fuzzy=True)

            date_pattern = '[0-9]+([/-])[0-9]+\\1[0-9]+'
            matched_date = re.search(date_pattern, value)
            if matched_date:
                return False if valid else True

            month_names_pattern = """(?ix)jan(uary)?|
                                     feb(ruary)?|
                                     mar(ch)?|
                                     apr(il)?|
                                     may|
                                     june?|
                                     july?|
                                     aug(ust)?|
                                     sep(tember)?|
                                     oct(ober)?|
                                     nov(ember)?|
                                     dec(ember)?"""
            matched_month_names = re.search(month_names_pattern, value)
            if matched_month_names:
                return False if valid else True

            day_names_pattern = '(?i)(sun|mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?'
            matched_day_names = re.search(day_names_pattern, value)
            if matched_day_names:
                return False if valid else True

            time_pattern = '[0-9]+:[0-9]+'
            matched_time = re.search(time_pattern, value)
            result = bool(matched_time)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def is_isodate(cls, value, valid=True, on_exception=True):
        """
        Validate whether a given string represents a valid ISO 8601 date.

        This method checks if the provided `value` conforms to the ISO 8601
        date format (e.g., "YYYY-MM-DD"). It supports configurable validation
        outcomes and exception handling, allowing either strict validation
        (raise on failure) or permissive validation (return False).

        Parameters
        ----------
        value : str
            The input string to validate as an ISO 8601 date (e.g., "2025-12-15").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when `value` is a valid ISO date.
            - If False, returns True when `value` is *not* a valid ISO date.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when validation fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the validation outcome matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If `value` is not a valid ISO date and `on_exception=True`.

        Notes
        -----
        - ISO 8601 date format is typically `YYYY-MM-DD` (e.g., "2025-12-15").
        - Time and timezone components (e.g., "2025-12-15T00:00:00Z") are part of
          ISO 8601 datetime, not pure date validation.
        - The `valid` flag allows inversion of the check (e.g., ensuring a string
          is *not* a valid ISO date).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '':
                return False

            value = str(value).strip()
            isoparse(value)

            pattern = '[0-9]{4}((-[0-9]{2})|(-?W[0-9]{2}))$'
            match = re.match(pattern, value)
            if match:
                return True if valid else False

            pattern = ('[0-9]{4}('
                       '(-?[0-9]{2}-?[0-9]{2})|'
                       '(-?W[0-9]{2}-?[0-9])|'
                       '(-?[0-9]{3})'
                       ')')
            result = bool(re.match(pattern, value))
            return result if valid else False
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class VersionValidation:
    class VersionValidation:
        """
        A utility class for validating and comparing software version strings.

        This class provides methods to compare both generic version numbers
        and semantic versioning (SemVer) strings. It supports configurable
        validation outcomes and exception handling, allowing either strict
        validation (raise on failure) or permissive validation (return False).

        Methods
        -------
        compare_version(value, op, other, valid=True, on_exception=True) -> bool
            Compare two version strings using the specified operator.
            Examples of supported operators: "==", "!=", "<", "<=", ">", ">=".
            Returns True if the comparison result matches the expectation
            defined by `valid`, otherwise False.

        compare_semantic_version(value, op, other, valid=True, on_exception=True) -> bool
            Compare two semantic version strings (e.g., "1.2.3") using the
            specified operator. Supports major, minor, and patch comparisons
            according to semantic versioning rules.
            Returns True if the comparison result matches the expectation
            defined by `valid`, otherwise False.

        Notes
        -----
        - The `valid` flag allows inversion of the check (e.g., ensuring a
          comparison does *not* hold true).
        - The `on_exception` flag controls error handling:
            * If True, raises an exception on invalid input or comparison.
            * If False, suppresses exceptions and returns False.
        - Semantic versioning follows the format MAJOR.MINOR.PATCH, where:
            * MAJOR version increments indicate incompatible API changes.
            * MINOR version increments add functionality in a backward-compatible manner.
            * PATCH version increments include backward-compatible bug fixes.
        """
    @classmethod
    def compare_version(cls, value, op, other, valid=True, on_exception=True):
        """
        Compare two version strings using a specified operator.

        This method performs a comparison between two version strings (`value` and `other`)
        using the provided operator (`op`). It supports both symbolic operators
        ("<", "<=", ">", ">=", "==", "!=") and their textual equivalents
        ("lt", "le", "gt", "ge", "eq", "ne"). Validation outcome and exception
        handling can be configured via the `valid` and `on_exception` flags.

        Parameters
        ----------
        value : str
            The version string to validate and compare (e.g., "1.2.0").
        op : str
            The comparison operator. Supported values include:
            - Symbolic: "<", "<=", ">", ">=", "==", "!="
            - Textual: "lt", "le", "gt", "ge", "eq", "ne"
        other : str
            The version string to compare against (e.g., "1.3.0").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the comparison result is correct.
            - If False, returns True when the comparison result is *not* correct.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when comparison fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the comparison result matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If the operator is invalid or the version strings cannot be compared
            and `on_exception=True`.

        Notes
        -----
        - Versions are compared lexicographically or numerically depending on
          implementation (e.g., "1.10" > "1.2").
        - The `valid` flag allows inversion of the check (e.g., ensuring a comparison
          does *not* hold true).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating version.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            value, other = str(value), str(other)
            result = version_compare([value, other], comparison=op, scheme='string')
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result

    @classmethod
    def compare_semantic_version(cls, value, op, other, valid=True, on_exception=True):
        """
        Compare two semantic version strings using a specified operator.

        This method performs a comparison between two semantic version strings
        (`value` and `other`) according to semantic versioning (SemVer) rules.
        It supports both symbolic operators ("<", "<=", ">", ">=", "==", "!=")
        and their textual equivalents ("lt", "le", "gt", "ge", "eq", "ne").
        Validation outcome and exception handling can be configured via the
        `valid` and `on_exception` flags.

        Parameters
        ----------
        value : str
            The semantic version string to validate and compare (e.g., "1.2.3").
        op : str
            The comparison operator. Supported values include:
            - Symbolic: "<", "<=", ">", ">=", "==", "!="
            - Textual: "lt", "le", "gt", "ge", "eq", "ne"
        other : str
            The semantic version string to compare against (e.g., "1.3.0").
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the comparison result is correct.
            - If False, returns True when the comparison result is *not* correct.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when comparison fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the comparison result matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If the operator is invalid, the version strings are not valid semantic
            versions, or the comparison cannot be performed and `on_exception=True`.

        Notes
        -----
        - Semantic versioning follows the format MAJOR.MINOR.PATCH (e.g., "2.1.0").
        - Pre-release and build metadata (e.g., "1.0.0-alpha", "1.0.0+build.1")
          may also be supported depending on implementation.
        - The `valid` flag allows inversion of the check (e.g., ensuring a comparison
          does *not* hold true).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = str(op).lower().strip()
            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op
            valid_ops = ('lt', 'le', 'gt', 'ge', 'eq', 'ne')
            if op not in valid_ops:
                fmt = 'Invalid {!r} operator for validating version.  It MUST be {}.'
                raise ValidationOperatorError(fmt.format(op, valid_ops))

            value, other = str(value), str(other)
            result = version_compare([value, other], comparison=op, scheme='semver')
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result


class DatetimeResult:
    """
    Container for the result of parsing a custom datetime string.

    This class stores parsed datetime information along with optional
    metadata such as timezone, ISO formatting flags, and parsing preferences.
    It also provides helper methods for boolean conversion and timezone parsing.

    Attributes
    ----------
    data : str
        The original datetime string or parsed representation.
    timezone : dict, optional
        A dictionary representing the parsed timezone information.
        Typically includes Linux-style timezone identifiers such as
        "America/Los_Angeles". Default is None.
    iso : bool, optional
        Flag indicating whether the datetime string should be interpreted
        or formatted in ISO 8601 format. Default is None.
    dayfirst : bool, optional
        Flag indicating whether the day component should be parsed before
        the month (e.g., "15/12/2025" vs "12/15/2025"). Default is None.

    Methods
    -------
    to_bool(value, default=False) -> bool
        Convert a given value to a boolean. Returns `default` if conversion fails.
    parse_timezone() -> None
        Parse and normalize the timezone information stored in `timezone`.

    Raises
    ------
    ParsedTimezoneError
        Raised when timezone parsing fails or an invalid timezone is provided.

    Notes
    -----
    - This class is intended to encapsulate parsing results rather than
      perform full datetime validation.
    - The `iso` and `dayfirst` flags provide flexibility in handling
      different datetime formats and regional conventions.
    """
    def __init__(self, data='', timezone=None, iso=False,
                 dayfirst=True, fuzzy=True):
        self.data = data
        self.iso = self.to_bool(iso, default=False)
        self.dayfirst = self.to_bool(dayfirst, default=True)
        self.fuzzy = self.to_bool(fuzzy, default=True)
        self.timezone = timezone
        self.tzinfos = dict()
        self.parse_timezone()

    def to_bool(self, value, default=False):    # noqa
        """
        Convert a given value into a boolean.

        This method attempts to interpret the provided `value` as a boolean.
        It supports both native boolean values (`True`, `False`) and common
        string representations (e.g., "true", "false", "yes", "no", "1", "0").
        If the input is empty or cannot be interpreted, the `default` value
        is returned.

        Parameters
        ----------
        value : str or bool
            The input value to convert. Supported values include:
            - Boolean: ``True`` or ``False``
            - String equivalents (case-insensitive): "true", "false",
              "yes", "no", "1", "0"
        default : bool, optional
            The fallback value to return if `value` is empty or invalid.
            Default is False.

        Returns
        -------
        bool
            True if `value` represents a truthy value, False otherwise.
            Returns `default` if the input is empty or unrecognized.

        Notes
        -----
        - String comparisons are case-insensitive (e.g., "TRUE" and "true"
          are treated the same).
        - Numeric strings "1" and "0" are interpreted as True and False,
          respectively.
        - If `value` is None or an empty string, the `default` is returned.
        """
        if isinstance(value, bool):
            return value
        value = str(value).title()
        result = default if value == '' else value == 'True'
        return result

    def parse_timezone(self):
        """
        Parse and normalize timezone information to build `tzinfos`.

        This method processes the `timezone` attribute and constructs a dictionary
        of timezone mappings (`tzinfos`). The `timezone` attribute may be provided
        as either a dictionary or a string. If a string is supplied, it must follow
        the format `"TZNAME:OFFSET, TZNAME:OFFSET, ..."`, where each pair represents
        a timezone name and its corresponding offset or identifier.

        Behavior
        --------
        - If `timezone` is None or an empty string, the method returns without action.
        - If `timezone` is a dictionary, it is copied directly into `tzinfos`.
        - If `timezone` is a string:
            * Each entry must be separated by `", "`.
            * Each entry must contain a `":"` separating the name and value.
            * Values are first attempted to be parsed as integers (offsets).
            * If parsing as an integer fails, values are passed to `dateutil.tz.gettz`
              for resolution.
            * If resolution fails, a `ParsedTimezoneError` is raised.

        Raises
        ------
        ParsedTimezoneError
            - If `timezone` is not a dict or str.
            - If the string format is invalid (missing `:` or malformed).
            - If a timezone value cannot be parsed as either an integer offset
              or a valid timezone identifier.

        Attributes Modified
        -------------------
        tzinfos : dict
            A dictionary mapping timezone names to either integer offsets or
            `tzinfo` objects.
        """
        if self.timezone in [None, '']:
            return

        if not isinstance(self.timezone, (dict, str)):
            fmt = 'timezone must be an instance of dict or str, but {}'
            raise ParsedTimezoneError(fmt.format(type(self.timezone)))

        if self.timezone and isinstance(self.timezone, dict):
            self.tzinfos = dict(self.timezone)
            return

        for pair in self.timezone.split(', '):
            items = pair.split(':', maxsplit=1)
            if len(items) != 2:
                fmt = 'Invalid timezone format -- {!r}'
                raise ParsedTimezoneError(fmt.format(self.timezone))
            tzname, tzvalue = [item.strip() for item in items]

            try:
                self.tzinfos[tzname] = int(tzvalue)
            except Exception as ex:         # noqa
                try:
                    self.tzinfos[tzname] = gettz(tzvalue)
                except Exception as ex:     # noqa
                    fmt = 'Invalid timezone value -- {!r}'
                    raise ParsedTimezoneError(fmt.format(self.timezone))


class DatetimeValidation:
    """
    A utility class for validating and comparing datetime values.

    This class provides methods to parse datetime strings into Python
    `datetime` objects and perform comparisons between them using
    symbolic or textual operators. It supports configurable validation
    outcomes and exception handling, allowing either strict validation
    (raise on failure) or permissive validation (return False).

    Methods
    -------
    get_date(datetime_value, options) -> datetime.datetime
        Parse a datetime string into a `datetime` object.
        Options may include parsing preferences such as ISO format,
        day-first ordering, or timezone handling.

    do_datetime_compare(a_datetime, op, other_datetime) -> bool
        Compare two `datetime` objects using the specified operator.
        Supported operators include "<", "<=", ">", ">=", "==", "!="
        and their textual equivalents ("lt", "le", "gt", "ge", "eq", "ne").

    compare_datetime(value, op, other, valid=True, on_exception=True) -> bool
        Compare two datetime values (strings or objects) using the specified
        operator. Returns True if the comparison result matches the expectation
        defined by `valid`, otherwise False. Raises an exception if invalid input
        is provided and `on_exception=True`.

    Raises
    ------
    ValueError
        If datetime parsing fails, an invalid operator is provided, or comparison
        cannot be performed and `on_exception=True`.

    Notes
    -----
    - String inputs are parsed into `datetime` objects before comparison.
    - Supported formats depend on the underlying parser (commonly ISO 8601
      or locale-specific formats).
    - The `valid` flag allows inversion of the check (e.g., ensuring a comparison
      does *not* hold true).
    - The `on_exception` flag provides flexibility in error handling.
    """
    @classmethod
    def parse_custom_date(cls, data):
        """
        Parse a custom datetime string and return a `DatetimeResult` instance.

        This method interprets a datetime string that may include additional
        parsing options such as timezone, ISO formatting, day-first ordering,
        or fuzzy parsing. The result is encapsulated in a `DatetimeResult`
        object, which stores the parsed datetime along with metadata.

        Parameters
        ----------
        data : str
            A datetime string with optional parsing directives. Supported directives:
            - timezone=<tz>   : Specify a timezone (e.g., "America/Los_Angeles").
            - iso=<bool>      : Flag to enforce ISO 8601 parsing (e.g., "iso=True").
            - dayfirst=<bool> : Flag to interpret day before month (e.g., "dayfirst=True").
            - fuzzy=<bool>    : Flag to allow fuzzy parsing, ignoring unknown tokens.

            Example: "2025-12-15 14:30:00 timezone=America/Los_Angeles iso=True dayfirst=False"

        Returns
        -------
        DatetimeResult
            An object containing the parsed datetime and associated metadata
            (timezone, ISO flag, day-first flag, etc.).

        Raises
        ------
        ValueError
            If the input string cannot be parsed into a valid datetime.

        Notes
        -----
        - The parsing behavior depends on the underlying datetime parser
          (commonly `dateutil.parser`).
        - Fuzzy parsing allows ignoring extraneous text in the input string.
        - The returned `DatetimeResult` provides structured access to both
          the parsed datetime and parsing options.
        """
        pattern = '(?i) +(timezone|iso|dayfirst|fuzzy)='

        if not re.search(pattern, data):
            result = DatetimeResult(data=data)
            return result

        start = 0
        date_val, timezone, iso, dayfirst, fuzzy = [''] * 5
        match_data = ''
        m = None
        for m in re.finditer(pattern, data):
            before_match = m.string[start:m.start()]
            if not date_val:
                date_val = before_match.strip()
            elif not timezone and match_data.startswith('timezone='):
                timezone = before_match.strip()
            elif not iso and match_data.startswith('iso='):
                iso = before_match.strip()
            elif not iso and match_data.startswith('dayfirst='):
                dayfirst = before_match.strip()
            elif not fuzzy and match_data.startswith('fuzzy='):
                fuzzy = before_match.strip()
            match_data = m.group().strip()
            start = m.end()
        else:
            if m:
                if not timezone and match_data.startswith('timezone='):
                    timezone = m.string[m.end():].strip()
                elif not iso and match_data.startswith('iso='):
                    iso = m.string[m.end():].strip()
                elif not dayfirst and match_data.startswith('dayfirst='):
                    dayfirst = m.string[m.end():].strip()
                elif not fuzzy and match_data.startswith('fuzzy='):
                    fuzzy = m.string[m.end():].strip()

        result = DatetimeResult(data=date_val, timezone=timezone, iso=iso,
                                dayfirst=dayfirst, fuzzy=fuzzy)
        return result

    @classmethod
    def get_date(cls, datetime_value, options):
        """
        Parse a datetime string into a `datetime.datetime` instance.

        This method converts a raw datetime string into a Python `datetime`
        object, applying parsing options provided via a `DatetimeResult`
        instance. Options may include timezone handling, ISO formatting,
        day-first ordering, or fuzzy parsing.

        Parameters
        ----------
        datetime_value : str
            The datetime string to parse (e.g., "2025-12-15 14:30:00").
        options : DatetimeResult
            A `DatetimeResult` object containing parsing preferences such as:
            - timezone : dict or str
                Timezone information (e.g., "America/Los_Angeles").
            - iso : bool
                Flag to enforce ISO 8601 parsing.
            - dayfirst : bool
                Flag to interpret day before month (e.g., "15/12/2025").
            - fuzzy : bool
                Flag to allow fuzzy parsing, ignoring unknown tokens.

        Returns
        -------
        datetime.datetime
            A Python `datetime` object representing the parsed value.

        Raises
        ------
        ValueError
            If the input string cannot be parsed into a valid datetime.

        Notes
        -----
        - Parsing behavior depends on the underlying parser (commonly `dateutil.parser`).
        - Timezone information is applied if provided in `options`.
        - Fuzzy parsing allows ignoring extraneous text in the input string.
        """
        if options.iso:
            result = isoparse(datetime_value)
            return result
        else:
            pattern = """(?ix)(.*[0-9])(
                        jan(uary)?|
                        feb(ruary)?|
                        mar(ch)?|
                        apr(il)?|
                        may|
                        june?|
                        july?|
                        aug(ust)?|
                        sep(tember)?|
                        oct(ober)?|
                        nov(ember)?|
                        dec(ember)?)([0-9].*)"""
            datetime_value = re.sub(pattern, r'\1 \2 \12', datetime_value)
            result = parse(datetime_value, dayfirst=options.dayfirst,
                           fuzzy=options.fuzzy, tzinfos=options.tzinfos)
            return result

    @classmethod
    def do_date_compare(cls, a_date, op, other_date):
        """
        Compare two datetime objects using a specified operator.

        This method performs a comparison between `a_date` and `other_date`
        using either symbolic or textual operators. It supports equality,
        inequality, and relational comparisons.

        Parameters
        ----------
        a_date : datetime.datetime
            The first datetime object to compare.
        op : str
            The comparison operator. Supported values include:
            - Textual: "lt", "le", "gt", "ge", "eq", "ne"
            - Symbolic: "<", "<=", ">", ">=", "==", "!="
        other_date : datetime.datetime
            The second datetime object to compare against.

        Returns
        -------
        bool
            True if the comparison between `a_date` and `other_date`
            evaluates successfully according to the operator.
            False otherwise.

        Raises
        ------
        ValueError
            If an unsupported operator is provided.

        Notes
        -----
        - Operators are case-sensitive and must match one of the supported
          textual or symbolic forms.
        - Comparison is performed directly on `datetime` objects, so both
          inputs must be valid `datetime.datetime` instances.
        """
        a_tzname = a_date.tzname()
        other_tzname = other_date.tzname()
        if not bool(a_tzname) ^ bool(other_tzname):
            result = getattr(operator, op)(a_date, other_date)
            return result
        elif not a_tzname:
            a_new_datetime = datetime(
                a_date.year, a_date.month, a_date.day,
                a_date.hour, a_date.minute, a_date.second,
                a_date.microsecond, tzinfo=UTC
            )
            result = getattr(operator, op)(a_new_datetime, other_date)
            return result
        else:
            other_new_datetime = datetime(
                other_date.year, other_date.month, other_date.day,
                other_date.hour, other_date.minute, other_date.second,
                other_date.microsecond, tzinfo=UTC
            )
            result = getattr(operator, op)(a_date, other_new_datetime)
            return result

    @classmethod
    def compare_datetime(cls, value, op, other, valid=True, on_exception=True):
        """
        Compare two datetime values using a specified operator.

        This method parses two datetime strings (`value` and `other`) into
        `datetime.datetime` objects and performs a comparison using either
        symbolic or textual operators. It supports equality, inequality,
        and relational comparisons, with configurable validation outcomes
        and exception handling.

        Parameters
        ----------
        value : str
            The first datetime string to compare (e.g., "2025-12-15 14:30:00").
        op : str
            The comparison operator. Supported values include:
            - Textual: "lt", "le", "gt", "ge", "eq", "ne"
            - Symbolic: "<", "<=", ">", ">=", "==", "!="
        other : str
            The second datetime string to compare against.
        valid : bool, optional
            Expected validation outcome. Default is True.
            - If True, returns True when the comparison result is correct.
            - If False, returns True when the comparison result is *not* correct.
        on_exception : bool, optional
            Controls exception behavior. Default is True.
            - If True, raises an exception when parsing or comparison fails.
            - If False, suppresses exceptions and returns False.

        Returns
        -------
        bool
            True if the comparison result matches the expectation defined by `valid`.
            False otherwise.

        Raises
        ------
        ValueError
            If the operator is invalid, the datetime strings cannot be parsed,
            or the comparison fails and `on_exception=True`.

        Notes
        -----
        - String inputs are parsed into `datetime.datetime` objects before comparison.
        - Operators are case-sensitive and must match one of the supported
          textual or symbolic forms.
        - The `valid` flag allows inversion of the check (e.g., ensuring a comparison
          does *not* hold true).
        - The `on_exception` flag provides flexibility in error handling.
        """
        if str(value).upper() == '__EXCEPTION__':
            return False

        try:
            if str(value).strip() == '' or str(other).strip() == '':
                return False

            op = 'lt' if op == '<' else 'le' if op == '<=' else op
            op = 'gt' if op == '>' else 'ge' if op == '>=' else op
            op = 'eq' if op == '==' else 'ne' if op == '!=' else op

            dt_parsed_result = DatetimeValidation.parse_custom_date(other)

            a_date_str, other_date_str = value, dt_parsed_result.data

            if other_date_str.strip() == '':
                return False

            a_date = DatetimeValidation.get_date(a_date_str, dt_parsed_result)
            other_date = DatetimeValidation.get_date(other_date_str, dt_parsed_result)

            result = DatetimeValidation.do_date_compare(a_date, op, other_date)
            return result if valid else not result
        except Exception as ex:
            result = raise_exception_if(ex, on_exception=on_exception)
            return result
