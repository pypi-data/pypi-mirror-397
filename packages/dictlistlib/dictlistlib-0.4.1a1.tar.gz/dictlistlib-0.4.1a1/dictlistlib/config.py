"""Module containing metadata and attributes for dictlistlib.

This module defines versioning, edition information, and the `Data` class,
which centralizes application metadata such as package dependencies,
company details, repository links, and license information.
"""

from os import path

import compare_versions
import dateutil
import yaml

__version__ = '0.4.1a1'
version = __version__
__edition__ = 'Community'
edition = __edition__

__all__ = [
    'version',
    'edition',
    'Data'
]


class Data:
    """
    Centralized metadata container for the dictlistlib application.

    The `Data` class provides static attributes and helper methods
    that describe the application, its dependencies, company details,
    and licensing information. It serves as a single source of truth
    for metadata used throughout the application.

    Attributes
    ----------
    main_app_text : str
        Display text for the main application including version.
    compare_versions_text : str
        Version string for the `compare_versions` dependency.
    compare_versions_link : str
        PyPI link for the `compare_versions` package.
    python_dateutil_text : str
        Version string for the `python-dateutil` dependency.
    python_dateutil_link : str
        PyPI link for the `python-dateutil` package.
    pyyaml_text : str
        Version string for the `PyYAML` dependency.
    pyyaml_link : str
        PyPI link for the `PyYAML` package.
    company : str
        Name of the company maintaining dictlistlib.
    company_url : str
        Official company website.
    repo_url : str
        GitHub repository URL for dictlistlib.
    documentation_url : str
        Link to the README file in the repository.
    license_url : str
        Link to the LICENSE file in the repository.
    years : str
        License validity years.
    license_name : str
        Name of the license (BSD-3-Clause).
    copyright_text : str
        Copyright notice text.
    license : str
        Full license text loaded from the LICENSE file.
    """
    # main app
    main_app_text = 'dictlistlib {}'.format(version)

    # packages
    compare_versions_text = 'compare_versions v{}'.format(compare_versions.__version__)
    compare_versions_link = 'https://pypi.org/project/compare_versions/'

    python_dateutil_text = 'python-dateutil v{}'.format(dateutil.__version__)   # noqa
    python_dateutil_link = 'https://pypi.org/project/python_dateutil/'

    pyyaml_text = 'pyyaml v{}'.format(yaml.__version__)
    pyyaml_link = 'https://pypi.org/project/PyYAML/'

    # company
    company = 'Geeks Trident LLC'
    company_url = 'https://www.geekstrident.com/'

    # URL
    repo_url = 'https://github.com/Geeks-Trident-LLC/dictlistlib'
    documentation_url = path.join(repo_url, 'blob/develop/README.md')
    license_url = path.join(repo_url, 'blob/develop/LICENSE')

    # License
    years = '2022-2040'
    license_name = 'BSD-3-Clause License'
    copyright_text = 'Copyright @ {}'.format(years)
    with open("LICENSE", encoding="utf-8") as f:
        license = f.read()

    @classmethod
    def get_dependency(cls):
        """
        Retrieve metadata for external package dependencies.

        This method returns a dictionary containing version strings
        and PyPI links for the key dependencies used by dictlistlib.

        Returns
        -------
        dict
            A dictionary with dependency names as keys and metadata
            dictionaries as values. Each metadata dictionary contains:
            - 'package': str, version string of the dependency.
            - 'url': str, PyPI link for the dependency.
        """
        dependencies = dict(
            compare_versions=dict(
                package=cls.compare_versions_text,
                url=cls.compare_versions_link
            ),
            dateutil=dict(
                package=cls.python_dateutil_text,
                url=cls.python_dateutil_link
            ),
            pyyaml=dict(
                package=cls.pyyaml_text,
                url=cls.pyyaml_link
            )
        )
        return dependencies
