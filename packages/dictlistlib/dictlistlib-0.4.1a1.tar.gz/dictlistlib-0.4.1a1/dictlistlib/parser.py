"""Parsing utility for dictlistlib.

This module provides logic for interpreting simplified SQL-like
`SELECT` statements used within dictlistlib. It supports parsing
column definitions, validating syntax, and constructing predicate
functions for filtering data. The parser is designed to work with
dictlistlib’s query engine, enabling flexible selection and filtering
of dictionary-based datasets.

Classes
-------
SelectParser
    A parser for SQL-like SELECT statements that extracts column
    references and builds predicate functions for filtering.
"""

import re
import logging
from functools import partial
from dictlistlib.predicate import Predicate


logger = logging.getLogger(__file__)


class SelectParser:
    """
    Parser for SQL-like SELECT statements.

    This class provides functionality to interpret and validate
    simplified SELECT statements, manage column definitions,
    and construct predicate functions for filtering data.

    Attributes
    ----------
    select_statement : str
        The raw SELECT statement to be parsed.
    columns : list
        List of column names referenced in the statement.
    predicate : callable
        A function used to evaluate filtering conditions.
    logger : logging.Logger
        Logger instance for reporting parsing activity and errors.
    on_exception : bool
        If True, raise an Exception on errors; otherwise return False.

    Methods
    -------
    is_zero_select() -> bool
        Indicates whether the SELECT statement returns zero columns.
    is_all_select() -> bool
        Indicates whether the SELECT statement requests all columns.
    get_predicate(expression) -> callable
        Build and return a predicate function from the given expression.
    build_predicate() -> callable
        Construct the predicate function based on the parsed statement.
    parse_statement() -> None
        Parse the SELECT statement and populate attributes accordingly.
    """
    def __init__(self, select_statement, on_exception=True):
        self.select_statement = select_statement
        self.columns = [None]
        self.left_operands = []
        self.predicate = None
        self.logger = logger
        self.on_exception = on_exception

    @property
    def is_zero_select(self):
        """
        Check whether the SELECT statement specifies zero columns.

        This property evaluates the parsed `columns` attribute and
        returns True if no column has been selected (represented
        internally as `[None]`).

        Returns
        -------
        bool
            True if no column is selected, otherwise False.
        """
        return self.columns == [None]

    @property
    def is_all_select(self):
        """
        Check whether the SELECT statement requests all columns.

        This property evaluates the parsed `columns` attribute and
        returns True if it is an empty list (`[]`), which internally
        represents a `SELECT *` operation (i.e., selecting all columns).

        Returns
        -------
        bool
            True if all columns are selected, otherwise False.
        """
        return self.columns == []

    def get_predicate(self, expression):
        """
        Build a predicate function from an expression.

        This method parses a given expression string and converts it
        into a callable predicate function that can be applied to
        dictionary-based records. The expression may represent either
        a left-hand or right-hand condition in a simplified SQL-like
        `WHERE` clause.

        Parameters
        ----------
        expression : str
            A filtering expression to be parsed. Can represent either
            a left-hand or right-hand condition (e.g., `"age > 30"`,
            `"name == 'Alice'"`).

        Returns
        -------
        callable
            A predicate function that evaluates the given expression
            against a record (dict). Returns True if the record satisfies
            the condition, otherwise False.
        """
        pattern = '''(?i)["'](?P<key>.+)['"] +(?P<op>\\S+) +(?P<value>.+)'''
        match = re.match(pattern, expression)
        if match:
            key = match.group('key').strip()
            op = match.group('op').strip()
            value = match.group('value').strip()
        else:
            key, op, value = [i.strip() for i in re.split(r' +', expression, maxsplit=2)]

        key = key.replace('_COMMA_', ',')
        op = op.lower()
        value = value.replace('_COMMA_', ',')

        key not in self.left_operands and self.left_operands.append(key)

        tbl1 = {'lt': 'lt', 'le': 'le', '<': 'lt', '<=': 'le',
                'less_than': 'lt', 'less_than_or_equal': 'le',
                'less_than_or_equal_to': 'le', 'equal_or_less_than': 'le',
                'equal_to_or_less_than': 'le',
                'gt': 'gt', 'ge': 'ge', '>': 'gt', '>=': 'ge',
                'greater_than': 'gt', 'greater_than_or_equal': 'ge',
                'greater_than_or_equal_to': 'ge', 'equal_or_greater_than': 'ge',
                'equal_to_or_greater_than': 'ge'}

        tbl2 = {'eq': 'eq', '==': 'eq', 'equal': 'eq', 'equal_to': 'eq',
                'ne': 'ne', '!=': 'ne', 'not_equal': 'ne', 'not_equal_to': 'ne'}

        if op == 'is':
            func = partial(Predicate.is_, key=key, custom=value,
                           on_exception=self.on_exception)
        elif op in ['is_not', 'isnot']:
            func = partial(Predicate.isnot, key=key, custom=value,
                           on_exception=self.on_exception)
        elif op in tbl1:
            op = tbl1.get(op)
            val = str(value).strip()
            pattern = r'''
                (?i)((?P<semantic>semantic)_)?
                version[(](?P<expected_version>.+)[)]$
            '''
            match_version = re.match(pattern, val, flags=re.VERBOSE)

            pattern = r'(?i)(datetime|date|time)[(](?P<datetime_str>.+)[)]$'
            match_datetime = re.match(pattern, val)

            if match_version:
                semantic = match_version.group('semantic')
                expected_version = match_version.group('expected_version')
                if not semantic:
                    func = partial(Predicate.compare_version, key=key,
                                   op=op, other=expected_version,
                                   on_exception=self.on_exception)
                else:
                    func = partial(Predicate.compare_semantic_version,
                                   key=key, op=op, other=expected_version,
                                   on_exception=self.on_exception)
            elif match_datetime:
                datetime_str = match_datetime.group('datetime_str')
                func = partial(Predicate.compare_datetime, key=key,
                               op=op, other=datetime_str,
                               on_exception=self.on_exception)
            else:
                func = partial(Predicate.compare_number, key=key,
                               op=op, other=value)
        elif op in tbl2:
            op = tbl2.get(op)
            val = str(value).strip()
            pattern = r'''
                (?i)((?P<semantic>semantic)_)?
                version[(](?P<expected_version>.+)[)]$
            '''
            match_version = re.match(pattern, val, flags=re.VERBOSE)

            pattern = r'(?i)(datetime|date|time)[(](?P<datetime_str>.+)[)]$'
            match_datetime = re.match(pattern, val)

            if match_version:
                semantic = match_version.group('semantic')
                expected_version = match_version.group('expected_version')
                if not semantic:
                    func = partial(Predicate.compare_version, key=key,
                                   op=op, other=expected_version,
                                   on_exception=self.on_exception)
                else:
                    func = partial(Predicate.compare_semantic_version,
                                   key=key, op=op, other=expected_version,
                                   on_exception=self.on_exception)
            elif match_datetime:
                datetime_str = match_datetime.group('datetime_str')
                func = partial(Predicate.compare_datetime, key=key,
                               op=op, other=datetime_str,
                               on_exception=self.on_exception)
            else:
                try:
                    float(value)
                    func = partial(Predicate.compare_number,
                                   key=key, op=op, other=value,
                                   on_exception=self.on_exception)
                except Exception as ex:     # noqa
                    func = partial(Predicate.compare,
                                   key=key, op=op, other=value,
                                   on_exception=self.on_exception)
        elif op == 'match':
            func = partial(Predicate.match, key=key, pattern=value,
                           on_exception=self.on_exception)
        elif op in ['not_match', 'notmatch']:
            func = partial(Predicate.notmatch, key=key, pattern=value,
                           on_exception=self.on_exception)
        elif op in ['contain', 'contains']:
            func = partial(Predicate.contain, key=key, other=value,
                           on_exception=self.on_exception)
        elif re.match('not_?contains?', op, re.I):
            func = partial(Predicate.notcontain, key=key, other=value,
                           on_exception=self.on_exception)
        elif op in ['belong', 'belongs']:
            func = partial(Predicate.belong, key=key, other=value,
                           on_exception=self.on_exception)
        elif re.match('not_?belongs?', op, re.I):
            func = partial(Predicate.notbelong, key=key, other=value,
                           on_exception=self.on_exception)
        else:
            msg = (
                '*** Return False because of an unsupported {!r} logical '
                'operator.  Contact developer to support this case.'
            ).format(op)
            self.logger.info(msg)
            func = partial(Predicate.false)
        return func

    def build_predicate(self, expressions):
        """
        Construct a predicate function from one or more expressions.

        This method parses the provided expression(s) and builds a
        callable predicate function that can be applied to dictionary-based
        records. The resulting function evaluates whether a record
        satisfies the conditions defined in the expression(s).

        Parameters
        ----------
        expressions : str or list of str
            A single expression (e.g., `"age > 30"`) or multiple expressions
            (e.g., `["age > 30", "name == 'Alice'"]`) to be combined into
            a predicate.

        Returns
        -------
        callable
            A predicate function that evaluates the given expression(s)
            against a record (dict). Returns True if the record satisfies
            all conditions, otherwise False.
        """
        def chain(data_, a_=None, b_=None, op_='', on_exception=False):
            try:
                result_a, result_b = a_(data_), b_(data_)
                if op_ in ['or_', '||']:
                    return result_a or result_b
                elif op_ in ['and_', '&&']:
                    return result_a and result_b
                else:
                    msg_ = (
                        '* Return False because of an unsupported {!r} logical '
                        'operator.  Contact developer to support this case.'
                    ).format(op_)
                    self.logger.info(msg_)
                    return Predicate.false(data_)
            except Exception as ex:
                if on_exception:
                    raise ex
                else:
                    return Predicate.false(data_)

        groups = []
        start = 0
        match = None
        for match in re.finditer(' +(or_|and_|&&|[|]{2}) +', expressions, flags=re.I):
            expr = match.string[start:match.start()]
            op = match.group().strip().lower()
            groups.extend([expr.strip(), op.strip()])
            start = match.end()
        else:
            if groups and match:
                expr = match.string[match.end():].strip()
                groups.append(expr)

        if groups:
            total = len(groups)
            if total % 2 == 1 and total > 2:
                result = self.get_predicate(groups[0])
                for case, expr in zip(groups[1:-1:2], groups[2::2]):
                    func_b = self.get_predicate(expr)
                    result = partial(chain, a_=result, b_=func_b, op_=case,
                                     on_exception=self.on_exception)
                return result
            else:
                msg = (
                    '* Return False because of an invalid {!r} '
                    'expression.  Contact developer for this case.'
                ).format(expressions)
                self.logger.info(msg)
                result = partial(Predicate.false)
                return result
        else:
            return self.get_predicate(expressions)

    def parse_statement(self):
        """
        Parse and analyze the SELECT statement.

        This method interprets the raw `select_statement` string,
        extracts column definitions, and constructs the associated
        predicate function for filtering records. It updates the
        parser’s internal state (`columns` and `predicate`) based
        on the parsed statement.

        Workflow
        --------
        1. Tokenize and validate the SELECT statement.
        2. Identify column references (e.g., `name`, `age`).
        3. Parse any filtering expressions (e.g., `age > 30`).
        4. Build a callable predicate function for evaluation.
        5. Store results in `self.columns` and `self.predicate`.

        Returns
        -------
        None
            Updates internal attributes (`columns`, `predicate`)
            with parsed results.
        """
        statement = self.select_statement

        if statement == '':
            return

        if ' where ' in statement.lower():
            select, expressions = re.split(
                ' +where +', statement, maxsplit=1, flags=re.I
            )
            select, expressions = select.strip(), expressions.strip()
            select = re.sub('^ *select +', '', select, flags=re.I).strip()
        elif statement.lower().startswith('where'):
            select = None
            expressions = re.sub('^where +', '', statement, flags=re.I)

        else:
            select = re.sub('^ *select +', '', statement, flags=re.I).strip()
            expressions = None

        if select:
            if re.match(r'(?i) *([*]|_+all_+) *$', select):
                self.columns = []
            else:
                self.columns = re.split(' *, *', select.strip(), flags=re.I)

        if expressions:
            self.predicate = self.build_predicate(expressions)
