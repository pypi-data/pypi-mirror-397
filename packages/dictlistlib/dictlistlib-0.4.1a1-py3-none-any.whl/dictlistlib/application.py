"""
dictlistlib application module.

This module provides the main logic and user interface components
for the `dictlistlib` library. It integrates with `tkinter` to
offer a graphical interface for working with dictionary/list data
structures, and supports importing data from multiple formats.

Notes
-----
- If `tkinter` is not installed, the module prints a descriptive
  error message and terminates the program.
- This module is intended to serve as the entry point for launching
  the dictlistlib application with GUI support.
"""

import platform

from dictlistlib.utils import Text

try:
    import tkinter as tk
except ModuleNotFoundError as ex:
    from dictlistlib.utils import Printer
    from dictlistlib.constant import ECODE
    import sys
    lst = ["Failed to launch dictlistlib application because",
           "Python{} binary doesn't have tkinter module".format(platform.python_version()),
           "Please install tkinter module and try it again"]
    Printer.print(lst)
    sys.exit(ECODE.BAD)
except Exception as ex:
    raise ex

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font

from os import path
from pprint import pformat
import webbrowser

from dictlistlib import create_from_csv_data
from dictlistlib import create_from_json_data
from dictlistlib import create_from_yaml_data

from dictlistlib.utils import Tabular

from dictlistlib.config import Data


def get_relative_center_location(parent, width, height):
    """
    Calculate the coordinates to center a child window relative to its parent.

    This function determines the (x, y) position for placing a child
    window so that it is centered within the bounds of the given
    parent window.

    Parameters
    ----------
    parent : tkinter.Tk or tkinter.Toplevel
        The parent window instance whose geometry is used as reference.
    width : int
        The width of the child window.
    height : int
        The height of the child window.

    Returns
    -------
    tuple of int
        A tuple ``(x, y)`` representing the top-left coordinates at
        which the child window should be placed to appear centered
        within the parent window.

    Notes
    -----
    - The calculation uses the parent's geometry string (width x height + x + y).
    - Coordinates are returned as integers suitable for use with
      ``geometry()`` in tkinter.
    """
    pwh, px, py = parent.winfo_geometry().split('+')
    px, py = int(px), int(py)
    pw, ph = [int(i) for i in pwh.split('x')]

    x = int(px + (pw - width) / 2)
    y = int(py + (ph - height) / 2)
    return x, y


def create_msgbox(title=None, error=None, warning=None, info=None,
                  question=None, okcancel=None, retrycancel=None,
                  yesno=None, yesnocancel=None, **options):
    """
    Display a tkinter messagebox with the specified type and message.

    This function provides a unified interface for creating different
    types of message boxes (error, warning, info, question, and various
    confirmation dialogs). Only one type of message should be specified
    per call. The function delegates to the appropriate `tkinter.messagebox`
    function based on the provided keyword argument.

    Parameters
    ----------
    title : str, optional
        The title of the messagebox window. Default is None.
    error : str, optional
        An error message. Displays an error dialog. Default is None.
    warning : str, optional
        A warning message. Displays a warning dialog. Default is None.
    info : str, optional
        An informational message. Displays an info dialog. Default is None.
    question : str, optional
        A question prompt. Displays a yes/no dialog returning a string. Default is None.
    okcancel : str, optional
        A message for an OK/Cancel dialog. Returns a boolean. Default is None.
    retrycancel : str, optional
        A message for a Retry/Cancel dialog. Returns a boolean. Default is None.
    yesno : str, optional
        A message for a Yes/No dialog. Returns a boolean. Default is None.
    yesnocancel : str, optional
        A message for a Yes/No/Cancel dialog. Returns a boolean or None. Default is None.
    **options : dict
        Additional keyword arguments passed to the underlying tkinter
        messagebox function (e.g., `icon`, `default`).

    Returns
    -------
    str or bool or None
        The result of the messagebox interaction:
        - "ok" for error, warning, or info dialogs.
        - "yes"/"no" string for question dialogs.
        - Boolean for okcancel, retrycancel, yesno dialogs.
        - Boolean or None for yesnocancel dialogs.

    Notes
    -----
    - Only one message type should be provided per call. If multiple
      are specified, the first matching type in the order of evaluation
      (error → warning → info → question → okcancel → retrycancel → yesno → yesnocancel)
      will be used.
    - If no type is specified, an info dialog is shown by default.
    """
    if error:
        # a return result is an "ok" string
        result = messagebox.showerror(title=title, message=error, **options)
    elif warning:
        # a return result is an "ok" string
        result = messagebox.showwarning(title=title, message=warning, **options)
    elif info:
        # a return result is an "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)
    elif question:
        # a return result is a "yes" or "no" string
        result = messagebox.askquestion(title=title, message=question, **options)
    elif okcancel:
        # a return result is boolean
        result = messagebox.askokcancel(title=title, message=okcancel, **options)
    elif retrycancel:
        # a return result is boolean
        result = messagebox.askretrycancel(title=title, message=retrycancel, **options)
    elif yesno:
        # a return result is boolean
        result = messagebox.askyesno(title=title, message=yesno, **options)
    elif yesnocancel:
        # a return result is boolean or None
        result = messagebox.askyesnocancel(title=title, message=yesnocancel, **options)
    else:
        # a return result is an "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)

    return result


def set_modal_dialog(dialog):
    """
    Configure a tkinter dialog window to behave as a modal dialog.

    A modal dialog prevents interaction with other windows in the
    application until the dialog is closed. This function sets the
    dialog as transient to its parent, ensures it is visible, and
    grabs focus so that user input is restricted to the dialog.

    Parameters
    ----------
    dialog : tkinter.Toplevel or tkinter.Tk
        The dialog or window instance to configure as modal.

    Notes
    -----
    - `transient()` ties the dialog to its parent window.
    - `wait_visibility()` ensures the dialog is displayed before
      grabbing focus.
    - `grab_set()` restricts user input to the dialog only.
    - `wait_window()` blocks execution until the dialog is closed.
    """
    dialog.transient(dialog.master)
    dialog.wait_visibility()
    dialog.grab_set()
    dialog.wait_window()


class Content:
    """
    A container class for managing and processing structured content.

    The `Content` class encapsulates data provided either directly
    as a string or loaded from a file. It determines the file type
    (CSV, JSON, or YAML), validates the content, and prepares a
    query object for further use.

    Attributes
    ----------
    case : str
        Indicates the source of the content: "file", "data", or "unknown".
    data : str
        The raw text content, either provided directly or read from a file.
    filename : str
        The name of the file containing the content, if applicable.
    filetype : str
        The type of the content ("csv", "json", or "yaml").
    ready : bool
        True if the content has been successfully processed and is ready to use.
    query_obj : object or None
        The parsed query object created from the content, depending on file type.

    Notes
    -----
    - Supported file types: CSV, JSON, YAML/YML.
    - If content is invalid or empty, a warning messagebox is displayed.
    - The class automatically processes content during initialization.
    """
    def __init__(self, data='', filename='', filetype=''):
        """
        Initialize a Content instance.

        Parameters
        ----------
        data : str, optional
            Raw text content. Default is an empty string.
        filename : str, optional
            Path to a file containing content. Default is an empty string.
        filetype : str, optional
            Explicit file type ("csv", "json", "yaml"). Default is empty.
        """
        self.case = 'file' if filename else 'data' if data else 'unknown'
        self.data = data
        self.filename = filename
        self.filetype = filetype
        self.ready = False
        self.query_obj = None
        self.process()

    @property
    def is_csv(self):
        """
        Check if the content is in CSV format.

        Returns
        -------
        bool
            True if the filetype is "csv", otherwise False.
        """
        return self.filetype == 'csv'

    @property
    def is_json(self):
        """
        Check if the content is in JSON format.

        Returns
        -------
        bool
            True if the filetype is "json", otherwise False.
        """
        return self.filetype == 'json'

    @property
    def is_yaml(self):
        """
        Check if the content is in YAML format.

        Returns
        -------
        bool
            True if the filetype is "yaml" or "yml", otherwise False.
        """
        return self.filetype in ['yaml', 'yml']

    @property
    def is_ready(self):
        """
        Check if the content has been successfully processed.

        Returns
        -------
        bool
            True if the content is ready to use, otherwise False.
        """
        return self.ready

    def process_filename(self):
        """
        Process the content from a file.

        Determines the file extension, validates it, sets the filetype,
        and reads the file content into `self.data`. Displays a warning
        messagebox if the file extension is invalid or the file is empty.
        """
        if self.filename:
            _, ext = path.splitext(self.filename)
            extension = ext[1:]
            ext = ext.lower()[1:]
            if ext in ['csv', 'json', 'yml', 'yaml']:
                ext = 'yaml' if ext in ['yml', 'yaml'] else ext
                self.filetype = ext
            else:
                if not ext:
                    message = ('Make sure to select file with '
                               'extension json, yaml, yml, or csv.')
                else:
                    fmt = ('Selecting file extension is {}.  Make sure it is '
                           'in form of json, yaml, yml, or csv.')
                    message = fmt.format(extension)

                title = 'File Extension'
                create_msgbox(title=title, warning=message)

            with open(self.filename, newline='', encoding="utf-8") as stream:
                self.data = stream.read().strip()

                if not self.data:
                    message = 'This {} file is empty.'.format(self.filename)
                    title = 'File Extension'
                    create_msgbox(title=title, warning=message)

    def process_data(self):
        """
        Process the raw content data.

        Validates that data is not empty and that a filetype is specified.
        Depending on the filetype, attempts to parse the data into a query
        object using the appropriate parser (CSV, JSON, or YAML). Displays
        error messageboxes if parsing fails.
        """
        if not self.data:
            if self.case != 'file':
                title = 'Empty Data'
                message = 'data is empty.'
                create_msgbox(title=title, warning=message)

            return

        if not self.filetype:
            if self.case != 'file':
                title = 'Unselecting File Extension'
                message = ('Need to check filetype radio button '
                           'such as json, yaml, or csv.')
                create_msgbox(title=title, warning=message)
                return

        if self.is_yaml:
            try:
                self.query_obj = create_from_yaml_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing YAML Data', error=Text(exc))
        elif self.is_json:
            try:
                self.query_obj = create_from_json_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing JSON data', error=Text(exc))
        elif self.is_csv:
            try:
                self.query_obj = create_from_csv_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing CSV Data', error=Text(exc))

    def process(self):
        """
        Analyze and process the content.

        This method orchestrates content processing by:
        - Reading and validating file content if `self.filename` is provided.
        - Parsing raw data if `self.data` is provided.
        - Assigning the appropriate `self.filetype` and creating a query object.

        Notes
        -----
        - Called automatically during initialization.
        - Updates `self.ready` to True if processing succeeds.
        """
        self.process_filename()
        self.process_data()


class Application:
    """
    Main dictlistlib application class.

    This class provides the graphical user interface (GUI) for
    interacting with dictlistlib. It uses tkinter to build menus,
    frames, text areas, and entry widgets, and provides callbacks
    for file operations and help dialogs.

    Attributes
    ----------
    root : tkinter.Tk
        The root tkinter application window.
    content : Content or None
        A Content instance representing the loaded data, or None if
        no data has been loaded.
    Methods
    -------
    __init__() -> None
        Initialize the application, configure widgets, and build the GUI.
    build_menu() -> None
        Construct the application menu bar with file and help options.
    build_frame() -> None
        Build the main frames for organizing text, entry, and result areas.
    build_textarea() -> None
        Create and configure the input and result text areas.
    build_entry() -> None
        Create entry widgets for lookup and selection queries.
    build_result() -> None
        Create the result display area.
    set_title() -> None
        Set the application window title.
    run() -> None
        Start the tkinter main event loop.
    callback_file_open() -> None
        Handle the "Open File" menu action and load content.
    callback_help_documentation() -> None
        Open the dictlistlib documentation in a web browser.
    callback_help_view_licenses() -> None
        Display license information.
    callback_help_about() -> None
        Show an "About" dialog with application details.
    """

    browser = webbrowser

    def __init__(self):
        """
        Initialize the Application instance.

        Configures platform-specific tkinter widgets, sets up the
        main application window, initializes variables, and builds
        the GUI components (menu, frames, text areas, entries, and
        result display).
        """
        # support platform: macOS, Linux, and Window
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.is_window = platform.system() == 'Windows'

        # standardize tkinter widget for macOS, Linux, and Window operating system
        self.RadioButton = tk.Radiobutton if self.is_linux else ttk.Radiobutton
        self.CheckBox = tk.Checkbutton if self.is_linux else ttk.Checkbutton
        self.Label = ttk.Label
        self.Frame = ttk.Frame
        self.LabelFrame = ttk.LabelFrame
        self.Button = ttk.Button
        self.TextBox = ttk.Entry
        self.TextArea = tk.Text
        self.PanedWindow = ttk.PanedWindow

        self._base_title = 'dictlistlib'
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)
        self.content = None

        self.paned_window = None
        self.text_frame = None
        self.entry_frame = None
        self.result_frame = None

        self.radio_btn_var = tk.StringVar()
        self.radio_btn_var.set(None)    # noqa
        self.lookup_entry_var = tk.StringVar()
        self.select_entry_var = tk.StringVar()
        self.result = None

        self.input_textarea = None
        self.result_textarea = None
        self.csv_radio_btn = None
        self.json_radio_btn = None
        self.yaml_radio_btn = None

        self.set_title()
        self.build_menu()
        self.build_frame()
        self.build_textarea()
        self.build_entry()
        self.build_result()

    def set_title(self, widget=None, title=''):
        """
        Set the window title for a tkinter widget.

        This method updates the title of the specified tkinter widget.
        If no widget is provided, the root application window is used.
        The title is combined with the application's base title
        ("dictlistlib") for consistency.

        Parameters
        ----------
        widget : tkinter.Tk or tkinter.Toplevel, optional
            The tkinter window whose title should be set. If None,
            defaults to the root application window.
        title : str, optional
            A custom title prefix. If provided, the final title will
            be formatted as "<title> - dictlistlib". If empty, only
            the base title ("dictlistlib") is used.
        """
        widget = widget or self.root
        btitle = self._base_title
        title = '{} - {}'.format(title, btitle) if title else btitle
        widget.title(title)

    def create_custom_label(self, parent, text='', link='',
                            increased_size=0, bold=False, underline=False,
                            italic=False):
        """
        Create a custom tkinter label widget with optional styling and hyperlink behavior.

        This method generates a label with configurable font styles (bold,
        underline, italic, and size adjustments). If a hyperlink (`link`)
        is provided, the label is styled in blue and responds to mouse
        events to simulate hyperlink behavior:
        - On mouse hover, the label is underlined and the cursor changes to a hand.
        - On mouse leave, the label reverts to its original style.
        - On mouse click, the hyperlink is opened in a new browser tab.

        Parameters
        ----------
        parent : tkinter.Widget
            The parent widget in which the label will be placed.
        text : str, optional
            The text displayed in the label. Default is an empty string.
        link : str, optional
            A hyperlink associated with the label. If provided, the label
            becomes interactive and styled as a clickable link. Default is empty.
        increased_size : int, optional
            Amount to increase the font size relative to the default. Default is 0.
        bold : bool, optional
            If True, the label text is displayed in bold. Default is False.
        underline : bool, optional
            If True, the label text is underlined. Default is False.
        italic : bool, optional
            If True, the label text is italicized. Default is False.

        Returns
        -------
        tkinter.Label
            A configured label widget with the specified styling and behavior.

        Inner Methods
        -------------
        mouse_over(event) -> None
            Event handler for `<Enter>` (mouse hover). Adds underline to the font
            and changes the cursor to a hand pointer if the label has a link.
        mouse_out(event) -> None
            Event handler for `<Leave>` (mouse exit). Restores the original font
            and resets the cursor to an arrow.
        mouse_press(event) -> None
            Event handler for `<Button-1>` (mouse click). Opens the label's link
            in a new browser tab.
        """

        def mouse_over(event):
            if 'underline' not in event.widget.font:
                event.widget.configure(
                    font=event.widget.font + ['underline'],
                    cursor='hand2'
                )

        def mouse_out(event):
            event.widget.config(
                font=event.widget.font,
                cursor='arrow'
            )

        def mouse_press(event):
            self.browser.open_new_tab(event.widget.link)

        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        if link:
            label = self.Label(parent, text=text, style='Blue.TLabel')
            label.bind('<Enter>', mouse_over)
            label.bind('<Leave>', mouse_out)
            label.bind('<Button-1>', mouse_press)
        else:
            label = self.Label(parent, text=text)
        font = Font(name='TkDefaultFont', exists=True, root=label)
        font = [font.cget('family'), font.cget('size') + increased_size]
        bold and font.append('bold')
        underline and font.append('underline')
        italic and font.append('italic')
        label.configure(font=font)
        label.font = font
        label.link = link
        return label

    def callback_file_open(self):
        """
        Handle the "File > Open" menu action.

        This callback opens a file selection dialog, allowing the user
        to choose a JSON, YAML, or CSV file. Once a file is selected,
        it creates a `Content` instance from the file, validates and
        processes the data, and updates the application state and UI.

        Workflow
        --------
        1. Display a file dialog restricted to JSON, YAML/YML, and CSV files.
        2. If a file is selected:
           - Create a `Content` object with the chosen filename.
           - If the content is successfully processed (`is_ready`):
             * Update the application window title with the filename.
             * Clear the input text area and insert the file’s content.
             * Update the radio button selection to reflect the file type.

        Side Effects
        ------------
        - Modifies the application’s title via `set_title`.
        - Updates the input text area with new content.
        - Updates the filetype radio button variable.

        Returns
        -------
        None
        """
        filetypes = [
            ('JSON Files', '*json'),
            ('YAML Files', '*yaml'),
            ('YML Files', '*yml'),
            ('CSV Files', '*csv')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            content = Content(filename=filename)
            if content.is_ready:
                self.set_title(title=filename)
                self.input_textarea.delete("1.0", "end")
                self.input_textarea.insert(tk.INSERT, content.data)
                self.radio_btn_var.set(content.filetype)

    def callback_help_documentation(self):
        """
        Handle the "Help > Getting Started" menu action.

        This callback opens the dictlistlib documentation in the user's
        default web browser. It provides quick access to the official
        help resources so users can learn how to use the application.

        Returns
        -------
        None

        Notes
        -----
        - Uses the system's default browser to open the documentation URL.
        - The documentation URL is defined in `Data.documentation_url`.

        Examples
        --------
        Triggered automatically when the user selects:
        Menu → Help → Getting Started
        """
        self.browser.open_new_tab(Data.documentation_url)

    def callback_help_view_licenses(self):
        """
        Handle the "Help > View Licenses" menu action.

        This callback opens the dictlistlib license information in the
        user's default web browser. It provides quick access to the
        licensing terms and conditions associated with the application.

        Returns
        -------
        None

        Notes
        -----
        - Uses the system's default browser to open the license URL.
        - The license URL is defined in `Data.license_url`.

        Examples
        --------
        Triggered automatically when the user selects:
        Menu → Help → View Licenses
        """
        self.browser.open_new_tab(Data.license_url)

    def callback_help_about(self):
        """
        Handle the "Help > About" menu action.

        This callback displays an "About" dialog containing information
        about the dictlistlib application. It typically includes details
        such as the application name, version, and a brief description
        of its purpose.

        Returns
        -------
        None

        Notes
        -----
        - The dialog is shown using tkinter's messagebox functionality.
        - Intended to provide users with quick reference information
          about the application.

        Examples
        --------
        Triggered automatically when the user selects:
        Menu → Help → About
        """

        about = tk.Toplevel(self.root)
        self.set_title(widget=about, title='About')
        width, height = 460, 460
        x, y = get_relative_center_location(self.root, width, height)
        about.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        about.resizable(False, False)

        top_frame = self.Frame(about)
        top_frame.pack(fill=tk.BOTH, expand=True)

        paned_window = self.PanedWindow(top_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=8, pady=12)

        # company
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=4)

        self.create_custom_label(
            frame, text=Data.main_app_text,
            increased_size=2, bold=True
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # URL
        cell_frame = self.Frame(frame, width=450, height=5)
        cell_frame.grid(row=1, column=0, sticky=tk.W, columnspan=2)

        url = Data.repo_url
        self.Label(cell_frame, text='URL:').pack(side=tk.LEFT)

        self.create_custom_label(
            cell_frame, text=url, link=url
        ).pack(side=tk.LEFT)

        # dependencies
        self.create_custom_label(
            frame, text='Pypi.com Dependencies:', bold=True
        ).grid(row=2, column=0, sticky=tk.W)

        # compare_versions package
        self.create_custom_label(
            frame, text=Data.compare_versions_text,
            link=Data.compare_versions_link
        ).grid(row=3, column=0, padx=(20, 0), sticky=tk.W)

        # python-dateutil package
        self.create_custom_label(
            frame, text=Data.python_dateutil_text,
            link=Data.python_dateutil_link
        ).grid(row=4, column=0, padx=(20, 0), pady=(0, 10), sticky=tk.W)

        # PyYAML package
        self.create_custom_label(
            frame, text=Data.pyyaml_text,
            link=Data.pyyaml_link
        ).grid(row=3, column=1, padx=(20, 0), sticky=tk.W)

        # license textbox
        lframe = self.LabelFrame(
            paned_window, height=200, width=450,
            text=Data.license_name
        )
        paned_window.add(lframe, weight=7)

        width = 58 if self.is_macos else 51
        height = 18 if self.is_macos else 14 if self.is_linux else 15
        txtbox = self.TextArea(lframe, width=width, height=height, wrap='word')
        txtbox.grid(row=0, column=0, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lframe, orient=tk.VERTICAL, command=txtbox.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        txtbox.config(yscrollcommand=scrollbar.set)
        txtbox.insert(tk.INSERT, Data.license)
        txtbox.config(state=tk.DISABLED)

        # footer - copyright
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=1)

        self.Label(frame, text=Data.copyright_text).pack(side=tk.LEFT, pady=(10, 10))

        self.create_custom_label(
            frame, text=Data.company, link=Data.company_url
        ).pack(side=tk.LEFT, pady=(10, 10))

        self.Label(frame, text='.  All right reserved.').pack(side=tk.LEFT, pady=(10, 10))

        set_modal_dialog(about)

    def build_menu(self):
        """
        Construct the main menubar for the dictlistlib application.

        This method creates and attaches a menubar to the root window,
        providing "File" and "Help" menus with common application actions.

        Menu Structure
        --------------
        File
            - Open : Launches a file dialog to load JSON, YAML, or CSV content
                     (handled by `callback_file_open`).
            - Separator
            - Quit : Exits the application.

        Help
            - Documentation : Opens the dictlistlib documentation in the default browser
                              (handled by `callback_help_documentation`).
            - View Licenses : Opens the license information in the default browser
                              (handled by `callback_help_view_licenses`).
            - Separator
            - About : Displays an "About" dialog with application details
                      (handled by `callback_help_about`).

        Returns
        -------
        None

        Notes
        -----
        - The menubar is attached to the root tkinter window via `self.root.config(menu=...)`.
        - Menu items are bound to callback methods that handle user actions.
        """
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file = tk.Menu(menu_bar)
        help_ = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=file, label='File')
        menu_bar.add_cascade(menu=help_, label='Help')

        file.add_command(label='Open', command=lambda: self.callback_file_open())
        file.add_separator()
        file.add_command(label='Quit', command=lambda: self.root.quit())

        help_.add_command(label='Documentation',
                          command=lambda: self.callback_help_documentation())
        help_.add_command(label='View Licenses',
                          command=lambda: self.callback_help_view_licenses())
        help_.add_separator()
        help_.add_command(label='About', command=lambda: self.callback_help_about())

    def build_frame(self):
        """
        Construct the main layout frames for the dictlistlib application.

        This method creates a vertical paned window that organizes the
        application into three primary sections:
        - **Text Frame**: The main area for displaying or editing input data.
        - **Entry Frame**: A smaller area for query entry fields (e.g., lookup or select).
        - **Result Frame**: A section for displaying query results.

        The frames are added to a vertically oriented paned window with
        relative weights to control their resizing behavior.

        Layout Structure
        ----------------
        PanedWindow (vertical)
            ├── Text Frame   (weight=7, larger area for input content)
            ├── Entry Frame  (default weight, smaller area for query input)
            └── Result Frame (weight=2, medium area for results)

        Returns
        -------
        None

        Notes
        -----
        - The paned window expands to fill the root window (`fill=tk.BOTH, expand=True`).
        - Frame sizes are initialized with default width/height values but
          will adjust dynamically when the window is resized.
        - Relief style is set to `tk.RIDGE` for visual separation.
        """
        self.paned_window = self.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.text_frame = self.Frame(
            self.paned_window, width=600, height=400, relief=tk.RIDGE
        )
        self.entry_frame = self.Frame(
            self.paned_window, width=600, height=100, relief=tk.RIDGE
        )
        self.result_frame = self.Frame(
            self.paned_window, width=600, height=100, relief=tk.RIDGE
        )
        self.paned_window.add(self.text_frame, weight=7)
        self.paned_window.add(self.entry_frame)
        self.paned_window.add(self.result_frame, weight=2)

    def build_textarea(self):
        """
        Construct the input text area for the dictlistlib application.

        This method creates a multi-line text widget inside the `text_frame`
        for entering or displaying raw data (e.g., JSON, YAML, or CSV).
        It configures the widget to expand with the frame, and attaches
        both vertical and horizontal scrollbars for navigation.

        Layout Structure
        ----------------
        text_frame (grid layout)
            ├── input_textarea : tkinter.Text
            │   - Positioned at row=0, column=0
            │   - Expands to fill available space (sticky='nswe')
            ├── vscrollbar : ttk.Scrollbar (vertical)
            │   - Positioned at row=0, column=1
            │   - Controls vertical scrolling of the text area
            └── hscrollbar : ttk.Scrollbar (horizontal)
                - Positioned at row=1, column=0
                - Controls horizontal scrolling of the text area

        Returns
        -------
        None

        Notes
        -----
        - The text area uses `wrap='none'` to allow horizontal scrolling.
        - Scrollbars are linked to the text area via `yscrollcommand` and
          `xscrollcommand`.
        - The grid row and column are configured with weight=1 to ensure
          the text area expands when the window is resized.
        """

        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.input_textarea = self.TextArea(self.text_frame, width=20, height=5, wrap='none')
        self.input_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.input_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.HORIZONTAL, command=self.input_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.input_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def build_entry(self):
        """
        Construct the input entry section for the dictlistlib application.

        This method builds the interactive controls for selecting file types,
        running queries, clearing input/output, pasting clipboard data, and
        formatting results. It also provides entry fields for lookup and
        select queries, along with associated buttons.

        Layout Structure
        ----------------
        entry_frame
            ├── Row 0 (controls)
            │   ├── Radio buttons: csv, json, yaml
            │   ├── Buttons: Open, Paste, Clear, Run, Tabular
            └── Row 1 & 2 (query entries)
                ├── Lookup entry + Clear button
                └── Select entry + Clear button

        Inner Callback Functions
        ------------------------
        callback_run_btn()
            Execute a query using the current input data, filetype, lookup,
            and select values. Displays the result in the result text area.
            Shows an error messagebox if query execution fails.

        callback_tabular_btn()
            Execute a query and attempt to format the result in tabular form.
            If conversion fails, displays a formatted error message with the
            raw result. Updates the result text area accordingly.

        callback_clear_text_btn()
            Clear both input and result text areas, reset radio buttons and
            entry fields, and reset the application title.

        callback_paste_text_btn()
            Paste clipboard content into the input text area. Validates that
            a filetype is selected before processing. Updates the title and
            radio button state if content is successfully parsed. Shows a
            warning messagebox if the clipboard is empty or invalid.

        callback_clear_lookup_entry()
            Clear the lookup entry field.

        callback_clear_select_entry()
            Clear the select entry field.

        Returns
        -------
        None

        Notes
        -----
        - Radio buttons allow users to select the filetype (CSV, JSON, YAML).
        - The "Run" button executes queries directly, while "Tabular" attempts
          to format results in a tabular view.
        - The "Paste" button supports importing data from the system clipboard.
        - The "Clear" buttons reset either text areas or individual entry fields.
        """
        def callback_run_btn():
            """
            Execute a query based on the current input and update the result area.

            This inner function of `Application.build_entry` retrieves the input data,
            selected filetype, lookup value, and select value. It then constructs a
            `Content` object and attempts to run a query using its `query_obj`.
            The query result is displayed in the result text area. If query execution
            fails, an error messagebox is shown.

            Workflow
            --------
            1. Retrieve input data from the text area.
            2. Get the selected filetype, lookup, and select values.
            3. Create a `Content` instance and validate readiness.
            4. Execute the query via `query_obj.find(...)`.
            5. Display the result in the result text area.
            6. Show an error messagebox if an exception occurs.

            Returns
            -------
            None
            """
            data = self.input_textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(result))

            except Exception as exc:
                create_msgbox(title='Query Problem', error=Text(exc))

        def callback_tabular_btn():
            """
            Execute a query and attempt to display results in tabular format.

            This inner function of `Application.build_entry` retrieves the current
            input data, selected filetype, lookup value, and select value. It then
            constructs a `Content` object and executes a query using its `query_obj`.
            The result is passed to a `Tabular` object for formatting. If the result
            can be converted to tabular form, it is displayed in the result text area.
            Otherwise, a formatted error message along with the raw result is shown.

            Workflow
            --------
            1. Retrieve input data from the text area.
            2. Get the selected filetype, lookup, and select values.
            3. Create a `Content` instance and validate readiness.
            4. Execute the query via `query_obj.find(...)`.
            5. Wrap the result in a `Tabular` object.
            6. If tabular conversion succeeds, display the tabular text.
               Otherwise, show a failure message with the raw result.
            7. Catch exceptions and display an error messagebox if needed.

            Returns
            -------
            None

            Side Effects
            ------------
            - Updates `self.result` with the query result.
            - Clears and repopulates the result text area.
            - Displays error messages via `create_msgbox` if query execution fails.

            Examples
            --------
            Triggered automatically when the user clicks the "Tabular" button
            in the entry frame.
            """
            data = self.input_textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                tabular_obj = Tabular(self.result)

                if tabular_obj.is_tabular:
                    text = tabular_obj.get()
                else:
                    fmt = 'CANNOT convert to tabular format because {!r}\n{}\n{}'
                    pretty_text = pformat(self.result)
                    text = fmt.format(tabular_obj.failure, '-' * 40, pretty_text)

                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(text))

            except Exception as exc:
                create_msgbox(title='Query Problem', error=Text(exc))

        def callback_clear_text_btn():
            """
            Clear all input, output, and query state in the application.

            This inner function of `Application.build_entry` resets the
            application to a clean state by removing text from both the
            input and result areas, clearing query-related variables,
            and resetting the window title.

            Workflow
            --------
            1. Delete all content from the input text area.
            2. Delete all content from the result text area.
            3. Reset the filetype radio button selection to `None`.
            4. Clear the lookup and select entry fields.
            5. Reset the stored query result (`self.result`) to `None`.
            6. Reset the application title to its default state.

            Returns
            -------
            None

            Side Effects
            ------------
            - Modifies multiple UI widgets (input textarea, result textarea,
              radio buttons, lookup/select entries).
            - Updates application state variables (`self.result`).
            - Resets the window title via `set_title()`.

            Examples
            --------
            Triggered automatically when the user clicks the "Clear" button
            in the entry frame to reset the workspace.
            """
            self.input_textarea.delete("1.0", "end")
            self.result_textarea.delete("1.0", "end")
            self.radio_btn_var.set(None)    # noqa
            self.lookup_entry_var.set('')
            self.select_entry_var.set('')
            self.result = None
            self.set_title()

        def callback_paste_text_btn():
            """
            Paste clipboard content into the input text area.

            This inner function of `Application.build_entry` retrieves text data
            from the system clipboard and inserts it into the input textarea.
            It validates that a filetype (CSV, JSON, or YAML) has been selected
            before attempting to process the clipboard content. If the content
            can be parsed successfully, the application title and filetype state
            are updated accordingly. If the clipboard is empty or invalid, a
            warning messagebox is displayed.

            Workflow
            --------
            1. Check whether a filetype is selected (CSV, JSON, or YAML).
               - If not, show a warning messagebox and exit.
            2. Attempt to retrieve text data from the system clipboard.
            3. If data is available:
               - Clear the input textarea.
               - Create a `Content` object with the clipboard data and selected filetype.
               - If the content is ready:
                 * Update the application title to indicate clipboard paste.
                 * Insert the clipboard data into the input textarea.
                 * Update the radio button state to reflect the parsed filetype.
            4. If clipboard retrieval fails or is empty, show a warning messagebox.

            Returns
            -------
            None

            Side Effects
            ------------
            - Clears and repopulates the input textarea.
            - Updates `self.content` with a new `Content` object.
            - Updates the application title via `set_title()`.
            - Updates the filetype radio button state.
            - Displays warning messageboxes for invalid or empty clipboard states.

            Examples
            --------
            Triggered automatically when the user clicks the "Paste" button
            in the entry frame to import data from the clipboard.
            """
            filetype = self.radio_btn_var.get()
            if filetype == 'None':
                title = 'Unselect CSV/JSON/YAML'
                message = 'Please select CSV, JSON, or YAML.'
                create_msgbox(title=title, warning=message)
                return

            try:
                data = self.root.clipboard_get()
                if data:
                    self.input_textarea.delete("1.0", "end")
                    # filetype = self.radio_btn_var.get()
                    self.content = Content(data=data, filetype=filetype)
                    if self.content.is_ready:
                        self.set_title(title='<<PASTE - Clipboard>>')
                        self.input_textarea.insert(tk.INSERT, data)
                        self.radio_btn_var.set(self.content.filetype)
            except Exception as _ex:        # noqa
                title = 'Empty Clipboard',
                message = 'CAN NOT paste because there is no data in pasteboard.'
                create_msgbox(title=title, warning=message)

        def callback_clear_lookup_entry():
            """
            Clear the lookup entry field.

            This inner function of `Application.build_entry` resets the
            `lookup_entry_var` StringVar to an empty string, effectively
            clearing any text entered in the lookup input field.

            Returns
            -------
            None

            Side Effects
            ------------
            - Updates the bound `lookup_entry_var` to an empty string.
            - The associated lookup entry widget in the UI is cleared.

            Examples
            --------
            Triggered automatically when the user clicks the "Clear" button
            next to the Lookup entry field.
            """
            self.lookup_entry_var.set('')

        def callback_clear_select_entry():
            """
            Clear the select entry field.

            This inner function of `Application.build_entry` resets the
            `select_entry_var` StringVar to an empty string, effectively
            clearing any text entered in the select input field.

            Returns
            -------
            None

            Side Effects
            ------------
            - Updates the bound `select_entry_var` to an empty string.
            - The associated select entry widget in the UI is cleared.

            Examples
            --------
            Triggered automatically when the user clicks the "Clear" button
            next to the Select entry field.
            """
            self.select_entry_var.set('')

        width = 70 if self.is_macos else 79 if self.is_linux else 107
        x1 = 2 if self.is_linux else 0

        # frame for row 0
        frame = self.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=0, column=0, padx=10, pady=(4, 0), sticky=tk.W)

        # radio buttons
        self.csv_radio_btn = self.RadioButton(
            frame, text='csv', variable=self.radio_btn_var,
            value='csv'
        )
        self.csv_radio_btn.pack(side=tk.LEFT)

        self.json_radio_btn = self.RadioButton(
            frame, text='json', variable=self.radio_btn_var,
            value='json'
        )
        self.json_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        self.yaml_radio_btn = self.RadioButton(
            frame, text='yaml', variable=self.radio_btn_var,
            value='yaml'
        )
        self.yaml_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # open button
        open_file_btn = self.Button(frame, text='Open',
                                    command=self.callback_file_open)
        open_file_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # paste button
        paste_text_btn = self.Button(frame, text='Paste',
                                     command=callback_paste_text_btn)
        paste_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # clear button
        clear_text_btn = self.Button(frame, text='Clear',
                                     command=callback_clear_text_btn)
        clear_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # run button
        run_btn = self.Button(frame, text='Run',
                              command=callback_run_btn)
        run_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # pprint button
        tabular_btn = self.Button(frame, text='Tabular',
                                  command=callback_tabular_btn)
        tabular_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # frame for row 1 & 2
        frame = ttk.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=1, column=0, padx=10, pady=(0, 4), sticky=tk.W)

        # lookup entry
        lbl = self.Label(frame, text='Lookup')
        lbl.grid(row=0, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        lookup_entry = self.TextBox(frame, width=width,
                                    textvariable=self.lookup_entry_var)
        lookup_entry.grid(row=0, column=1, padx=0, pady=0, sticky=tk.W)
        lookup_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_lookup_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_lookup_entry)
        clear_lookup_btn.grid(row=0, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

        # select statement entry
        lbl = self.Label(frame, text='Select')
        lbl.grid(row=1, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        select_entry = self.TextBox(frame, width=width,
                                    textvariable=self.select_entry_var)
        select_entry.grid(row=1, column=1, padx=0, pady=0, sticky=tk.W)
        select_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_select_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_select_entry)
        clear_select_btn.grid(row=1, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

    def build_result(self):
        """
        Construct the result display area for the dictlistlib application.

        This method creates a multi-line text widget inside the `result_frame`
        for displaying query results. It configures the widget to expand with
        the frame and attaches both vertical and horizontal scrollbars for
        navigation.

        Layout Structure
        ----------------
        result_frame (grid layout)
            ├── result_textarea : tkinter.Text
            │   - Positioned at row=0, column=0
            │   - Expands to fill available space (sticky='nswe')
            ├── vscrollbar : ttk.Scrollbar (vertical)
            │   - Positioned at row=0, column=1
            │   - Controls vertical scrolling of the result text area
            └── hscrollbar : ttk.Scrollbar (horizontal)
                - Positioned at row=1, column=0
                - Controls horizontal scrolling of the result text area

        Returns
        -------
        None

        Notes
        -----
        - The text area uses `wrap='none'` to allow horizontal scrolling.
        - Scrollbars are linked to the text area via `yscrollcommand` and
          `xscrollcommand`.
        - The grid row and column are configured with weight=1 to ensure
          the text area expands when the window is resized.

        Examples
        --------
        >>> app = Application()
        >>> app.build_result()  # Creates result text area with scrollbars
        >>> app.result_textarea.insert("1.0", "Query results will appear here")
        """
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_textarea = self.TextArea(
            self.result_frame, width=20, height=5, wrap='none'
        )
        self.result_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.VERTICAL,
            command=self.result_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.HORIZONTAL,
            command=self.result_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.result_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def run(self):
        """
        Start the dictlistlib application event loop.

        This method launches the tkinter main loop, which keeps the
        application window open and responsive to user interactions
        (e.g., menu selections, button clicks, text entry). It blocks
        further code execution until the window is closed.

        Returns
        -------
        None

        Notes
        -----
        - This is the final step to make the GUI interactive.
        - The method should be called once after all widgets and
          layouts have been initialized.

        Examples
        --------
        >>> app = Application()
        >>> app.run()  # Opens the dictlistlib window and waits for user actions
        """
        self.root.mainloop()


def execute():
    """
    Entry point for launching the dictlistlib application.

    This function initializes the graphical user interface by
    creating an instance of the `Application` class and invoking
    its `run()` method. It is intended to be the main entry point
    when starting the program, ensuring that the application
    window is displayed and responsive to user interactions.

    Returns
    -------
    None

    Notes
    -----
    - This function does not accept any parameters.
    - Execution is blocked until the application window is closed,
      as `tkinter.mainloop()` runs inside `Application.run()`.
    - Typically invoked from the `__main__` block or a console
      script to start the application.
    """
    app = Application()
    app.run()
