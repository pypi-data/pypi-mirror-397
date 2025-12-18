"""Entry-point logic for dictlistlib.

This module defines the console and GUI entry-points for the dictlistlib
application. It provides functions for running tutorials, launching the
GUI, displaying dependencies, showing version information, and executing
the command-line interface (CLI).

Classes
-------
Cli
    Encapsulates the dictlistlib console CLI, including argument parsing,
    validation, and execution of queries.

Functions
---------
run_tutorial(options)
    Run a selected dictlistlib tutorial from the console.
run_gui_application(options)
    Launch the dictlistlib GUI application.
show_dependency(options)
    Display package dependencies and system information.
show_version(options)
    Display the current dictlistlib version.
execute()
    Execute the dictlistlib console CLI.
"""

import sys
import argparse
from os import path
from dictlistlib.application import Application
from dictlistlib import create_from_csv_file
from dictlistlib import create_from_json_file
from dictlistlib import create_from_yaml_file

from dictlistlib.utils import print_data_as_tabular

import dictlistlib.tutorial as tu

from dictlistlib.constant import ECODE


def run_tutorial(options):
    """
    Run a selected dictlistlib console tutorial.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `tutorial` flag.

    Returns
    -------
    None
        Executes the requested tutorial and terminates the process
        with ``sys.exit(ECODE.SUCCESS)``.
    """
    tutorial = options.tutorial.lower()

    if tutorial not in ['base', 'csv', 'json', 'yaml']:
        return None

    tutorial == 'base' and tu.show_tutorial_dlquery()
    tutorial == 'csv' and tu.show_tutorial_csv()
    tutorial == 'json' and tu.show_tutorial_json()
    tutorial == 'yaml' and tu.show_tutorial_yaml()
    sys.exit(ECODE.SUCCESS)


def run_gui_application(options):
    """
    Launch the dictlistlib GUI application.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `gui` flag.

    Returns
    -------
    None
        Runs the GUI application and terminates the process
        with ``sys.exit(ECODE.SUCCESS)`` if `--gui` is specified.
    """
    if options.gui:
        app = Application()
        app.run()
        sys.exit(ECODE.SUCCESS)


def show_dependency(options):
    """
    Display dictlistlib dependencies and system information.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `dependency` flag.

    Returns
    -------
    None
        Prints dependency information and terminates the process
        with ``sys.exit(ECODE.SUCCESS)`` if `--dependency` is specified.
    """
    if options.dependency:
        from platform import uname, python_version
        from dictlistlib.utils import Printer
        from dictlistlib.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        Printer.print(lst)
        sys.exit(ECODE.SUCCESS)


def show_version(options):
    """
    Display the current dictlistlib version and exit.

    This function checks whether the `--version` flag was provided
    in the parsed CLI options. If so, it imports the `version`
    string from the `dictlistlib` package, prints it to stdout, and
    terminates the process with a success exit code.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed command-line options. Must contain the `version` flag.

    Returns
    -------
    None
        Prints the application version and terminates the process
        with ``sys.exit(ECODE.SUCCESS)`` if `--version` is specified.
    """
    if options.version:
        from dictlistlib import version
        print(f'dictlistlib {version}')
        sys.exit(ECODE.SUCCESS)


class Cli:
    """
    dictlistlib console CLI application.

    This class encapsulates the command-line interface for dictlistlib.
    It defines argument parsing, validation, and execution logic for
    running queries against JSON, YAML, or CSV files.

    Attributes
    ----------
    filename : str
        The input filename provided via CLI.
    filetype : str
        The type of file (`csv`, `json`, `yaml`, or `yml`).
    result : Any
        The query result, if available.
    parser : argparse.ArgumentParser
        The argument parser instance used for CLI options.
    """
    def __init__(self):
        self.filename = ''
        self.filetype = ''
        self.result = None

        parser = argparse.ArgumentParser(
            prog='dictlistlib',
            usage='%(prog)s [options]',
            description='%(prog)s application',
        )

        parser.add_argument(
            '--gui', action='store_true',
            help='Launch a dictlistlib GUI application.'
        )

        parser.add_argument(
            '-f', '--filename', type=str,
            default='',
            help='JSON, YAML, or CSV file name.'
        )

        parser.add_argument(
            '-e', '--filetype', type=str, choices=['csv', 'json', 'yaml', 'yml'],
            default='',
            help='File type can be either json, yaml, yml, or csv.'
        )

        parser.add_argument(
            '-l', '--lookup', type=str, dest='lookup',
            default='',
            help='Lookup criteria for searching list or dictionary.'
        )

        parser.add_argument(
            '-s', '--select', type=str, dest='select_statement',
            default='',
            help='Select statement to enhance multiple searching criteria.'
        )

        parser.add_argument(
            '-t', '--tabular', action='store_true', dest='tabular',
            help='Show result in tabular format.'
        )

        parser.add_argument(
            '-d', '--dependency', action='store_true', dest='dependency',
            help='Show Python package dependencies.'
        )

        parser.add_argument(
            '-u', '--tutorial', type=str, choices=['base', 'csv', 'json', 'yaml'],
            default='',
            help='Tutorial can be either base, csv, json, or yaml.'
        )

        parser.add_argument(
            '-v', '--version', action='store_true', dest='version',
            help='Show dictlistlib version.'
        )

        self.parser = parser

    @property
    def is_csv_type(self):
        """
        Check whether the current filetype is CSV.

        This property evaluates the `filetype` attribute and returns
        a boolean indicating if it is set to `"csv"`.

        Returns
        -------
        bool
            True if `self.filetype` equals `"csv"`, otherwise False.
        """
        return self.filetype == 'csv'

    @property
    def is_json_type(self):
        """
        Check whether the current filetype is JSON.

        This property evaluates the `filetype` attribute and returns
        a boolean indicating if it is set to `"json"`.

        Returns
        -------
        bool
            True if `self.filetype` equals `"json"`, otherwise False.
        """
        return self.filetype == 'json'

    @property
    def is_yaml_type(self):
        """
        Check whether the current filetype is YAML.

        This property evaluates the `filetype` attribute and returns
        a boolean indicating if it is set to either `"yaml"` or `"yml"`.

        Returns
        -------
        bool
            True if `self.filetype` equals `"yaml"` or `"yml"`, otherwise False.
        """
        return self.filetype in ['yml', 'yaml']

    def validate_cli_flags(self, options):
        """
        Validate CLI flags.

        Parameters
        ----------
        options : argparse.Namespace
            Parsed command-line options.

        Returns
        -------
        bool
            True if at least one flag is provided. Otherwise,
            prints help and terminates with ``sys.exit(ECODE.BAD)``.
        """

        chk = any(bool(i) for i in vars(options).values())

        if not chk:
            self.parser.print_help()
            sys.exit(ECODE.BAD)

        return True

    def validate_filename(self, options):
        """
        Validate the `--filename` flag.

        Ensures that the provided filename has a valid extension
        (`csv`, `json`, `yml`, or `yaml`) or that a filetype flag
        is explicitly specified.

        Parameters
        ----------
        options : argparse.Namespace
            Parsed command-line options.

        Returns
        -------
        bool
            True if the filename is valid. Otherwise, prints an
            error message and terminates with ``sys.exit(ECODE.BAD)``.
        """
        filename, filetype = str(options.filename), str(options.filetype)
        if not filename:
            print('*** --filename flag CAN NOT be empty.')
            sys.exit(ECODE.BAD)

        self.filename = filename
        self.filetype = filetype

        _, ext = path.splitext(filename)
        ext = ext.lower()
        if ext in ['.csv', '.json', '.yml', '.yaml']:
            self.filetype = ext[1:]
            return True

        if not filetype:
            if ext == '':
                fmt = ('*** {} file doesnt have an extension.  '
                       'System cant determine a file type.  '
                       'Please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')

            else:
                fmt = ('*** {} file has an extension but its extension is not '
                       'csv, json, yml, or yaml.  If you think this file is '
                       'csv, json, yml, or yaml file, '
                       'please rerun with --filetype=<filetype> '
                       'where filetype is csv, json, yml, or yaml.')
            print(fmt.format(filename))
            sys.exit(ECODE.BAD)
        else:
            self.filetype = filetype

    def run_cli(self, options):
        """
        Execute dictlistlib query via CLI.

        Parameters
        ----------
        options : argparse.Namespace
            Parsed command-line options.

        Returns
        -------
        None
            Executes the query, prints results, and terminates
            with ``sys.exit(ECODE.SUCCESS)``.
        """
        lookup, select = options.lookup, options.select_statement
        if not options.lookup:
            print('*** --lookup flag CANNOT be empty.')
            sys.exit(ECODE.BAD)

        if self.is_csv_type:
            func = create_from_csv_file
        elif self.is_json_type:
            func = create_from_json_file
        elif self.is_yaml_type:
            func = create_from_yaml_file
        else:
            print('*** invalid filetype.  Check with DEV.')
            sys.exit(ECODE.BAD)

        query_obj = func(self.filename)
        result = query_obj.find(lookup=lookup, select=select)
        if result:
            print_data_as_tabular(result) if options.tabular else print(result)
        else:
            print('*** No record is found.')

        sys.exit(ECODE.SUCCESS)

    def run(self):
        """
        Parse CLI arguments and execute dictlistlib.

        This method orchestrates the CLI workflow by parsing arguments,
        showing version/dependency/tutorial information, validating flags
        and filenames, and executing queries.

        Returns
        -------
        None
        """
        options = self.parser.parse_args()
        show_version(options)
        show_dependency(options)
        run_tutorial(options)
        run_gui_application(options)
        self.validate_cli_flags(options)
        self.validate_filename(options)
        self.run_cli(options)


def execute():
    """
    Execute dictlistlib console CLI.

    This function instantiates the `Cli` class and runs its
    `run()` method, serving as the main entry point for the
    console application.

    Returns
    -------
    None
    """
    app = Cli()
    app.run()
