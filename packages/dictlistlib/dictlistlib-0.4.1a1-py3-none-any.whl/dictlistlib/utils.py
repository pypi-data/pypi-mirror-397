"""
Utility functions and helper classes for dictlistlib.

This module provides reusable logic for text formatting, wildcard-to-regex
conversion, dictionary views, and tabular data presentation. It includes
functions, classes, and helpers that support dictlistlib’s query and
output features.

Contents
--------
Functions
---------
convert_wildcard_to_regex(pattern: str, closed: bool = False) -> str
    Convert a wildcard pattern into an equivalent regular expression.
    Supports ?, *, [], and [!] syntax.

foreach(data: Any, choice: str = 'keys')
    Return a set-like view of a dictionary’s keys, values, or items.

get_data_as_tabular(data, columns=None, justify='left', missing='not_found') -> str
    Convert a list of dictionaries (or a single dictionary) into a tabular
    string representation.

print_data_as_tabular(data, columns=None, justify='left', missing='not_found') -> None
    Print a list of dictionaries (or a single dictionary) in tabular format.

Classes
-------
BaseText(str)
    A string subclass that formats exceptions into readable text.

Text(BaseText)
    A simple subclass of BaseText for text handling.

Printer
    A utility class for printing formatted data with optional headers,
    footers, and width constraints.

Tabular
    A class for constructing tabular representations of dictionary data.
    Supports column selection, justification, and handling of missing values.

Notes
-----
- Wildcard patterns are automatically converted to regex for flexible matching.
- Tabular formatting is useful for displaying query results in a readable way.
- These utilities are intended to support dictlistlib’s core query engine
  but can also be used independently.
"""

import re
from collections import OrderedDict
from textwrap import wrap
import typing
from pprint import pprint

from dictlistlib.argumenthelper import validate_argument_type
from dictlistlib.exceptions import RegexConversionError


def convert_wildcard_to_regex(pattern, closed=False):
    """
    Convert a wildcard pattern into an equivalent regular expression.

    This function translates common wildcard symbols into their regex
    equivalents, allowing flexible pattern matching. Optionally, the
    resulting regex can be anchored with ``^`` and ``$`` to enforce
    full-string matches.

    Parameters
    ----------
    pattern : str
        A wildcard pattern to convert. Supported symbols include:
        - ``?`` : matches any single character.
        - ``*`` : matches zero or more characters.
        - ``[]`` : defines a character range (e.g., ``[a-z]``).
        - ``[!]`` : negates a character range (e.g., ``[!0-9]``).
    closed : bool, optional
        If True, prepend ``^`` and append ``$`` to the regex pattern
        to enforce full-string matching. Default is False.

    Returns
    -------
    str
        A valid regular expression string equivalent to the given
        wildcard pattern.

    Raises
    ------
    RegexConversionError
        If the wildcard pattern cannot be converted into a valid regex.

    Notes
    -----
    - Literal ``.`` and ``+`` characters are escaped automatically.
    - Wildcard symbols are internally replaced with regex equivalents
      before compilation.
    - The function validates the resulting regex by compiling it.
    """
    validate_argument_type(str, pattern=pattern)    # noqa
    regex_pattern = ''
    try:
        regex_pattern = pattern.replace('.', r'\.')
        regex_pattern = regex_pattern.replace('+', r'\+')
        regex_pattern = regex_pattern.replace('?', '_replacetodot_')
        regex_pattern = regex_pattern.replace('*', '_replacetodotasterisk_')
        regex_pattern = regex_pattern.replace('_replacetodot_', '.')
        regex_pattern = regex_pattern.replace('_replacetodotasterisk_', '.*')
        regex_pattern = regex_pattern.replace('[!', '[^')
        regex_pattern = '^{}$'.format(regex_pattern) if closed else regex_pattern
        re.compile(regex_pattern)
        return regex_pattern
    except Exception as ex:
        fmt = 'Failed to convert wildcard({!r}) to regex({!r})\n{}'
        raise RegexConversionError(fmt.format(pattern, regex_pattern, ex))


def foreach(data, choice='keys'):
    """
    Return a set-like view of a dictionary’s keys, values, or items.

    This function provides a convenient way to iterate over a dictionary
    (or dict-like object) by returning a view object corresponding to
    the specified choice. The returned object behaves like a dynamic
    set-like view that reflects changes to the underlying dictionary.

    Parameters
    ----------
    data : dict or dict-like
        The dictionary or dict-like object to inspect.
    choice : str, optional
        Specifies which view to return. Must be one of:
        - ``'keys'``   : return a view of the dictionary’s keys.
        - ``'values'`` : return a view of the dictionary’s values.
        - ``'items'``  : return a view of the dictionary’s key-value pairs.
        Default is ``'keys'``.

    Returns
    -------
    dict_keys or odict_keys
        If ``choice='keys'``.
    dict_values or odict_values
        If ``choice='values'``.
    dict_items or odict_items
        If ``choice='items'``.

    Raises
    ------
    ValueError
        If `choice` is not one of ``'keys'``, ``'values'``, or ``'items'``.
    """
    if isinstance(data, dict):
        node = data
    elif isinstance(data, (list, tuple)):
        total = len(data)
        node = OrderedDict(zip(range(total), data))
    else:
        node = dict()

    if choice == 'keys':
        return node.keys()
    elif choice == 'values':
        return node.values()
    else:
        return node.items()


class BaseText(str):
    """
    A string subclass that provides enhanced text representation.

    `BaseText` extends Python’s built-in `str` type to handle exceptions
    gracefully. When initialized with a `BaseException` instance, it
    automatically formats the exception into a readable string containing
    the exception type and message. Otherwise, it behaves like a normal
    string.

    This is useful for consistent error reporting and logging, ensuring
    exceptions are converted into human-readable text without requiring
    explicit formatting.

    Methods
    -------
    __new__(*args, **kwargs)
        Create a new `BaseText` instance. If the first argument is an
        exception, return a formatted string representation of it.
    """
    def __new__(cls, *args, **kwargs):
        arg0 = args[0] if args else None
        if args and isinstance(arg0, BaseException):
            txt = str.__new__(cls, '{}: {}'.format(type(arg0).__name__, arg0))
            return txt
        else:
            txt = str.__new__(cls, *args, **kwargs)
            return txt


class Text(BaseText):
    """
    A string subclass with extended text formatting and utility methods.

    `Text` builds on `BaseText` to provide additional functionality for
    safe string formatting, HTML wrapping, and regex-based splitting.
    It is designed to simplify common text manipulation tasks while
    gracefully handling exceptions.

    Methods
    -------
    format(*args, **kwargs) -> str
        Safely format a string using either old-style (`%`) or new-style
        (`str.format`) formatting. If formatting fails, returns a readable
        error message instead of raising an exception.
        - If called with no arguments, returns an empty string.
        - If called with one argument, returns it as a `Text` instance.
        - If called with multiple arguments, attempts formatting with
          `%` first, then falls back to `str.format`.

    wrap_html(tag, data, *args) -> str
        Wrap the given data in an HTML tag. Optional attributes can be
        provided as additional arguments.
        - If `data` is empty, produces a self-closing tag.
        - Attributes are joined with spaces and inserted into the tag.

    do_finditer_split(pattern) -> list[str]
        Split the string into segments based on regex matches.
        Returns a list containing alternating non-matching substrings
        and matched substrings.
    """
    @classmethod
    def format(cls, *args, **kwargs):
        """
        Safely format text using old-style (`%`) or new-style (`str.format`) string formatting.

        This method attempts to format a string with the provided arguments,
        supporting both positional and keyword-based formatting. It provides
        graceful error handling: if formatting fails, the exception is captured
        and returned as a readable `Text` instance instead of raising an error.

        Behavior
        --------
        - If called with no arguments, returns an empty string.
        - If called with one argument, returns it as a `Text` instance.
        - If called with multiple arguments:
            * Tries old-style (`%`) formatting first.
            * Falls back to new-style (`str.format`) if needed.
            * If both fail, returns a concatenated error message from both attempts.

        Parameters
        ----------
        *args : tuple
            Positional arguments used for formatting. The first argument is
            treated as the format string, and subsequent arguments are values
            to substitute.
        **kwargs : dict
            Keyword arguments used for new-style (`str.format`) formatting.

        Returns
        -------
        str
            The formatted string if successful, otherwise a string containing
            the error message(s).
        """
        if not args:
            text = ''
            return text
        else:
            if kwargs:
                fmt = args[0]
                try:
                    text = str(fmt).format(args[1:], **kwargs)
                    return text
                except Exception as ex:
                    text = cls(ex)
                    return text
            else:
                if len(args) == 1:
                    text = cls(args[0])
                    return text
                else:
                    fmt = args[0]
                    t_args = tuple(args[1:])
                    try:
                        if len(t_args) == 1 and isinstance(t_args[0], dict):
                            text = str(fmt) % t_args[0]
                        else:
                            text = str(fmt) % t_args

                        if text == fmt:
                            text = str(fmt).format(*t_args)
                        return text
                    except Exception as ex1:
                        try:
                            text = str(fmt).format(*t_args)
                            return text
                        except Exception as ex2:
                            text = '%s\n%s' % (cls(ex1), cls(ex2))
                            return text

    @classmethod
    def wrap_html(cls, tag, data, *args):
        """
        Wrap text content in an HTML element.

        This method generates an HTML string by wrapping the given `data`
        inside the specified `tag`. Optional attributes can be provided
        as additional arguments. If `data` is empty or whitespace, a
        self-closing tag is produced instead.

        Parameters
        ----------
        tag : str
            The HTML tag name (e.g., "div", "span", "p").
        data : str
            The text content to wrap inside the tag. If empty, a self-closing
            tag is generated.
        *args : str
            Optional attribute strings (e.g., "class='highlight'", "id='main'").
            Multiple attributes are joined with spaces.

        Returns
        -------
        str
            A string containing the generated HTML element.

        Behavior
        --------
        - If attributes are provided, they are inserted into the opening tag.
        - If `data` contains non-whitespace text, a normal opening/closing tag
          pair is generated.
        - If `data` is empty or whitespace, a self-closing tag is generated.
        """
        data = str(data)
        tag = str(tag).strip()
        attributes = [str(arg).strip() for arg in args if str(arg).strip()]
        if attributes:
            attrs_txt = str.join(' ', attributes)
            if data.strip():
                result = '<{0} {1}>{2}</{0}>'.format(tag, attrs_txt, data)
            else:
                result = '<{0} {1}/>'.format(tag, attrs_txt)
        else:
            if data.strip():
                result = '<{0}>{1}</{0}>'.format(tag, data)
            else:
                result = '<{0}/>'.format(tag)
        return result

    def do_finditer_split(self, pattern):
        """
        Split the string into segments based on regex matches.

        This method uses `re.finditer` to locate all occurrences of the given
        regex `pattern` within the string. It returns a list containing
        alternating substrings: the non-matching text before each match,
        followed by the matched text itself. The final element includes any
        remaining text after the last match.

        Parameters
        ----------
        pattern : str
            A regular expression pattern used to identify matches within
            the string.

        Returns
        -------
        list of str
            A list of substrings consisting of:
            - Non-matching text before each match.
            - The matched text itself.
            - The trailing text after the last match (if any).

        Notes
        -----
        - If no matches are found, the entire string is returned as a single
          element in the list.
        - Useful for tokenizing text while preserving matched delimiters.
        """
        result = []
        start = 0
        m = None
        for m in re.finditer(pattern, self):
            pre_match = self[start:m.start()]
            match = m.group()
            result.append(pre_match)
            result.append(match)
            start = m.end()

        if m:
            post_match = self[m.end():]
            result.append(post_match)
        else:
            result.append(str(self))
        return result


class Printer:
    """
    A utility class for formatted printing of data.

    The `Printer` class provides methods to format and display data
    with optional headers, footers, failure messages, and width
    constraints. It is designed to improve readability of structured
    output such as lists, dictionaries, or tabular data.

    Methods
    -------
    get(data, header='', footer='', failure_msg='', width=80, width_limit=20) -> str
        Format the given data into a string with optional header and footer.
        If the data is empty or invalid, return the `failure_msg`.
        - `width` specifies the maximum line width before wrapping.
        - `width_limit` controls the maximum width of individual items.

    print(data, header='', footer='', failure_msg='', width=80, width_limit=20, print_func=None) -> None
        Print the formatted data directly to standard output (or a custom
        print function if provided). Accepts the same arguments as `get`.
    """
    @classmethod
    def get(cls, data, header='', footer='',
            width=80, width_limit=20, failure_msg=''):
        """
        Format data into a readable string with optional header and footer.

        This method converts the given `data` into a formatted string,
        applying line wrapping and width constraints for readability.
        If the data is empty or invalid, the provided `failure_msg` is
        returned instead. It is useful for preparing structured output
        (lists, dicts, tabular data) for display or logging.

        Parameters
        ----------
        data : str, list
            a text or a list of text.
        header : str
            Text to prepend before the formatted data. Default is empty.
        footer : str
            Text to append after the formatted data. Default is empty.
        failure_msg : str
            Message to return if `data` is empty or invalid. Default is empty.
        width : int
            Maximum line width before wrapping. Default is 80.
        width_limit : int
            Maximum width of individual items before truncation. Default is 20.

        Returns
        -------
        str
            A formatted string representation of the data, including
            optional header and footer. If `data` is empty, returns
            `failure_msg`.

        Notes
        -----
        - Line wrapping ensures readability for long strings or lists.
        - Width limits prevent overly long items from breaking formatting.
        - This method does not print directly; use `Printer.print` for output.
        """
        lst = []
        result = []

        sequence_type = (typing.List, typing.Tuple, typing.Set)

        if width > 0:
            right_bound = width - 4
        else:
            right_bound = 76

        headers = []
        if header:
            if isinstance(header, sequence_type):
                for item in header:
                    for line in str(item).splitlines():
                        headers.extend(wrap(line, width=right_bound))
            else:
                headers.extend(wrap(str(header), width=right_bound))

        footers = []
        if footer:
            if isinstance(footer, sequence_type):
                for item in footer:
                    for line in str(item).splitlines():
                        footers.extend(wrap(line, width=right_bound))
            else:
                footers.extend(wrap(str(footer), width=right_bound))

        if data:
            data = data if isinstance(data, sequence_type) else [data]
        else:
            data = []

        for item in data:
            if width > 0:
                if width >= width_limit:
                    for line in str(item).splitlines():
                        lst.extend(wrap(line, width=right_bound + 4))
                else:
                    lst.extend(line.rstrip() for line in str(item).splitlines())
            else:
                lst.append(str(item))
        length = max(len(str(i)) for i in lst + headers + footers)

        if width >= width_limit:
            length = right_bound if right_bound > length else length

        result.append(Text.format('+-{}-+', '-' * length))  # noqa
        if header:
            for item in headers:
                result.append(Text.format('| {} |', item.ljust(length)))    # noqa
            result.append(Text.format('+-{}-+', '-' * length))  # noqa

        for item in lst:
            result.append(item)
        result.append(Text.format('+-{}-+', '-' * length))  # noqa

        if footer:
            for item in footers:
                result.append(Text.format('| {} |', item.ljust(length)))    # noqa
            result.append(Text.format('+-{}-+', '-' * length))  # noqa

        if failure_msg:
            result.append(failure_msg)

        txt = str.join(r'\n', result)
        return txt

    @classmethod
    def print(cls, data, header='', footer='',
              width=80, width_limit=20, failure_msg='', print_func=None):
        """
        Print formatted data with optional header and footer.

        This method formats the given `data` into a readable string
        (using the same logic as `Printer.get`) and prints it directly
        to standard output or a custom print function. It is useful for
        displaying structured output such as lists, dictionaries, or
        tabular data in a human-readable way.

        Parameters
        ----------
        data : str, list
            a text or a list of text.
        header : str
            Text to prepend before the formatted data. Default is empty.
        footer : str
            Text to append after the formatted data. Default is empty.
        failure_msg : str
            Message to print if `data` is empty or invalid. Default is empty.
        width : int
            Maximum line width before wrapping. Default is 80.
        width_limit : int
            Maximum width of individual items before truncation. Default is 20.
        print_func : callable
            A custom print function to use instead of the built-in `print`.
            Must accept a single string argument. Default is None.

        Returns
        -------
        None
            This method prints the formatted output and does not return a value.

        Notes
        -----
        - Internally uses `Printer.get` to format the data before printing.
        - If `print_func` is provided, the formatted string is passed to it
          instead of being printed to stdout.
        """

        txt = Printer.get(data, header=header, footer=footer,
                          failure_msg=failure_msg, width=width,
                          width_limit=width_limit)

        print_func = print_func if callable(print_func) else print
        print_func(txt)

    @classmethod
    def get_message(cls, fmt, *args, style='format', prefix=''):
        """
        Construct a formatted message string with optional prefix.

        This method formats a message using either Python's new-style
        (`str.format`) or old-style (`%`) string interpolation. It allows
        flexible message construction with positional arguments and an
        optional prefix. If no arguments are provided, the format string
        itself is returned.

        Parameters
        ----------
        fmt : str
            The format string to interpolate. Can contain placeholders
            compatible with either `.format` or `%` depending on `style`.
        *args : tuple
            Positional arguments to substitute into the format string.
        style : str, optional
            The formatting style to use:
            - ``'format'`` : use `str.format` (default).
            - ``'%'``      : use old-style `%` interpolation.
        prefix : str, optional
            A string to prepend before the formatted message. If provided,
            it is followed by a space before the message. Default is empty.

        Returns
        -------
        str
            The formatted message string, optionally prefixed.
        """
        if args:
            message = fmt.format(*args) if style == 'format' else fmt % args
        else:
            message = fmt

        message = '{} {}'.format(prefix, message) if prefix else message
        return message

    @classmethod
    def print_message(cls, fmt, *args, style='format', prefix='', print_func=None):
        """
        Format and print a message with optional prefix.

        This method constructs a message string using either Python's
        new-style (`str.format`) or old-style (`%`) string interpolation,
        then prints it directly to standard output or a custom print
        function. It is useful for producing consistent, human-readable
        messages for logging, reporting, or user-facing output.

        Parameters
        ----------
        fmt : str
            The format string to interpolate. Can contain placeholders
            compatible with either `.format` or `%` depending on `style`.
        *args : tuple
            Positional arguments to substitute into the format string.
        style : str, optional
            The formatting style to use:
            - ``'format'`` : use `str.format` (default).
            - ``'%'``      : use old-style `%` interpolation.
        prefix : str, optional
            A string to prepend before the formatted message. If provided,
            it is followed by a space before the message. Default is empty.
        print_func : callable, optional
            A custom print function to use instead of the built-in `print`.
            Must accept a single string argument. Default is None.

        Returns
        -------
        None
            This method prints the formatted message and does not return a value.
        """
        message = cls.get_message(fmt, *args, style=style, prefix=prefix)
        print_func = print_func if callable(print_func) else print
        print_func(message)


class Tabular:
    """
    A utility class for constructing and displaying tabular data.

    The `Tabular` class formats dictionaries (or lists of dictionaries)
    into a human-readable table. It supports column selection, text
    justification, and handling of missing values. This is useful for
    presenting structured data such as query results, reports, or logs
    in a clear tabular format.

    Attributes
    ----------
    data : list of dict
        The input data to format. Can be a list of dictionaries or a
        single dictionary (which will be wrapped in a list).
    columns : list of str, optional
        A list of column headers to include in the table. If None,
        all keys from the dictionaries are used. Default is None.
    justify : str, optional
        Text alignment for columns. Must be one of:
        - ``'left'``   : left-align text (default).
        - ``'right'``  : right-align text.
        - ``'center'`` : center-align text.
    missing : str, optional
        Placeholder text for missing values when a column is not found
        in the data. Default is ``'not_found'``.

    Methods
    -------
    validate_argument_list_of_dict() -> None
        Validate that the input data is a list of dictionaries.
    build_width_table(columns) -> dict
        Compute the maximum width for each column based on the data.
    align_string(value, width) -> str
        Align a string within a given width according to `justify`.
    build_headers_string(columns, width_tbl) -> str
        Construct the header row as a formatted string.
    build_tabular_string(columns, width_tbl) -> str
        Construct the table body as a formatted string.
    process() -> None
        Process the input data and prepare the tabular representation.
    get() -> str or list
        Return the formatted table as a string, or raw data if not processed.
    print() -> None
        Print the formatted table directly to standard output.
    """
    def __init__(self, data, columns=None, justify='left', missing='not_found'):
        self.result = ''
        if isinstance(data, dict):
            self.data = [data]
        else:
            self.data = data
        self.columns = columns
        self.justify = str(justify).lower()
        self.missing = missing
        self.is_ready = True
        self.is_tabular = False
        self.failure = ''
        self.validate_argument_list_of_dict()
        self.process()

    def validate_argument_list_of_dict(self):
        """
        Validate that the input data is a list of dictionaries.

        This method ensures that the `data` attribute of the `Tabular`
        instance is properly structured as either:
        - A list of dictionaries, or
        - A single dictionary (which is automatically wrapped in a list
          during initialization).

        If the validation fails, the method sets internal flags to mark
        the tabular object as invalid and records an error message.

        Returns
        -------
        None
            This method does not return a value. It updates internal
            state (`is_ready`, `failure`) to reflect validation results.

        Raises
        ------
        TypeError
            If `data` is not a dictionary or a list of dictionaries.

        Notes
        -----
        - This method is called automatically during initialization.
        - Ensures that subsequent tabular processing methods can safely
          assume the input is valid.
        """
        if not isinstance(self.data, (list, tuple)):
            self.is_ready = False
            self.failure = 'data MUST be a list.'
            return

        if not self.data:
            self.is_ready = False
            self.failure = 'data MUST be NOT an empty list.'
            return

        chk_keys = list()
        for a_dict in self.data:
            if isinstance(a_dict, dict):
                if not a_dict:
                    self.is_ready = False
                    self.failure = 'all dict elements MUST be NOT empty.'
                    return

                keys = list(a_dict.keys())
                if not chk_keys:
                    chk_keys = keys
                else:
                    if keys != chk_keys:
                        self.is_ready = False
                        self.failure = 'dict element MUST have same keys.'
                        return
            else:
                self.is_ready = False
                self.failure = 'all elements of list MUST be dictionary.'
                return

    def build_width_table(self, columns):
        """
        Compute the maximum width for each column in the tabular data.

        This method analyzes the provided `columns` and the instance's `data`
        to determine the maximum string length required for each column. The
        result is a mapping of column names to their respective widths, which
        can be used to align and format tabular output consistently.

        Parameters
        ----------
        columns : list of str
            A list of column headers to include in the width calculation.
            Each column name is checked against the data to determine the
            longest string value.

        Returns
        -------
        dict
            A dictionary mapping each column name to its maximum string
            length (including the header itself). For example:
            ``{"name": 5, "age": 3}``.

        Notes
        -----
        - The width of each column is the maximum of:
            * The length of the column header.
            * The length of the longest value in that column across all rows.
        - Missing values are replaced with the `missing` attribute before
          measuring length.
        """
        width_tbl = dict(zip(columns, (len(str(k)) for k in columns)))

        for a_dict in self.data:
            for col, width in width_tbl.items():
                curr_width = len(str(a_dict.get(col, self.missing)))
                new_width = max(width, curr_width)
                width_tbl[col] = new_width
        return width_tbl

    def align_string(self, value, width):
        """
        Align a string within a given width according to the justification setting.

        This method takes a value, converts it to a string, and aligns it
        within the specified width based on the `justify` attribute of the
        `Tabular` instance. Supported justifications are left, right, and
        center alignment.

        Parameters
        ----------
        value : Any
            The data to align. It will be converted to a string before alignment.
        width : int
            The target width for alignment. If the string is shorter than
            `width`, padding is added according to the justification.

        Returns
        -------
        str
            The aligned string, padded with spaces as needed to fit the
            specified width.

        Notes
        -----
        - The `justify` attribute of the `Tabular` instance determines
          alignment:
            * ``'left'``   : pad on the right.
            * ``'right'``  : pad on the left.
            * ``'center'`` : pad evenly on both sides.
        - If `value` is longer than `width`, it is returned unchanged.
        """
        value = str(value)
        if self.justify == 'center':
            return str.center(value, width)
        elif self.justify == 'right':
            return str.rjust(value, width)
        else:
            return str.ljust(value, width)

    def build_headers_string(self, columns, width_tbl):
        """
        Construct the header row of the tabular output as a formatted string.

        This method takes a list of column headers and a width mapping table,
        then aligns each header according to the `justify` setting of the
        `Tabular` instance. The result is a single string representing the
        header row of the table.

        Parameters
        ----------
        columns : list of str
            A list of column names to include in the header row.
        width_tbl : dict
            A dictionary mapping each column name to its maximum width
            (as computed by `build_width_table`). Used to align headers
            consistently with the table body.

        Returns
        -------
        str
            A formatted string containing the aligned column headers,
            separated by spaces.

        Notes
        -----
        - Each header is padded or aligned based on the width specified
          in `width_tbl`.
        - Alignment is controlled by the `justify` attribute of the
          `Tabular` instance (left, right, or center).
        - The resulting string is typically used as the first row of
          the tabular output.
        """
        lst = []
        for col in columns:
            width = width_tbl.get(col)
            new_col = self.align_string(col, width)
            lst.append(new_col)
        return '| {} |'.format(str.join(' | ', lst))

    def build_tabular_string(self, columns, width_tbl):
        """
        Construct the body of the tabular output as a formatted string.

        This method iterates over the instance's `data` and builds a
        tabular representation row by row. Each value is aligned according
        to the `justify` setting of the `Tabular` instance and padded to
        the width specified in `width_tbl`. The result is a multi-line
        string representing the table body.

        Parameters
        ----------
        columns : list of str
            A list of column headers that define the order of values in
            each row.
        width_tbl : dict
            A dictionary mapping each column name to its maximum width
            (as computed by `build_width_table`). Used to align values
            consistently across rows.

        Returns
        -------
        str
            A formatted string containing the tabular data rows, with
            values aligned and separated by spaces.

        Notes
        -----
        - Missing values are replaced with the `missing` attribute of
          the `Tabular` instance.
        - Alignment is controlled by the `justify` attribute (left,
          right, or center).
        - The resulting string does not include headers; use
          `build_headers_string` for the header row.
        """
        lst_of_str = []
        for a_dict in self.data:
            lst = []
            for col in columns:
                val = a_dict.get(col, self.missing)
                width = width_tbl.get(col)
                new_val = self.align_string(val, width)
                lst.append(new_val)
            lst_of_str.append('| {} |'.format(str.join(' | ', lst)))

        return str.join(r'\n', lst_of_str)

    def process(self):
        """
        Prepare the input data for tabular formatting.

        This method validates the input `data` and constructs the internal
        structures required to generate a tabular representation. It ensures
        that the data is properly normalized (list of dictionaries), computes
        column widths, and builds both the header and body strings. After
        calling `process`, the table is ready to be retrieved with `get()` or
        printed with `print()`.

        Returns
        -------
        None
            This method updates internal state and does not return a value.

        Notes
        -----
        - Calls `validate_argument_list_of_dict()` to ensure data integrity.
        - Uses `build_width_table()` to compute column widths.
        - Relies on `build_headers_string()` and `build_tabular_string()` to
          construct the formatted output.
        - Must be executed before calling `get()` or `print()` if the table
          has not yet been processed.
        """
        if not self.is_ready:
            return

        try:
            keys = list(self.data[0].keys())
            columns = self.columns or keys
            width_tbl = self.build_width_table(columns)
            deco = ['-' * width_tbl.get(c) for c in columns]
            deco_str = '+-{}-+'.format(str.join('-+-', deco))
            headers_str = self.build_headers_string(columns, width_tbl)
            tabular_data = self.build_tabular_string(columns, width_tbl)

            lst = [deco_str, headers_str, deco_str, tabular_data, deco_str]
            self.result = str.join(r'\n', lst)
            self.is_tabular = True
        except Exception as ex:
            self.failure = '{}: {}'.format(type(ex).__name__, ex)
            self.is_tabular = False

    def get(self):
        """
        Retrieve the processed tabular output or the raw data.

        This method returns the formatted tabular string if the instance
        has successfully processed the input data into tabular format.
        Otherwise, it falls back to returning the original `data` attribute.

        Returns
        -------
        str or Any
            - If `is_tabular` is True, returns the formatted tabular string
              stored in `result`.
            - If `is_tabular` is False, returns the original `data`.

        Notes
        -----
        - Typically called after `process()` to retrieve the final tabular
          representation.
        - Provides a safe way to access either the formatted output or the
          raw data depending on processing status.
        """
        tabular_data = self.result if self.is_tabular else self.data
        return tabular_data

    def print(self):
        """
        Print the tabular content or raw data.

        This method retrieves the current output from `get()` and prints it
        in a human-readable format. If the result is a structured object
        (e.g., dict, list, tuple, or set), it uses `pprint` for pretty-printing.
        Otherwise, it prints the string representation directly.

        Returns
        -------
        None
            This method prints the output and does not return a value.

        Notes
        -----
        - If the data has been processed into tabular format, the formatted
          string is printed.
        - If the data is still raw (e.g., a dictionary or list), it is
          pretty-printed for readability.
        - Acts as a convenience wrapper around `get()` and `pprint`.
        """
        tabular_data = self.get()
        if isinstance(tabular_data, (dict, list, tuple, set)):
            pprint(tabular_data)
        else:
            print(tabular_data)


def get_data_as_tabular(data, columns=None, justify='left', missing='not_found'):
    """
    Convert structured data into a tabular string representation.

    This function wraps the `Tabular` class to provide a simple interface
    for translating dictionaries or lists of dictionaries into a formatted
    table. It supports optional column selection, text justification, and
    handling of missing values.

    Parameters
    ----------
    data : list of dict or dict
        The input data to format. Can be:
        - A list of dictionaries (multiple rows).
        - A single dictionary (treated as one row).
    columns : list of str, optional
        A list of column headers to include in the table. If None, all keys
        from the dictionaries are used. Default is None.
    justify : str, optional
        Text alignment for columns. Must be one of:
        - ``'left'``   : left-align text (default).
        - ``'right'``  : right-align text.
        - ``'center'`` : center-align text.
    missing : str, optional
        Placeholder text for missing values when a column is not found in
        the data. Default is ``'not_found'``.

    Returns
    -------
    str
        A formatted string representing the tabular data.

    Notes
    -----
    - Internally creates a `Tabular` instance and calls its `get()` method.
    - Useful for quickly converting structured data into a human-readable
      table without manually instantiating `Tabular`.
    """
    node = Tabular(data, columns=columns, justify=justify, missing=missing)
    result = node.get()
    return result


def print_data_as_tabular(data, columns=None, justify='left', missing='not_found'):
    """
    Print structured data in a tabular format.

    This function wraps the `Tabular` class to provide a simple interface
    for displaying dictionaries or lists of dictionaries as a formatted
    table. It supports optional column selection, text justification, and
    handling of missing values. The formatted table is printed directly
    to standard output.

    Parameters
    ----------
    data : list of dict or dict
        The input data to format. Can be:
        - A list of dictionaries (multiple rows).
        - A single dictionary (treated as one row).
    columns : list of str, optional
        A list of column headers to include in the table. If None, all keys
        from the dictionaries are used. Default is None.
    justify : str, optional
        Text alignment for columns. Must be one of:
        - ``'left'``   : left-align text (default).
        - ``'right'``  : right-align text.
        - ``'center'`` : center-align text.
    missing : str, optional
        Placeholder text for missing values when a column is not found in
        the data. Default is ``'not_found'``.

    Returns
    -------
    None
        This function prints the formatted table and does not return a value.

    Notes
    -----
    - Internally creates a `Tabular` instance and calls its `print()` method.
    - Useful for quickly displaying structured data without manually
      instantiating `Tabular`.
    """
    node = Tabular(data, columns=columns, justify=justify, missing=missing)
    node.print()
