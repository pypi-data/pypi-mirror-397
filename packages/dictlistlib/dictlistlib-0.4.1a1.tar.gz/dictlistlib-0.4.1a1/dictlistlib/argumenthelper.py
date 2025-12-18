"""Argument helper utilities.

This module provides validation functions for checking argument types,
choices, and emptiness in functions or methods. It raises descriptive
errors when arguments fail validation, ensuring safer and more explicit
API usage.
"""

from dictlistlib.exceptions import ArgumentError
from dictlistlib.exceptions import ArgumentValidationError


def validate_argument_type(*args, **kwargs):
    """
    Validate that arguments match expected types.

    Parameters
    ----------
    *args : type
        One or more reference types (classes) to validate against.
    **kwargs : dict
        Keyword arguments mapping argument names to values that must
        match one of the provided types.

    Returns
    -------
    bool
        True if all arguments match the expected types.

    Raises
    ------
    ArgumentError
        If no reference types are provided, or if any element in `args`
        is not a class.
    ArgumentValidationError
        If a keyword argument value does not match any of the provided
        types.
    """
    if len(args) == 0:
        msg = 'Cannot validate argument with no reference data type.'
        raise ArgumentError(msg)
    else:
        for arg in args:
            if not issubclass(arg, object):
                msg = 'args must contain all classes.'
                raise ArgumentError(msg)

    fmt = '{} argument must be a data type of {}.'
    type_name = ', '.join(arg.__name__ for arg in args)
    type_name = '({})'.format(type_name) if len(args) > 1 else type_name

    for name, obj in kwargs.items():
        if not isinstance(obj, args):
            raise ArgumentValidationError(fmt.format(name, type_name))
    return True


def validate_argument_choice(**kwargs):
    """
    Validate that arguments belong to a set of allowed choices.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments mapping argument names to a tuple of
        (argument_value, choices). `choices` must be a non-empty
        list or tuple of valid options.

    Returns
    -------
    bool
        True if all arguments match one of their allowed choices.

    Raises
    ------
    ArgumentError
        If the provided (argument, choices) pair is invalid or if
        `choices` is empty or not a list/tuple.
    ArgumentValidationError
        If an argument value is not among the allowed choices.
    """
    for name, value in kwargs.items():
        try:
            argument, choices = value
        except Exception as ex:     # noqa
            msg = 'Invalid argument for verifying validate_argument_choice'
            raise ArgumentError(msg)

        is_not_a_list = not isinstance(choices, (list, tuple))
        is_empty = not bool(choices)

        if is_not_a_list or is_empty:
            raise ArgumentError('choices CAN NOT be empty.')

        if argument not in choices:
            fmt = '{} argument must be a choice of {}.'
            raise ArgumentValidationError(fmt.format(name, choices))
    return True


def validate_argument_is_not_empty(**kwargs):
    """
    Validate that arguments are not empty.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments mapping argument names to values that must
        not be empty (evaluating to False).

    Returns
    -------
    bool
        True if all arguments are non-empty.

    Raises
    ------
    ArgumentValidationError
        If one or more arguments are empty.
    """
    empty_args = []
    for name, value in kwargs.items():
        if not value:
            empty_args.append(name)

    if empty_args:
        if len(empty_args) == 1:
            msg = 'a {} argument CANNOT be empty.'.format(empty_args[0])
        else:
            msg = '({}) arguments CANNOT be empty.'.format(', '.join(empty_args))
        raise ArgumentValidationError(msg)
    return True
