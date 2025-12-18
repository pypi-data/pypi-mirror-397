"""
Module providing data structure collection logic.

This module defines a custom `List` class that extends Python's built-in
list with additional convenience properties and error handling. It also
imports supporting utilities, parsers, and validation helpers from
`dictlistlib`.
"""

import yaml
import json
import re
from functools import partial
from dictlistlib.argumenthelper import validate_argument_type
from dictlistlib import utils
from dictlistlib.parser import SelectParser
from dictlistlib.validation import OpValidation
from dictlistlib.validation import CustomValidation

from dictlistlib.exceptions import ListIndexError
from dictlistlib.exceptions import ResultError
from dictlistlib.exceptions import LookupClsError
from dictlistlib.exceptions import ObjectArgumentError


class List(list):
    """
    A custom list collection with extended properties and safe access methods.

    This class inherits from Python's built-in `list` and adds convenience
    properties for checking emptiness, retrieving the first and last elements,
    and obtaining the total number of items. It also provides dynamic attribute
    access for indexed elements (e.g., `list.index0`, `list.index_1`).

    Properties
    ----------
    is_empty : bool
        Indicates whether the list is empty.
    first : Any
        Returns the first element of the list. Raises `ListIndexError` if empty.
    last : Any
        Returns the last element of the list. Raises `ListIndexError` if empty.
    total : int
        The total number of elements in the list.

    Raises
    ------
    ListIndexError
        Raised when attempting to access an element in an empty list or
        when an index is out of range.
    """
    def __getattribute__(self, attr):
        """
        Provide custom attribute access for index-based lookup.

        This method overrides the default attribute access to support
        dynamic retrieval of list elements using attribute names that
        match the pattern ``indexN`` or ``index_N`` (where N is a number).
        For example, accessing ``obj.index0`` or ``obj.index_1`` will
        return the corresponding item from the underlying list.

        Parameters
        ----------
        attr : str
            The attribute name being accessed. If it matches the
            ``index<digit>`` pattern, it is interpreted as a list index;
            otherwise, normal attribute lookup is performed.

        Returns
        -------
        Any
            The value of the requested attribute, or the list element
            corresponding to the parsed index.

        Raises
        ------
        ListIndexError
            If the attribute matches the index pattern but the lookup
            fails (e.g., invalid index).
        AttributeError
            If the attribute does not exist and does not match the
            index pattern.

        Notes
        -----
        - Attribute names like ``index0`` or ``index_2`` are converted
          into integer indices (e.g., "0", "2") before lookup.
        - Underscores in the index portion are replaced with hyphens
          before conversion.
        - If the attribute does not match the index pattern, the method
          falls back to standard attribute resolution via
          ``super().__getattribute__``.
        """
        match = re.match(r'index(?P<index>_?[0-9]+)$', attr)    # noqa
        if match:
            index = match.group('index').replace('_', '-')
            try:
                value = self[int(index)]
                return value
            except Exception as ex:
                raise ListIndexError(str(ex))
        else:
            value = super().__getattribute__(attr)
            return value

    @property
    def is_empty(self):
        """
        Check whether the List is empty.

        Returns
        -------
        bool
            True if the List contains no items (i.e., length is zero),
            otherwise False.
        """
        return self.total == 0

    @property
    def first(self):
        """
        Return the first element of the list.

        Raises
        ------
        ListIndexError
            If the list is empty.
        """
        if not self.is_empty:
            return self[0]

        raise ListIndexError('Can not get a first element of an empty list.')

    @property
    def last(self):
        """
        Return the last element of the list.

        Raises
        ------
        ListIndexError
            If the list is empty.
        """
        if not self.is_empty:
            return self[-1]
        raise ListIndexError('Can not get last element of an empty list.')

    @property
    def total(self):
        """
        Get the total number of elements in the list.

        This property provides a convenient way to access the length
        of the list, equivalent to calling ``len(self)``.

        Returns
        -------
        int
            The number of elements contained in the list.
        """
        return len(self)


class Result:
    """
    Container class for storing data and managing parent relationships.

    The Result class encapsulates arbitrary data and optionally links
    to a parent Result instance. It provides convenience methods and
    properties to manage hierarchical relationships between results.

    Attributes
    ----------
    data : Any
        The payload or content stored in this Result.
    parent : Result or None
        Optional parent Result instance. Defaults to None.

    Methods
    -------
    has_parent() -> bool
        True if this Result has a parent assigned, False otherwise.
    update_parent(parent: Result) -> None
        Assign a new parent Result instance.

    Raises
    ------
    ResultError
        If the provided parent is not None or an instance of Result.
    """
    def __init__(self, data, parent=None):
        self.parent = None
        self.data = data
        self.update_parent(parent)

    def update_parent(self, parent):
        """
        Update the parent reference of the current Result.

        This method assigns a new parent to the Result. The parent must be
        either an instance of `Result` (or the same class as the current
        object) or `None`. If an invalid type is provided, a `ResultError`
        is raised.

        Parameters
        ----------
        parent : Result or None
            The new parent to assign. Must be a `Result` instance (or the
            same class as `self`) or `None` to clear the parent reference.

        Raises
        ------
        ResultError
            If the provided parent is not a `Result` instance or `None`.

        Notes
        -----
        - Passing `None` removes the parent reference.
        - This method enforces type safety to ensure that only valid parent
          objects are associated with the element.
        """
        if parent is None or isinstance(parent, self.__class__):
            self.parent = parent
        else:
            msg = 'parent argument must be Result instance or None.'
            raise ResultError(msg)

    @property
    def has_parent(self):
        """
        Check whether the Result has a parent.

        A Result is considered to have a parent if its `parent`
        attribute references a valid `Result` instance.

        Returns
        -------
        bool
            True if the Result has a parent, otherwise False.
        """
        return isinstance(self.parent, Result)


class Element(Result):
    """
    The `Element` class extends `Result` and provides a unified interface
    for handling different data types (scalars, lists, dictionaries, and
    objects). Each `Element` may contain child elements if its data is
    iterable, or a scalar value if not. It supports recursive traversal,
    filtering, and lookup operations.

    Attributes
    ----------
    data : Any
        The underlying data value represented by this element.
    index : str
        The index or key associated with the element if the parent data
        is a list or dictionary. Defaults to an empty string.
    parent : Element, optional
        The parent `Element` instance in the hierarchy. Defaults to None.
    on_exception : bool
        If True, exceptions are raised during operations. If False,
        operations return gracefully without raising.
    type : str
        A string representation of the data type (e.g., "dict", "list",
        "int", "str", "object").

    Notes
    -----
    - Iterable data (lists, tuples, sets, dicts) are converted into
      child `Element` instances accessible via `children`.
    - Scalar values (int, float, bool, str, None) are stored directly
      in `value`.
    - Provides convenience properties such as `is_leaf`, `is_scalar`,
      `is_list`, and `is_dict` for type checks.
    - Supports recursive search and filtering using `find` and
      `filter_result`.
    """
    def __init__(self, data, index='', parent=None, on_exception=False):
        super().__init__(data, parent=parent)
        self.index = index
        self.type = ''
        self.on_exception = on_exception
        self._build(data)

    def __iter__(self):
        """
        Return an iterator over the element's underlying data.

        This method enables iteration (`for ... in element`) depending on
        the type of data wrapped by the element:

        - If the element represents a dictionary, iteration yields its keys.
        - If the element represents a list, iteration yields index positions
          (0 through `len(data) - 1`).
        - For all other types, iteration is not supported and a `TypeError`
          is raised.

        Returns
        -------
        iterator
            An iterator over dictionary keys or list indices, depending on
            the element type.

        Raises
        ------
        TypeError
            If the element does not represent a dictionary or list, making
            it non-iterable.
        """
        if self.type == 'dict':
            return iter(self.data.keys())
        elif self.type == 'list':
            return iter(range(len(self.data)))
        else:
            fmt = '{!r} object is not iterable.'
            msg = fmt.format(type(self).__name__)
            raise TypeError(msg)

    def __getitem__(self, index):
        """
        Retrieve an item from the element's underlying data by index or key.

        This method enables subscript notation (e.g., `element[index]`) for
        elements that wrap dictionary or list data. If the element does not
        represent a subscriptable type, a `TypeError` is raised.

        Parameters
        ----------
        index : int or str
            The position (for lists) or key (for dictionaries) used to access
            the corresponding item in the underlying data.

        Returns
        -------
        Any
            The item stored at the given index or key in the element's data.

        Raises
        ------
        TypeError
            If the element's type is not a dictionary or list, making it
            non-subscriptable.
        """
        if self.type not in ['dict', 'list']:
            fmt = '{!r} object is not subscriptable.'
            msg = fmt.format(type(self).__name__)
            raise TypeError(msg)
        result = self.data[index]
        return result

    def _build(self, data):
        """
        Construct the internal representation of an element based on its data type.

        This method initializes the `children`, `value`, and `type` attributes
        of the element depending on the nature of the provided data. Composite
        types (dicts, lists, tuples, sets) are expanded into child `Element`
        instances, while scalar and object types are stored directly as values.

        Parameters
        ----------
        data : Any
            The input data to wrap in the element. Can be a dictionary, list,
            tuple, set, scalar (int, float, bool, str, None), or any other object.

        Notes
        -----
        - If `data` is a dict:
            Each key-value pair is converted into a child `Element` with the
            key as its index. The element type is set to `"dict"`.
        - If `data` is a list, tuple, or set:
            Each item is converted into a child `Element` with an auto-generated
            index (`"__index__<i>"`). The element type is set to `"list"`.
        - If `data` is a scalar (int, float, bool, str, or None):
            The element type is set to the scalar type name, and the value is
            stored directly in `self.value`.
        - For all other types:
            The element type is set to `"object"`, and the value stores
            directly in `self.value`.

        Attributes Set
        --------------
        children : List or None
            A list of child `Element` instances if the data is composite,
            otherwise None.
        value : Any or None
            The scalar or object value if the data is non-composite,
            otherwise None.
        type : str
            A string describing the type of the data ("dict", "list",
            scalar type name, or "object").
        """
        self.children = None
        self.value = None
        if isinstance(data, dict):
            self.type = 'dict'
            lst = List()
            for index, val in data.items():
                elm = Element(val, index=index, parent=self)
                lst.append(elm)
            self.children = lst or None
        elif isinstance(data, (list, tuple, set)):
            self.type = 'list'
            lst = List()
            for i, item in enumerate(data):
                index = '__index__{}'.format(i)
                elm = Element(item, index=index, parent=self)
                lst.append(elm)
            self.children = lst or None
        elif isinstance(data, (int, float, bool, str)) or data is None:
            self.type = type(data).__name__
            self.value = data
        else:
            self.type = 'object'
            self.value = data

    @property
    def has_children(self):
        """
        Check whether the element contains child elements.

        An element is considered to have children if its underlying data
        is a composite type (e.g., list or dictionary) and child `Element`
        instances have been created during initialization.

        Returns
        -------
        bool
            True if the element has one or more children, otherwise False.
        """
        return bool(self.children)

    @property
    def is_element(self):
        """
        Check whether the element is a composite node.

        An element is considered a composite if it contains children,
        meaning it represents a nested structure (e.g., a list or dictionary).

        Returns
        -------
        bool
            True if the element has children, otherwise False.
        """
        return self.has_children

    @property
    def is_leaf(self):
        """
        Check whether the element is a leaf node.

        A leaf node is defined as an element that has no children
        (i.e., it does not contain nested elements).

        Returns
        -------
        bool
            True if the element has no children, otherwise False.
        """
        return not self.has_children

    @property
    def is_scalar(self):
        """
        Check whether the element represents a scalar value.

        Scalar values are defined here as primitive, non-iterable types:
        integers, floats, booleans, strings, or None.

        Returns
        -------
        bool
            True if the element's underlying data is a scalar type
            (int, float, bool, str, or None), otherwise False.
        """
        return isinstance(self.data, (int, float, bool, str, None))     # noqa

    @property
    def is_list(self):
        """
        Check if the element represents a list.

        Returns
        -------
        bool
            True if the element's underlying data type is a list,
            otherwise False.
        """
        return self.type == 'list'

    @property
    def is_dict(self):
        """
        Check if the element represents a dictionary.

        Returns
        -------
        bool
            True if the element's underlying data type is a dictionary,
            otherwise False.
        """
        return self.type == 'dict'

    def filter_result(self, records, select_statement):
        """
        Apply a selection filter to a list of records.

        This method parses a given select statement and filters the provided
        records accordingly. Depending on the parsed selection, it can return
        raw record data, parent data, or a subset of columns.

        Parameters
        ----------
        records : List[Element]
            A list of `Element` records to be filtered.
        select_statement : str
            A selection expression used to determine which records or fields
            should be included in the result. Parsed by `SelectParser`.

        Returns
        -------
        List
            A new `List` containing filtered results. The contents vary based
            on the select statement:
            - If a predicate is defined, only matching records are included.
            - If `is_zero_select` is True, returns the `data` of each record.
            - If `is_all_select` is True, returns the `parent.data` of each record.
            - Otherwise, returns dictionaries containing only the selected columns.

        Raises
        ------
        Exception
            If `on_exception` is True and an error occurs during parsing or
            predicate evaluation.

        Notes
        -----
        - The `SelectParser` is responsible for interpreting the select statement
          and generating a predicate function.
        - When no predicate is defined, all records are included by default.
        - Column filtering ensures missing keys are set to `None`.
        """
        result = List()
        select_obj = SelectParser(select_statement,
                                  on_exception=self.on_exception)
        select_obj.parse_statement()

        if callable(select_obj.predicate):
            lst = List()
            for record in records:
                is_found = select_obj.predicate(record.parent.data,
                                                on_exception=self.on_exception)
                if is_found:
                    lst.append(record)
        else:
            lst = records[:]

        if select_obj.is_zero_select:
            for item in lst:
                result.append(item.data)
        elif select_obj.is_all_select:
            for item in lst:
                result.append(item.parent.data)
        else:
            for item in lst:
                new_data = item.parent.data.fromkeys(select_obj.columns)
                is_added = True
                for key in new_data:
                    is_added &= key in item.parent.data
                    new_data[key] = item.parent.data.get(key, None)
                is_added and result.append(new_data)
        return result

    def find_(self, node, lookup_obj, result):
        """
        Recursively traverse an element tree to locate records matching a lookup.

        This helper method walks through the children of a given `Element`
        node, applying lookup rules to determine whether each child should
        be added to the result set. It supports both dictionary and list
        structures, and continues recursion into nested elements.

        Parameters
        ----------
        node : Element
            The current `Element` node to inspect. Must be of type dict or list
            to have children.
        lookup_obj : LookupCls
            A `LookupCls` instance that defines the matching rules. Provides
            methods such as `is_left_matched` and `is_right_matched` for
            evaluating keys and values.
        result : List
            A mutable list used to collect matching `Element` instances. This
            list is updated in place as matches are found.

        Notes
        -----
        - For list nodes, recursion continues into child elements without
          applying key/value matching.
        - For dict nodes, the child's index (key) is checked against the
          left-hand lookup condition. If matched, the right-hand condition
          (if present) is applied to the child's data.
        - Matching children are appended directly to the `result` list.
        - Recursion proceeds into child elements if they themselves contain
          nested structures.
        """
        if node.is_dict or node.is_list:
            for child in node.children:
                if node.is_list:
                    if child.is_element:
                        self.find_(child, lookup_obj, result)
                else:
                    if lookup_obj.is_left_matched(child.index):
                        if lookup_obj.is_right:
                            if lookup_obj.is_right_matched(child.data):
                                result.append(child)
                        else:
                            result.append(child)
                    if child.is_element:
                        self.find_(child, lookup_obj, result)

    def find(self, lookup, select=''):
        """
         Recursively search for elements matching a lookup expression.

         This method traverses the element tree, applying a lookup pattern
         to identify matching nodes. The results are then optionally filtered
         using a select statement to refine the output.

         Parameters
         ----------
         lookup : str
             A lookup expression or search pattern used to locate matching
             elements within the hierarchy. Parsed by `LookupCls`.
         select : str, optional
             A select statement that determines how the matched records
             should be returned (e.g., raw data, parent data, or specific
             columns). Defaults to an empty string, meaning no additional
             filtering.

         Returns
         -------
         List
             A `List` of records that match the lookup criteria. The exact
             contents depend on the select statement:
             - Without a select statement, returns matching `Element` records.
             - With `is_zero_select`, returns the `data` of each record.
             - With `is_all_select`, returns the `parent.data` of each record.
             - With column selection, returns dictionaries containing only
               the specified columns.

         Notes
         -----
         - Internally, this method delegates recursive traversal to `find_`.
         - Filtering and projection of results are handled by `filter_result`.
         - Useful for querying nested structures such as lists and dictionaries.
         """
        records = List()
        lkup_obj = LookupCls(lookup)
        self.find_(self, lkup_obj, records)
        result = self.filter_result(records, select)
        return result


class ObjectDict(dict):
    """The ObjectDict can retrieve value of key as attribute style."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    ############################################################################
    # Special methods
    ############################################################################
    def __getattribute__(self, attr):
        try:
            value = super().__getattribute__(attr)
            return value
        except Exception as ex:
            if attr in self:
                return self[attr]
            else:
                raise ex

    def __setitem__(self, key, value):
        new_value = self._build(value)
        super().__setitem__(key, new_value)

    def __setattr__(self, attr, value):
        new_value = self._build(value)
        if attr in self:
            self[attr] = new_value
        else:
            super().__setattr__(attr, new_value)

    ############################################################################
    # Private methods
    ############################################################################
    def _build(self, value, forward=True):
        """The function to recursively build a ObjectDict instance
        when the value is the dict instance.

        Parameters
        ----------
        value (Any): The value to recursively build a ObjectDict
                instance when value is the dict instance.
        forward (boolean): set flag to convert dict instance to ObjectDict
                instance or vice versa.  Default is True.
        Returns
        -------
        Any: the value or a new value.
        """
        if isinstance(value, (dict, list, set, tuple)):
            if isinstance(value, ObjectDict):
                if forward:
                    return value
                else:
                    result = dict([i, self._build(j, forward=forward)] for i, j in value.items())  # noqa
                    return result
            elif isinstance(value, dict):
                lst = [[i, self._build(j, forward=forward)] for i, j in value.items()]
                if forward:
                    result = self.__class__(lst)
                    return result
                else:
                    result = dict(lst)      # noqa
                    return result
            elif isinstance(value, list):
                lst = [self._build(item, forward=forward) for item in value]
                return lst
            elif isinstance(value, set):
                lst = [self._build(item, forward=forward) for item in value]
                return set(lst)
            else:
                tuple_obj = (self._build(item, forward=forward) for item in value)
                return tuple_obj
        else:
            return value

    ############################################################################
    # class methods
    ############################################################################
    @classmethod
    def create_from_json_file(cls, filename, **kwargs):
        """Create a ObjectDict instance from JSON file.

        Parameters
        ----------
        filename (str): YAML file.
        kwargs (dict): the keyword arguments.

        Returns
        -------
        Any: any data
        """
        from io import IOBase
        if isinstance(filename, IOBase):
            obj = json.load(filename, **kwargs)
        else:
            with open(filename, encoding="utf-8") as stream:
                obj = json.load(stream, **kwargs)

        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_json_data(cls, data, **kwargs):
        obj = json.loads(data, **kwargs)
        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_yaml_file(cls, filename, loader=yaml.SafeLoader):
        """Create a ObjectDict instance from YAML file.

        Parameters
        ----------
        filename (str): YAML file.
        loader (yaml.loader.Loader): YAML loader.

        Returns
        -------
        Any: any data
        """
        from io import IOBase
        if isinstance(filename, IOBase):
            obj = yaml.load(filename, Loader=loader)    # noqa
        else:
            with open(filename, encoding="utf-8") as stream:
                obj = yaml.load(stream, Loader=loader)

        obj_dict = ObjectDict(obj)
        return obj_dict

    @classmethod
    def create_from_yaml_data(cls, data, loader=yaml.SafeLoader):
        """Create a ObjectDict instance from YAML data.

        Parameters
        ----------
        data (str): YAML data.
        loader (yaml.loader.Loader): YAML loader.

        Returns
        -------
        Any: Any data
        """
        obj = yaml.load(data, Loader=loader)
        obj_dict = ObjectDict(obj)
        return obj_dict

    ############################################################################
    # public methods
    ############################################################################
    def update(self, *args, **kwargs):
        """Update data to ObjectDict."""
        obj = dict(*args, **kwargs)
        new_obj = dict()
        for key, value in obj.items():
            new_obj[key] = self._build(value)
        super().update(new_obj)

    def deep_apply_attributes(self, node=None, **kwargs):
        """Recursively apply attributes to ObjectDict instance.

        Parameters
        ---------
        node (ObjectDict): a `ObjectDict` instance
        kwargs (dict): keyword arguments
        """

        def assign(node_, **kwargs_):
            for key, val in kwargs_.items():
                setattr(node_, key, val)

        def apply(node_, **kwargs_):
            if isinstance(node_, (dict, list, set, tuple)):
                if isinstance(node_, dict):
                    if isinstance(node_, self.__class__):
                        assign(node_, **kwargs_)
                    for value in node_.values():
                        apply(value, **kwargs_)
                else:
                    for item in node_:
                        apply(item, **kwargs_)

        node = self if node is None else node
        validate_argument_type(self.__class__, node=node)
        apply(node, **kwargs)

    def to_dict(self, data=None):
        """Convert a given data to native dictionary

        Parameters
        ----------
        data (ObjectDict): a dynamic dictionary instance.
            if data is None, it will convert current instance to dict.

        Returns
        -------
        dict: dictionary
        """
        if data is None:
            data = dict(self)

        validate_argument_type(dict, data=data)
        result = self._build(data, forward=False)
        return result

    todict = to_dict


class LookupCls:
    """
    Utility class for constructing and parsing lookup expressions.

    The `LookupCls` provides a flexible mechanism to define search
    criteria for dictionary-like structures. A lookup expression
    consists of two parts:
    - A **left lookup**: matches dictionary keys (supports text,
      wildcard, or regex).
    - A **right lookup**: matches dictionary values (supports text,
      wildcard, regex, or callable predicates).

    Attributes
    ----------
    lookup : str
        The raw lookup expression provided by the user.
    left : str
        The parsed left-hand lookup used to match dictionary keys.
        Typically a string or regular expression.
    right : str or callable
        The parsed right-hand lookup used to match dictionary values.
        Can be a string, regex pattern, or a callable predicate
        function.

    Notes
    -----
    Supported lookup forms include:

    1. ``lookup='abc'``
       - Left lookup: matches keys named "abc".
       - Right lookup: empty (no value check).

    2. ``lookup='abc=xyz'``
       - Left lookup: matches keys named "abc".
       - Right lookup: matches values equal to "xyz".

    3. ``lookup='=xyz'``
       - Left lookup: empty (matches all keys).
       - Right lookup: matches values equal to "xyz".

    4. ``lookup='abc=_wildcard(*xyz*)'``
       - Left lookup: matches keys named "abc".
       - Right lookup: matches values containing "xyz" via wildcard.

    Both left and right lookups support:
    - Plain text
    - Wildcards (e.g., ``_wildcard(*xyz*)``)
    - Regex (e.g., ``_regex(.*xyz.*)``)
    - Case-insensitive variants (``_iwildcard``, ``_iregex``)

    Examples of valid combinations:
    - ``abc=_wildcard(*xyz*)``
    - ``abc=_iregex(.*xyz.*)``
    - ``_wildcard([Aa][Bb]c)=_regex(.*xyz.*)``
    - ``=ipv4_address()``

    The right lookup also supports custom keywords such as:
    - ``empty`` / ``not_empty``
    - ``ip_address``, ``ipv4_address``, ``ipv6_address``
    - ``date``, ``datetime``, ``time``
    """
    def __init__(self, lookup):
        self.lookup = str(lookup)
        self.left = None
        self.right = None
        self.process()

    @property
    def is_right(self):
        """
        Check whether the lookup expression includes a right-hand component.

        The right-hand lookup represents the value-matching part of a
        lookup expression. It may be defined as a string, regular
        expression, or callable predicate. This property evaluates to
        True if such a component exists, and False otherwise.

        Returns
        -------
        bool
            True if the lookup has a right-hand component, otherwise False.
        """
        return bool(self.right)

    @classmethod
    def parse(cls, text):
        """
        Parse a lookup expression into a regular expression pattern or validation function.

        This method interprets a lookup string and converts it into either:
        - A compiled regular expression pattern (for text, wildcard, or regex lookups).
        - A callable predicate function (for custom validations or comparison operators).

        Parameters
        ----------
        text : str
            The lookup expression to parse. Examples include:
            - "_regex(.*xyz.*)"
            - "_wildcard(*abc*)"
            - "is_empty()"
            - "lt(10)"

        Returns
        -------
        str or callable
            A regular expression pattern string if the lookup is regex/wildcard/text-based,
            or a callable function if the lookup corresponds to a custom validation or
            comparison operator.

        Raises
        ------
        LookupClsError
            If the lookup expression cannot be parsed into a valid pattern or function.
        """
        def parse_(text_):
            """
            Inner helper method of `LookupCls.parse`

            This function parses a lookup expression that uses one of the
            supported methods: "text", "wildcard", or "regex". It also
            supports the optional "i" flag for case-insensitive matching.

            Parameters
            ----------
            text_ : str
                A lookup expression containing one of the supported methods:
                "text", "wildcard", or "regex". May include the "i" option
                for case-insensitive matching.

            Returns
            -------
            tuple
                A tuple containing:
                - pattern (str): The converted regular expression pattern.
                - ignorecase (bool): True if case-insensitive matching is requested.
            """
            vpat = '''
                _(?P<options>i?)                    # options
                (?P<method>text|wildcard|regex)     # method is wildcard or regex
                [(]
                (?P<pattern>.+)                     # wildcard or regex pattern
                [)]
            '''
            match_ = re.search(vpat, text_, re.VERBOSE)
            options_ = match_.group('options').lower()
            method_ = match_.group('method').lower()
            pattern_ = match_.group('pattern')

            ignorecase_ = 'i' in options_
            if method_ == 'wildcard':
                pattern_ = utils.convert_wildcard_to_regex(pattern_)
            elif method_ == 'text':
                pattern_ = re.escape(pattern_)
            return pattern_, ignorecase_

        def parse_other_(text_):
            """
            Inner helper method of `LookupCls.parse` used to parse custom
            validation or comparison lookup expressions.

            This function handles lookup expressions that are not based on
            regex, wildcard, or text patterns. Instead, it supports custom
            keywords (e.g., "is_empty()") and comparison operators
            (e.g., "lt(10)", "eq(value)").

            Parameters
            ----------
            text_ : str
                The lookup expression to parse.

            Returns
            -------
            callable or str
                A callable predicate function for custom validations or
                comparisons, or a regex pattern string if no match is found.

            Notes
            -----
            Supported custom validations include:
            - is_empty(), is_not_empty()
            - is_ip_address(), is_not_ip_address()
            - is_ipv4_address(), is_ipv6_address()
            - is_date(), is_datetime(), is_time()
            - is_true(), is_false(), etc.

            Supported comparison operators include:
            - lt(), le(), gt(), ge(), eq(), ne()
            """
            vpat1_ = '''
                (?i)(?P<custom_name>
                is_empty|is_not_empty|
                is_mac_address|is_not_mac_address|
                is_ip_address|is_not_ip_address|
                is_ipv4_address|is_not_ipv4_address|
                is_ipv6_address|is_not_ipv6_address|
                is_date|is_datetime|is_time|
                is_true|is_not_true|
                is_false|is_not_false)
                [(][)]$
            '''
            vpat2_ = '''
                (?i)(?P<op>lt|le|gt|ge|eq|ne)
                [(]
                (?P<other>([0-9]+)?[.]?[0-9]+)
                [)]$
            '''
            vpat3_ = '''
                (?i)(?P<op>eq|ne)
                [(]
                (?P<other>.*[^0-9].*)
                [)]$
            '''
            data_ = text_.lower()
            match1_ = re.match(vpat1_, data_, flags=re.VERBOSE)
            if match1_:
                custom_name = match1_.group('custom_name')
                valid = False if '_not_' in custom_name else True
                custom_name = custom_name.replace('not_', '')
                method = getattr(CustomValidation, custom_name)
                pfunc = partial(method, valid=valid, on_exception=False)
                return pfunc
            else:
                match2_ = re.match(vpat2_, data_, flags=re.VERBOSE)
                if match2_:
                    op = match2_.group('op')
                    other = match2_.group('other')
                    pfunc = partial(
                        OpValidation.compare_number,
                        op=op, other=other, on_exception=False
                    )
                    return pfunc
                else:
                    match3_ = re.match(vpat3_, data_, flags=re.VERBOSE)
                    if match3_:
                        op = match3_.group('op')
                        other = match3_.group('other')
                        pfunc = partial(
                            OpValidation.compare,
                            op=op, other=other, on_exception=False
                        )
                        return pfunc
                    else:
                        pattern_ = '^{}$'.format(re.escape(text_))
                        return pattern_

        pat = r'_i?(text|wildcard|regex)[(].+[)]'

        if not re.search(pat, text):
            result = parse_other_(text)
            return result
        lst = []
        start = 0
        is_ignorecase = False
        for node in re.finditer(pat, text):
            predata = text[start:node.start()]
            lst.append(re.escape(predata))
            data = node.group()
            pattern, ignorecase = parse_(data)
            lst.append(pattern)
            start = node.end()
            is_ignorecase |= ignorecase
        else:
            if lst:
                postdata = text[start:]
                lst.append(re.escape(postdata))

        pattern = ''.join(lst)
        if pattern:
            ss = '' if pattern[0] == '^' else '^'
            es = '' if pattern[-1] == '$' else '$'
            ic = '(?i)' if is_ignorecase else ''
            pattern = '{}{}{}{}'.format(ic, ss, pattern, es)
            return pattern
        else:
            fmt = 'Failed to parse this lookup : {!r}'
            raise LookupClsError(fmt.format(text))

    def process(self):
        """
        Parse the lookup string into left and right expressions.

        This method splits the raw lookup expression into two parts:
        - **Left expression**: Used to match dictionary keys.
        - **Right expression**: Used to match dictionary values.

        The left part is always parsed if present. If the lookup string
        also contains a right-hand expression (after the "=" sign), it
        is parsed and assigned to `self.right`. If no right-hand part
        exists, `self.right` remains None.

        Notes
        -----
        Examples of lookup parsing:
        - "abc" → left="abc", right=None
        - "abc=xyz" → left="abc", right="xyz"
        - "=regex(.*2021.*)" → left=None, right=regex pattern
        """

        left, *lst = self.lookup.split('=', maxsplit=1)
        left = left.strip()
        if left:
            self.left = self.parse(left)
        if lst:
            self.right = self.parse(lst[0])

    def is_left_matched(self, data):
        """
        Determine whether the given input string matches the left-hand lookup expression.

        The left-hand expression is used to match dictionary keys. If defined,
        this method applies the compiled regex pattern to the provided string.
        If no left-hand expression exists, the result depends on whether a
        right-hand expression is defined:
        - If `self.right` exists, the method returns True (all keys are considered matched).
        - If neither left nor right is defined, the method returns False.

        Parameters
        ----------
        data : str
            The input string (typically a dictionary key) to test against
            the left-hand lookup expression.

        Returns
        -------
        bool
            True if the input matches the left-hand expression, or if no
            left-hand expression exists but a right-hand expression is defined.
            False otherwise.

        Notes
        -----
        - Non-string inputs always return False.
        - Matching is performed using `re.search` against the parsed left
          expression if available.
        """
        if not isinstance(data, str):
            return False

        if self.left:
            result = re.search(self.left, data)
            return bool(result)
        else:
            return True if self.right else False

    def is_right_matched(self, data):
        """
        Determine whether the given input matches the right-hand lookup expression.

        The right-hand expression is used to match dictionary values. If no
        right-hand expression is defined, this method returns True (all values
        are considered matched). If defined, the behavior depends on the type
        of `self.right`:

        - If `self.right` is a callable, it is invoked with the input `data`
          and its result is returned.
        - If `self.right` is a regex pattern string, the input must be a string
          and is tested against the pattern using `re.search`.
        - If `data` is not a string when a regex pattern is expected, the method
          returns False.

        Parameters
        ----------
        data : Any
            The input value to test against the right-hand lookup expression.
            Must be a string if `self.right` is a regex pattern.

        Returns
        -------
        bool
            True if the input matches the right-hand expression, or if no
            right-hand expression is defined. False otherwise.

        Notes
        -----
        - When `self.right` is callable, any type of input may be supported
          depending on the predicate function.
        - When `self.right` is a regex pattern, non-string inputs always
          return False.
        """
        if not self.right:
            return True
        else:
            if callable(self.right):
                result = self.right(data)
                return result
            else:
                if not isinstance(data, str):
                    return False
                result = re.search(self.right, data)
                return bool(result)


class Object:
    """
    Utility class for constructing objects with positional and keyword arguments.

    The Object class provides a flexible way to store and manage
    initialization arguments. It validates that positional arguments
    meet expected requirements and raises errors when invalid data
    is provided.

    Attributes
    ----------
    args (list): a position arguments.
    kwargs (dict): a keyword arguments.

    Raises
    ------
    ObjectArgumentError: Raised if any positional argument is not a dictionary instance.
    """
    def __init__(self, *args, **kwargs):
        errors = []
        for index, arg in enumerate(args, 1):
            if not isinstance(arg, dict):
                errors.append(index)
            else:
                self.__dict__.update(arg)
        if errors:
            if len(errors) == 1:
                fmt = 'a position argument #{} is not a dictionary.'
                msg = fmt.format(errors[0])
            else:
                fmt = 'position arguments # {} are not a dictionary'
                msg = fmt.format(tuple(errors))
            raise ObjectArgumentError(msg)
        self.__dict__.update(kwargs)

    def __len__(self):
        """
        Return the number of attributes stored in the object.

        Returns
        -------
        int
            The number of attributes currently defined in the object.
        """
        return len(self.__dict__)

    def __bool__(self):
        """
        Evaluate the truthiness of the object.

        An `Object` instance is considered truthy if it contains
        one or more attributes, and falsy if it is empty.

        Returns
        -------
        bool
            True if the object has attributes, False otherwise.
        """
        return len(self) > 0
