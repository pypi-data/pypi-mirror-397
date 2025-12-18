"""Factory functions for creating dictlistlib instances.

This module provides helper functions to construct `DLQuery` objects
from different data sources and formats, including JSON, YAML, and CSV.
It abstracts away the parsing logic and ensures that the resulting
objects are wrapped in a `DLQuery` instance for querying.

Supported Sources
-----------------
- JSON files and raw JSON strings
- YAML files and raw YAML strings
- CSV files and raw CSV strings

Each function returns a `DLQuery` instance initialized with the parsed
data, ready for query operations.
"""

import yaml
import json
import csv
from dictlistlib import DLQuery


def create_from_json_file(filename, **kwargs):
    """
    Create a `DLQuery` instance from a JSON file.

    Parameters
    ----------
    filename : str or IOBase
        Path to a JSON file or an open file-like object.
    **kwargs : dict
        Additional keyword arguments passed to `json.load`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed JSON data.
    """
    from io import IOBase
    if isinstance(filename, IOBase):
        obj = json.load(filename, **kwargs)
    else:
        with open(filename, encoding="utf-8") as stream:
            obj = json.load(stream, **kwargs)

    query_obj = DLQuery(obj)
    return query_obj


def create_from_json_data(data, **kwargs):
    """
    Create a `DLQuery` instance from a JSON string.

    Parameters
    ----------
    data : str
        JSON data in string format.
    **kwargs : dict
        Additional keyword arguments passed to `json.loads`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed JSON data.
    """
    obj = json.loads(data, **kwargs)
    query_obj = DLQuery(obj)
    return query_obj


def create_from_yaml_file(filename, loader=yaml.SafeLoader):
    """
    Create a `DLQuery` instance from a YAML file.

    Parameters
    ----------
    filename : str
        Path to a YAML file.
    loader : yaml.loader.Loader, optional
        YAML loader to use. Default is `yaml.SafeLoader`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed YAML data.
    """
    with open(filename, encoding="utf-8") as stream:
        obj = yaml.load(stream, Loader=loader)
        query_obj = DLQuery(obj)
        return query_obj


def create_from_yaml_data(data, loader=yaml.SafeLoader):
    """
    Create a `DLQuery` instance from a YAML string.

    Parameters
    ----------
    data : str
        YAML data in string format.
    loader : yaml.loader.Loader, optional
        YAML loader to use. Default is `yaml.SafeLoader`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed YAML data.
    """
    obj = yaml.load(data, Loader=loader)
    query_obj = DLQuery(obj)
    return query_obj


def create_from_csv_file(filename, fieldnames=None, restkey=None,
                         restval=None, dialect='excel', *args, **kwds):
    """
    Create a `DLQuery` instance from a CSV file.

    Parameters
    ----------
    filename : str
        Path to a CSV file.
    fieldnames : list, optional
        List of keys for the dictionary rows.
    restkey : str, optional
        Key to capture extra values in long rows.
    restval : Any, optional
        Default value for missing fields in short rows.
    dialect : str, optional
        CSV dialect. Default is 'excel'.
    *args : tuple
        Additional positional arguments for `csv.DictReader`.
    **kwds : dict
        Additional keyword arguments for `csv.DictReader`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed CSV data.
    """
    with open(filename, newline='', encoding="utf-8") as stream:
        csv_reader = csv.DictReader(
            stream, fieldnames=fieldnames, restkey=restkey,
            restval=restval, dialect=dialect, *args, **kwds
        )
        lst_of_dict = [row for row in csv_reader]
        query_obj = DLQuery(lst_of_dict)
        return query_obj


def create_from_csv_data(data, fieldnames=None, restkey=None,
                         restval=None, dialect='excel', *args, **kwds):
    """
    Create a `DLQuery` instance from a CSV string.

    Parameters
    ----------
    data : str
        CSV data in string format.
    fieldnames : list, optional
        List of keys for the dictionary rows.
    restkey : str, optional
        Key to capture extra values in long rows.
    restval : Any, optional
        Default value for missing fields in short rows.
    dialect : str, optional
        CSV dialect. Default is 'excel'.
    *args : tuple
        Additional positional arguments for `csv.DictReader`.
    **kwds : dict
        Additional keyword arguments for `csv.DictReader`.

    Returns
    -------
    DLQuery
        A `DLQuery` instance containing the parsed CSV data.
    """
    from io import StringIO
    data = str(data).strip()
    stream = StringIO(data)
    csv_reader = csv.DictReader(
        stream, fieldnames=fieldnames, restkey=restkey,
        restval=restval, dialect=dialect, *args, **kwds
    )
    lst_of_dict = [row for row in csv_reader]
    query_obj = DLQuery(lst_of_dict)
    return query_obj
