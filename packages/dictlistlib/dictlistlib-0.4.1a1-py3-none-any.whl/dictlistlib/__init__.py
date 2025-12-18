"""
dictlistlib: Top-level package initializer.

This module provides the primary entry points for working with
`dictlistlib`. It exposes the `DLQuery` class for querying lists
of dictionaries, as well as factory functions for creating query
instances from CSV, JSON, or YAML sources.

Overview
--------
- Initialize a query instance directly with the `DLQuery` class.
- Or create a query instance using one of the factory functions:
  * `create_from_csv_file`
  * `create_from_csv_data`
  * `create_from_json_file`
  * `create_from_json_data`
  * `create_from_yaml_file`
  * `create_from_yaml_data`

Query Mechanics
---------------
A query instance provides the `find()` method to traverse dictionaries
or lists and extract records based on a **lookup expression** and an
optional **select statement**.

**Lookup Expressions**
- Consist of a left-hand expression (field) and a right-hand expression (filter).
- Supported filters:
  * `_text(...)`, `_itext(...)` — exact text match (case-sensitive / case-insensitive).
  * `_wildcard(...)`, `_iwildcard(...)` — wildcard pattern matching.
  * `_regex(...)`, `_iregex(...)` — regular expression matching.
- The right-hand expression also supports validations such as:
  * `is_empty()`, `is_not_empty()`
  * `is_ipv4_address()`, and more.

**Select Statements**
- Work similarly to SQL but with minimal syntax.
- Allow filtering with `WHERE` clauses and projection with `SELECT`.

Examples
--------
Assume we have a list of dictionaries:

>>> lst_of_dict = [
...     {"a": "Apple", "b": "Banana", "c": "Cherry"},
...     {"a": "Apricot", "b": "Boysenberry", "c": "Cantaloupe"},
...     {"a": "Avocado", "b": "Blueberry", "c": "Clementine"},
... ]

Initialize a query object:

>>> from dictlistlib import DLQuery
>>> query_obj = DLQuery(lst_of_dict)

**Snippet 1: Lookup with wildcard filtering**

>>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='')
>>> assert result == ['Apple', 'Apricot']

**Snippet 2: Lookup with regex filtering**

>>> result = query_obj.find(lookup='a=_regex(Ap\\w+)', select='')
>>> assert result == ['Apple', 'Apricot']

**Snippet 3: Lookup with WHERE clause**

>>> result = query_obj.find(lookup='a', select='WHERE a match Ap\\w+')
>>> assert result == ["Apple", "Apricot"]

**Snippet 4: Lookup with wildcard + SELECT**

>>> result = query_obj.find(lookup='a=_wildcard(Ap*)', select='SELECT a, b')
>>> assert result == [{'a': 'Apple', 'b': 'Banana'},
...                   {'a': 'Apricot', 'b': 'Boysenberry'}]

**Snippet 5: Lookup with regex + SELECT**

>>> result = query_obj.find(lookup='a=_regex(Ap\\w+)', select='SELECT a, c')
>>> assert result == [{'a': 'Apple', 'c': 'Cherry'},
...                   {'a': 'Apricot', 'c': 'Cantaloupe'}]

**Snippet 6: Lookup with WHERE clause + SELECT**

>>> result = query_obj.find(lookup='a', select='SELECT c WHERE a match Ap\\w+')
>>> assert result == [{'c': 'Cherry'}, {'c': 'Cantaloupe'}]

Notes
-----
- If no fields are selected, the result is a list of values.
- Using `SELECT` allows retrieval of filtered records along with sibling fields.
- Filtering supports case sensitivity and regex flexibility.
"""

from dictlistlib.dlquery import DLQuery         # noqa
from dictlistlib.factory import create_from_yaml_file   # noqa
from dictlistlib.factory import create_from_yaml_data   # noqa
from dictlistlib.factory import create_from_json_file   # noqa
from dictlistlib.factory import create_from_json_data   # noqa
from dictlistlib.factory import create_from_csv_file    # noqa
from dictlistlib.factory import create_from_csv_data    # noqa

from dictlistlib.validation import RegexValidation      # noqa
from dictlistlib.validation import OpValidation         # noqa
from dictlistlib.validation import CustomValidation     # noqa

from dictlistlib.config import version
from dictlistlib.config import edition

__version__ = version
__edition__ = edition

__all__ = [
    'CustomValidation',
    'DLQuery',
    'OpValidation',
    'RegexValidation',
    'create_from_csv_file',
    'create_from_csv_data',
    'create_from_json_file',
    'create_from_json_data',
    'create_from_yaml_file',
    'create_from_yaml_data',
    'version',
    'edition'
]
