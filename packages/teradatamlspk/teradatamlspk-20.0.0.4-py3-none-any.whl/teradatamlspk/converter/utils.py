import ast
import os, re, sys
import json, csv
import mistune
import nbformat
from enum import Enum
from collections import deque, defaultdict
from teradatamlspk.converter.object_types import spark_objects_
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader
from string import Template
import traceback, time
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradatamlspk.converter.read_write_interactive import InteractivePreferenceHandler
# Import constants from the constants file
from teradatamlspk.converter.constants import (
    ICON_PLACEHOLDER,
    NOTIFICATION_TEMPLATE,
    CODE_LINE_TEMPLATE,
    FUNCTION_API_TEMPLATE,
    SEPARATOR,
    ICON_TYPE,
    LIST_ITEM_HTML_TEMPLATE,
    EXAMPLES_SECTION_HTML_TEMPLATE,
    CODE_BLOCK_OPEN_HTML,
    CODE_BLOCK_CLOSE_HTML,
    CODE_BLOCK_HTML,
    COMMENT_HTML,
    LEFT_FILES_TEMPLATE,
    LEFT_PANE_NB_CELL,
    LEFT_PANE_NB_MARKDOWN,
    HEADER_HTML_API,
    HEADER_HTML,
    HTML_ROW_BY_MODULE_TEMPLATE,
    HTML_ROW_BY_FILE_TEMPLATE,
    CONSOLIDATED_TEMPLATE,
    TOTAL_SUMMARY,
    FILEDIR_DISPLAY_BASE,
    FILEDIR_DISPLAY_ERROR,
    FILEDIR_DISPLAY_SUCCESS,
    FILEDIR_DISPLAY_EMPTY,
    ARRAY_UDF_CONFIG
)
cloud_handler = InteractivePreferenceHandler()
combined_attributes = {
    "writeTo": ["overwrite", "overwritePartitions", "using", "tableProperty"],
    "write": ["json", "csv", "parquet", "options", "option", "format", "orc", "partitionBy", "bucketBy"],
    "read": ["csv", "json", "parquet", "format", "orc"],
    "na": "fill"
}

def _get_json(file_path):
    """ Gets the json from a file. """
    with open(file_path, encoding='utf-8') as fp:
        return json.load(fp)

temp_json =  _get_json(os.path.join(os.path.dirname(__file__), "user_notes.json"))
dynamic_json = _get_json(os.path.join(os.path.dirname(__file__), "dynamic_user_notes.json"))
class UserNoteType(Enum):
    NOT_SUPPORTED = 1
    PARTIALLY_SUPPORTED = 2
    NO_ACTION = 3


class UserNote:
    """
    DESCRIPTION:
        Represents an individual user note of Script.
    """
    def __init__(self, start_line_no, end_line_no, object_name, notes, note_type):
        self.start_line_no = start_line_no
        self.end_line_no = end_line_no
        self.object_name = object_name
        self.user_notes = notes
        self.note_type = note_type

    def to_json(self):
        return {
                "Start Line No": self.start_line_no,
                "End Line No": self.end_line_no,
                "Object Name": self.object_name,
                "Notes": self.user_notes,
                "Notification Type": self.note_type.name
                }

class NotebookUserNote:
    """
    DESCRIPTION:
        Represents an individual user note of Notebook.
    """
    def __init__(self, cell_no, start_line_no, end_line_no, object_name, notes, note_type):
        self.cell_no = cell_no
        self.start_line_no = start_line_no
        self.end_line_no = end_line_no
        self.object_name = object_name
        self.user_notes = notes
        self.note_type = note_type

    def to_json(self):
        return {
                "Cell No": self.cell_no,
                "Start Line No": self.start_line_no,
                "End Line No": self.end_line_no,
                "Object Name": self.object_name,
                "Notes": self.user_notes,
                "Notification Type": self.note_type.name
                }

class UserNotes:
    def __init__(self, user_notes):
        """
        DESCRIPTION:
            Represents a list of UserNote objects that are of a given input file
            and provides methods to manipulate and format these notes.

        PARAMETERS:
            user_notes:
                Required Argument.
                The list of UserNote objects.
                Type: List[UserNote]
        """
        self._user_notes = user_notes
        self.lines = dict()
        self.nb_lines = dict()
        self.template_dir = os.path.join(os.path.dirname(__file__), "html_template")

        # Initialize templates using the utility function.
        self.right_template = self.get_template_path("right_template.html")
        self.template = self.get_template_path("script_template.html")
        self.api_template = self.get_template_path("api_description_template.html")
        self.dir_template = self.get_template_path("directory_template.html")
        self.module_template = self.get_template_path("module_template.html")
        self.array_config_template = self.get_template_path("array_config_template.html")

    def get_template_path(self, template_name):
        """Get the full path for a given template name."""
        return os.path.join(self.template_dir, template_name)

    def to_json(self):
        """ Convert the UserNotes to JSON format."""
        json_representations = [note.to_json() for note in self._user_notes]
        return json_representations
    
    def _get_filename_html(self, filename):
        """
        DESCRIPTION:
            Generates an HTML-safe version of the filename, truncating it based on the display length.

        PARAMETERS:
            filename
                Required Argument.
                The original filename or path to be processed.
                Type: str
        
        RETURNS:
            An HTML-safe version of the filename, potentially truncated for display.
            Type: str
        """
        filename_html = f'<span class="dynamic-filename" title="{filename}">{filename}</span>'
        return filename_html

    def _flatten_list(self, nested_list):
        """
        DESCRIPTION:
            Flatten a potentially nested list into a single-level list.

        PARAMETERS:
            nested_list
                Required Argument.
                The list that may contain sublists.
                Type: list

        RETURNS:
            A flattened version of the input list.
            Type: list
        """
        
        return [item for sublist in nested_list if isinstance(sublist, list) for item in sublist] + \
            [item for item in nested_list if not isinstance(item, list)]
    
    def generate_object_summary_csv(self, object_summary_rows):
        """
        Generates a CSV file for the object summary table.

        PARAMETERS:
            object_summary_rows:
                Required Argument.
                The object summary data.
                Type: list of dictionaries.

        Returns:
            None
        """
        if not object_summary_rows:
            return
        # Flatten the list of object summary rows.
        object_summary_rows = self._flatten_list(object_summary_rows)
        
        rows = []
        # Iterate through each row in the object summary rows and create a new row for the CSV.
        for row in object_summary_rows:
            filename = row["where_found"]
            method_name = row["object_name"]
            notification = row["notification"]
            partially_supported = row["partially_supported"]
            not_supported = row["not_supported"]
            total = row["total"]

            rows.append({"Filename": filename,
                        "Method observed": method_name,
                        "Black alert": notification,
                        "Blue alert": partially_supported,
                        "Red alert": not_supported,
                        "total": total})

        # Sort rows by Filename and Method observed
        rows.sort(key=lambda x: (x["Filename"], x["Method observed"]))

        # Create the CSV filename if input is a file
        if os.path.isfile(self.filepath) and (self.filepath.endswith(".py") or self.filepath.endswith(".ipynb")):
            dir_name = os.path.dirname(self.filepath)
            base_name = os.path.basename(self.filepath)
            file_name = os.path.splitext(base_name)[0]
            csv_filename = os.path.join(dir_name, f"{file_name}_method_analysis.csv")
        else:
            # If input is a directory, create the CSV filename inside the directory.
            dir_name = self.filepath
            folder_name = os.path.basename(os.path.normpath(self.filepath))  
            csv_filename = os.path.join(dir_name, f"{folder_name}_method_analysis.csv")

        # Define the field names for the CSV file.
        fieldnames = ["Filename", "Method observed", "Black alert", "Blue alert", "Red alert", "total"]

        # Open the CSV file for writing (overwrite if exists).
        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"CSV file '{csv_filename}' generated successfully.")

    def _get_object_summary_rows(self, filename=None):
        """
        DESCRIPTION:
            This function generates summary rows for objects based on user notes.
            It categorizes objects by their support status (notification, 
            partially supported, not supported) and provides counts for each category.

        PARAMETERS:
            filename
                Required Argument.
                Optional path to a file. If not provided, it defaults to `self.filepath`.

        RETURNS:
            list:
                A list of dictionaries where each dictionary represents an object's summary.
                Each dictionary contains keys for object name, notification count, 
                partially supported count, not supported count, total count, 
                and where the object was found (filename).
        """

        object_summary_rows = []
        # Get the relative path of the file for the directory, 
        # else if only 1 script is provided, get the filename.
        if filename:
            # see for notebook these both are same so, add a condition if endswith .ipynb then need to do basename
            if filename.endswith(".ipynb"):
                filename = os.path.basename(filename)
            else:
                filename = os.path.relpath(filename, self.filepath)
        else:
            filename = os.path.basename(self.filepath)

        # As for the directory user notes will be in the form of list of list,
        # we need to flatten the list of user notes.
        flattened_user_notes = self._flatten_list(self._user_notes)

        objects = {}
        # Iterate through each note, categorize by object name and note type, 
        # and count them.
        for note in flattened_user_notes:
            obj_name = note.object_name
            note_type = note.note_type

            # If this is a new object in our dictionary, initialize its counts 
            # with zeros and set where it was found.
            if obj_name not in objects:
                objects[obj_name] = {"notification": 0, "partially_supported": 0, 
                                     "not_supported": 0, "total": 0, "where_found": filename}

            # Increment appropriate counters based on note type.
            if note_type == UserNoteType.NOT_SUPPORTED:
                objects[obj_name]["not_supported"] += 1
            elif note_type == UserNoteType.PARTIALLY_SUPPORTED:
                objects[obj_name]["partially_supported"] += 1
            elif note_type == UserNoteType.NO_ACTION:
                objects[obj_name]["notification"] += 1

            objects[obj_name]["total"] += 1

        # Create rows for each object with its summary data.
        for object_name, counts in objects.items():
            # For each unique object name collected above create a row 
            # that summarizes its status across different categories .
            object_summary_rows.append({
                "object_name": object_name,
                "notification": counts["notification"],
                "partially_supported": counts["partially_supported"],
                "not_supported": counts["not_supported"],
                "total": counts["total"],
                "where_found": counts["where_found"]
            })

        return object_summary_rows
    
    def get_overview_table(self, object_summary_rows=None, csv_report=False):
        """
        DESCRIPTION:
            This function generates an HTML table providing an overview of 
            objects based on their support status. It categorizes objects by 
            notifications, partially supported features, and not supported features.

        PARAMETERS:
            object_summary_rows:
                Optional Argument 
                of dictionaries containing object summaries. If not provided,
                it defaults to the result of `_get_object_summary_rows()`.

            csv_report:
                Optional Argument.
                If True, the function will also generate a CSV file for the object summary.
                Type: bool
                Default Value: False

        RETURNS:
            An HTML string representing the overview table.
            Type: str
        """
        if object_summary_rows is None:
            object_summary_rows = self._get_object_summary_rows()

        # Generate the CSV file only if csv_report is True
        if csv_report:
            self.generate_object_summary_csv(object_summary_rows)

        # Initialize total counters
        total_not_supported = 0
        total_partially_supported = 0
        total_notification = 0
        total_count = 0
        html_rows = ""

        # flatten object_summary_rows
        if object_summary_rows:
            flattend_rows = self._flatten_list(object_summary_rows)

            # sort the rows based on object name and then by where found.
            flattend_rows = sorted(flattend_rows, key=lambda row: (row["where_found"], row["object_name"]))
            # To keep track of object names and their combined "Where Found" locations
            object_summary = {}

            # Process rows and combine where found for the same object
            for row in flattend_rows:
                # Get the HTML version of the filename for display.
                filename_html = self._get_filename_html(row["where_found"])
                object_name = row["object_name"]
                if object_name not in object_summary:
                    object_summary[object_name] = {
                        "notification": 0,
                        "partially_supported": 0,
                        "not_supported": 0,
                        "total": 0,
                        "where_found": []
                    }
                
                # Update the object summary data
                object_summary[object_name]["notification"] += row["notification"]
                object_summary[object_name]["partially_supported"] += row["partially_supported"]
                object_summary[object_name]["not_supported"] += row["not_supported"]
                object_summary[object_name]["total"] += row["total"]
                object_summary[object_name]["where_found"].append(filename_html)

                # Only add unique "where_found" values
                if filename_html not in object_summary[object_name]["where_found"]:
                    object_summary[object_name]["where_found"].append(filename_html)

            # Build the HTML rows from the dictionary data
            for object_name, summary in object_summary.items():
                total_notification += summary["notification"]
                total_partially_supported += summary["partially_supported"]
                total_not_supported += summary["not_supported"]
                total_count += summary["total"]
                
                where_found = self._get_notes(summary["where_found"])

                # Build the HTML table row for the current object using its name and counts.
                html_rows += HTML_ROW_BY_MODULE_TEMPLATE.format(object_name=object_name,
                                                                notification=summary['notification'],
                                                                partially_supported=summary['partially_supported'],
                                                                not_supported=summary['not_supported'],
                                                                total=summary['total'],
                                                                where_found=where_found)

        env = Environment(loader=FileSystemLoader(os.path.dirname(self.module_template)))
        # Load and render the template
        template = env.get_template(os.path.basename(self.module_template))

        return template.render( 
                                html_rows=html_rows,
                                not_supported = ICON_TYPE["NOT_SUPPORTED"],
                                partially_supported = ICON_TYPE["PARTIALLY_SUPPORTED"],
                                notification = ICON_TYPE["NO_ACTION"],
                                total_notification=total_notification,
                                total_partially_supported=total_partially_supported,
                                total_not_supported=total_not_supported,
                                total_count=total_count)

    def _get_consolidated_rows(self, filename=None):
        """
        DESCRIPTION:
            Consolidates user notes for a given file, counting occurrences of each note type.

        PARAMETERS:
            filename: 
                Optional Argument.
                The name of the file to process. If None, uses self.filepath.
                Type: str

        RETURNS:
            A dictionary containing the consolidated counts for each note type.
            Type: dict
        """

        # Get the relative path of the file for the directory, 
        # else if only 1 script is provided, get the filename.
        # see for notebook these both are same so, add a condition if endswith .ipynb then need to do basename
        if filename:
            if filename.endswith(".ipynb"):
                filename = os.path.basename(filename)
            else:
                filename = os.path.relpath(filename, self.filepath)
        else:
            filename = os.path.basename(self.filepath)
        # Flatten the nested list of user notes into a single list.
        flattened_user_notes = self._flatten_list(self._user_notes)
        # Initialize counters
        black_notes_count = 0
        blue_notes_count = 0
        red_notes_count = 0

        # Count the notes by type and get HTML classes
        for note in flattened_user_notes:
            if note.note_type == UserNoteType.NO_ACTION:
                black_notes_count += 1
            elif note.note_type == UserNoteType.PARTIALLY_SUPPORTED:
                blue_notes_count += 1
            elif note.note_type == UserNoteType.NOT_SUPPORTED:
                red_notes_count += 1

        # Calculate the total count of notes.
        total_count = black_notes_count + blue_notes_count + red_notes_count
        # Return a dictionary instead of an HTML row
        return {
            "filename": filename,
            "user_error": 0,  # Indicate it's a processed file.
            "utility_error": 0,
            "empty_file": 0,
            "notification": black_notes_count,
            "partially_supported": blue_notes_count,
            "not_supported": red_notes_count,
            "total": total_count
        }
    
    def get_consolidated_table(self, consolidated_rows=None):
        """
        DESCRIPTION:
            Creates an HTML table summarizing compatibility for PySpark workloads, 
            grouping features into notifications, partially supported, and not supported categories.

        PARAMETERS:
            consolidated_rows:
                Optional Argument.
                List of dictionaries containing consolidated data per file. If None,
                defaults to a list containing the result of `_get_consolidated_rows()`.
                Type: List[Dict]

        RETURNS:
            An HTML string representing the consolidated table.
            Type: str
        """
        if consolidated_rows is None:
            consolidated_rows = [self._get_consolidated_rows()]

        # Initialize total counters
        total_not_supported = 0
        total_partially_supported = 0
        total_notification = 0
        total_count =0

        # sort the rows based on filename and then by notification, partially supported, not supported and total
        if consolidated_rows:
            consolidated_rows = sorted(consolidated_rows, key=lambda row: (row["filename"], row["notification"], \
                                                                           row["partially_supported"], row["not_supported"],
                                                                           row["total"]))

        # Build the HTML rows from the dictionary data
        html_rows = ""
        for row in consolidated_rows:
            filename_html = self._get_filename_html(row["filename"])
            user_error = row["user_error"]
            utility_error = row["utility_error"]
            error = "UE" if utility_error else "SE" if user_error else "0"
            empty_file = row["empty_file"]
            total_not_supported += row["not_supported"]
            total_partially_supported += row["partially_supported"]
            total_notification += row["notification"]
            total_count += row["total"]

            html_rows += HTML_ROW_BY_FILE_TEMPLATE.format(filename_html=filename_html,
                                                          error=error,
                                                          empty_file=empty_file,
                                                          notification=row['notification'],
                                                          partially_supported=row['partially_supported'],
                                                          not_supported=row['not_supported'],
                                                          total=row['total'])

        return CONSOLIDATED_TEMPLATE.format(html_rows=html_rows,
                                            bug_report = ICON_TYPE["BUG_REPORT"],
                                            empty_file = ICON_TYPE["EMPTY_FILE"],
                                            not_supported = ICON_TYPE["NOT_SUPPORTED"],
                                            partially_supported = ICON_TYPE["PARTIALLY_SUPPORTED"],
                                            notification = ICON_TYPE["NO_ACTION"])
    

    def to_html(self, csv_report=False, consolidated_rows=None, highlighted_code=None, error_type=None):
        """
        DESCRIPTION:
            The function generates the HTML representation the script conversion report by
            combining the right pane HTML, script or notebook content along with any
            associated API descriptions.
        
        PARAMETERS:
            csv_report
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

            consolidated_rows:
                Optional Argument.
                List of dictionaries containing consolidated data per file.
                Type: List[Dict]
            
            highlighted_code:
                Optional Argument.
                The highlighted code to be displayed in the HTML report.
                Type: str
            
            error_type:
                Optional Argument.
                The type of error for which the highlighted code is generated.
                Type: str

        RETURNS:
            A string containing the HTML representation of the script conversion report.
        """
        array_functions = {'array', 'array_overslap', 'array_contains', 'array_join', 'slice', 'array_position', 'element_at', \
                           'array_append', 'array_sort', 'array_insert', 'array_remove', 'array_prepend', 'array_distinct', \
                           'array_intersect', 'array_union', 'array_except', 'array_compact', 'explode', 'explode_outer', \
                           'pos_explode', 'posexplode_outer', 'get', 'sort_array', 'array_max', 'array_min', 'shuffle', \
                           'sequence', 'array_repeat', 'try_element_at', 'array_agg'}
        flattened_user_notes = self._flatten_list(self._user_notes)
        has_array_functions = any(note.object_name in array_functions for note in flattened_user_notes)
        if has_array_functions:
            with open(self.array_config_template, "r") as file:
                array_config_html = file.read()
        else:
            array_config_html = ""

        # Check if there are any UDF related user notes to include UDF configuration section.
        array_udf = any(note.object_name == "udf" for note in flattened_user_notes)
        # Filter out UDF notes while maintaining the structure of _user_notes
        filtered_notes = []
        for item in self._user_notes:
            if isinstance(item, list): # It's a list of UserNote objects
                filtered_notes.append([note for note in item if note.object_name != "udf"])
            else:  # It's a direct UserNote object, filter it
                if item.object_name != "udf":
                    filtered_notes.append(item)
        self._user_notes = filtered_notes
        if array_udf:
            array_udf_html = ARRAY_UDF_CONFIG
        else:
            array_udf_html = ""
                
        with open(self.right_template, "r") as file:
            template = Template(file.read())
        
        # Get the right pane HTML and substitute the file name and icons.
        right_pane_html =  template.safe_substitute(file_name= os.path.basename(self.filepath),
                                                    not_supported = ICON_TYPE["NOT_SUPPORTED"],
                                                    partially_supported = ICON_TYPE["PARTIALLY_SUPPORTED"],
                                                    notification = ICON_TYPE["NO_ACTION"],
                                                    bug_report = ICON_TYPE["BUG_REPORT"],
                                                    empty_file = ICON_TYPE["EMPTY_FILE"],
                                                    success_file = ICON_TYPE["SUCCESS_FILE"],
                                                    total_summary="", # Total summary is not required for single script/notebook.
                                                    overview_table = self.get_overview_table(csv_report=csv_report) if highlighted_code is None else "",
                                                    consolidated_table = self.get_consolidated_table(consolidated_rows) 
                                                    if consolidated_rows else self.get_consolidated_table(),
                                                    array_config_options=array_config_html,
                                                    array_udf_config=array_udf_html)
        
        # Indicates this particular call is from errored files.
        if highlighted_code:
            highlighted_spkcode = None
            # For empty file, no need of bell icon.
            if error_type == "empty_file":
                highlighted_code = highlighted_code
                function_details = ""
            else:
                noti = NOTIFICATION_TEMPLATE.format(counter=f"{os.path.basename(self.filepath)}-{1}-{None}",
                                                                icon=ICON_TYPE["NOT_SUPPORTED"])
                highlighted_code = f"<div>{noti}</div><pre>{highlighted_code}</pre>"
                
                # Get the details of the corresponding error type.
                description = self._get_function_details(temp_json.get("not_supported")[error_type])

                function_details = FUNCTION_API_TEMPLATE.format(counter=f"{os.path.basename(self.filepath)}-1-{None}",
                                                                details=description)
            
        else:
            # Get the pyspark, tdmlspk code, and function details to be displayed in the HTML report.
            highlighted_code, highlighted_spkcode, function_details = self._get_html_data()

        # Load the template using Jinja2.
        env = Environment(loader=FileSystemLoader(os.path.dirname(self.template)))
        template = env.get_template(os.path.basename(self.template))

        # Render the template with the provided data.
        full_html = template.render(css_styles=HtmlFormatter().get_style_defs(".highlight"),
                                    highlighted_code=highlighted_code,
                                    highlighted_tdmlspk_code = highlighted_spkcode,
                                    right_pane=right_pane_html,
                                    function_details="".join(function_details),
                                    file_name=os.path.basename(self.filepath))
        
        return full_html
    
    def _get_html_data(self, file_path=None):
        """
        DESCRIPTION:
            Reads the content of a specified script file, processes the code lines
            to highlight them, and generates an HTML representation of the code along with any
            associated API descriptions.
            
        PARAMETERS:
            file_path:
                Optional Argument. 
                The path to the file.
                Type: str

        RETURNS:
            Tuple containing highlighted code and function details.    
        """

        file_name = file_path if file_path else self.filepath
        with open(file_name, "r", encoding="utf-8") as file:
            code_lines = file.read().splitlines()

        tdmlspk_path = file_name[:-3]+"_tdmlspk.py"
        if os.path.exists(tdmlspk_path):
            with open(tdmlspk_path, "r", encoding="utf-8") as file:
                tdmlspk_code = file.read().splitlines()

        self._get_combined_user_note()
        # Get the highlighted code and function details for pyspark script.
        highlighted_lines, function_details = self.highlight_code_lines(code_lines,
                                                                        self.lines,
                                                                        os.path.basename(file_name))
      
        # As function details are not required get only the highlighted code for teradatamlspk script.
        highlighted_spkcode, _ = self.highlight_code_lines(tdmlspk_code, 
                                                           file_name=os.path.basename(tdmlspk_path))
        
        # Combine highlighted lines and error details into HTML.
        highlighted_spkcode = "\n".join(highlighted_spkcode)
        highlighted_code = "\n".join(highlighted_lines)

        return highlighted_code, highlighted_spkcode, function_details
    
    def highlight_code_lines(self, code_lines, notification_lines=None, file_name=None, cell_counter=None):
        """
        DESCRIPTION:
            Highlight code lines with notification icons and generate function details for each notification.
        
        PARAMETERS:
            code_lines:
                Required Argument.
                List of code lines.
                Type: List[str]

            notification_lines:
                Optional Argument.
                Dictionary of notification lines.
                Type: Dict[int, List[Tuple[str, str]]]

            file_name:
                Optional Argument.
                The name of the file.
                Type: str

            cell_counter:
                Optional Argument.
                The cell number.
                Type: int

        RETURNS:
            Tuple containing highlighted lines and error details.

        EXAMPLE:
            >>> code = [
            ...     "print('Hello, World!')",
            ...     "result = 1 + 2",
            ...     "# This is a comment",
            ...     "print(result)"
            ... ]
            >>> notifications = {
            ...     2: [("Line 2", "PARTIALLY_SUPPORTED")],
            ...     4: [("Line 4", "NOT_SUPPORTED")]
            ... }
            >>> highlighted_lines, function_details = highlight_code_lines(code, notifications)
            >>> print(highlighted_lines)
            ['<div class="code-line"><div class="line-number">1</div><div class="notification">...</div><div class="highlighted-line">...</div></div>', ...]
            >>> print(function_details)
            ['<div class="error-detail">...</div>', ...]

        """

        formatter = HtmlFormatter(cssclass="highlight")
        highlighted_lines, function_details = [], []
        notification_counter = 1  # For notification icons
        
        # Get the function details from the JSON file.
        not_supported = temp_json.get("not_supported")
        partially_supported = temp_json.get("partially_supported")
        notifications = temp_json.get("notification")

        for index, line in enumerate(code_lines):
            indexes = highlight(f"{index + 1}", PythonLexer(), formatter)
            highlighted_line = highlight(line, PythonLexer(), formatter)

            # pygments highlights '!', '`' as syntax error.
            # A syntax error are already handled as part of code processing.
            # In HTML report, the syntax error won't be highlighted.
            highlighted_line = highlighted_line.replace('class="err"', '')

            # Default notification icon and class.
            noti = ICON_PLACEHOLDER
            if notification_lines and (index + 1) in notification_lines:
                # Fetch the relevant heading for this line number.
                headings = notification_lines[index + 1]
                headings = sorted(headings, key=lambda x: x[0])

                # Get the icon based on the heading type.
                for heading in headings:
                    if heading[1] in ICON_TYPE:
                        icon = ICON_TYPE[heading[1]]
                        noti = NOTIFICATION_TEMPLATE.format(counter=f"{file_name}-{notification_counter}-{cell_counter}",
                                                            icon=icon)
                
                notification_counter += 1

            # Get the file name if provided, else use the from self.filepath.
            filename =  file_name if file_name else self.filepath
            # Add line number if the file is a Python script.
            line_number = f"<div class='line-number'>{indexes}</div>" if filename.endswith('.py') else ""

            # Add the highlighted line with the notification icon.
            highlighted_lines.append(CODE_LINE_TEMPLATE.format(line_number=line_number,
                                                               notification=noti,
                                                               highlighted_line=highlighted_line))

        if notification_lines:
            notification_counter = 1
            # Generate function details for each notification.
            for _, notification_line in sorted(notification_lines.items()):
                notification_line = sorted(notification_line, key=lambda x: x[0])
                details_list = []

                for heading in notification_line:
                    # Initialize description as None by default.
                    description = None

                    # For specific keywords like "setFeaturesCol", "setInputCol",
                    # "setInputCols","inputCol","inputCols", "featuresCol", 
                    # and UDFs, the notes are populated conditionally during processing. 
                    # If we directly add them to main json, the notes would be populated  
                    # for every occurrence, regardless of whether the conditions are met. 
                    # To handle this, we use a separate dynamic_json to manage these cases, 
                    # and fetch the corresponding description details dynamically when required.
                    if heading[0] in ["setFeaturesCol", "setInputCol", "setInputCols","inputCol",\
                                    "inputCols", "featuresCol"]:
                        description = self._get_function_details(dynamic_json["input_list"], name=heading[0])

                    elif heading[0] in ["cast", "astype"]:
                        description = self._get_function_details(dynamic_json[heading[1]][heading[0]])
                
                    elif heading[0] in dynamic_json:
                        description = self._get_function_details(dynamic_json[heading[0]])

                    # Check in not_supported.
                    elif heading[0] in not_supported:
                        description = self._get_function_details(not_supported[heading[0]])

                    # Check in partially_supported.
                    elif heading[0] in partially_supported:
                        description = self._get_function_details(partially_supported[heading[0]])

                    # Check in notifications.
                    elif heading[0] in notifications:
                        description = self._get_function_details(notifications[heading[0]])

                    # If description is a list, convert it to a string.
                    if isinstance(description, list):
                        description = "\n".join(description)

                    details_list.append(f"<p>{description}</p>\n")

                details = SEPARATOR.join(details_list)

                # Add the error details to the list.
                function_details.append(FUNCTION_API_TEMPLATE.format(counter=f"{file_name}-{notification_counter}-{cell_counter}",
                                                                details=details))
                notification_counter += 1

        return highlighted_lines, function_details

    def _get_function_details(self, api_data, name=None):
        """
        DESCRIPTION:
            Retrieves and formats function details from the specified examples file,
            generating an HTML representation of PySpark and teradatamlspk code examples.

        PARAMETERS:
            api_data:
                Required Argument.
                The API data.
                Type: Dict

            name:
                Optional Argument.
                The name of the keyword.
                Type: str

        RETURNS:
            The HTML representation of the function details.

        EXAMPLE:
            >>> api_data = {
            ...     'examples': 'path/to/examples.txt',
            ...     'notes': ['This API supports X features']
            ...     'user_action': ['Perform Y action to use this API'],
            ...     'Name': 'Sample API'
            ... }
            >>> html_output = _get_function_details(api_data)
            >>> print(html_output)
                <div class="function-details">
                    <h2>Sample API</h2>
                    <div class="notes">
                        <p>This API supports X features</p>
                    </div>
                    <div class="user-action">
                        <p>Perform Y action to use this API</p>
                    </div>
                    <div class="examples">
                        <a href="path/to/examples.txt">Examples</a>
                    </div>
                </div>
        """
        examples_file_path = os.path.join(os.path.dirname(__file__), api_data['examples'])
        # Final HTML content.
        examples_content = ""  
        # block_open = False

        # Try to read the examples file, handle file not found.
        try:
            with open(examples_file_path, 'r') as file:
                lines = file.readlines()
            # If the file is found, read its content and format it as HTML.
            examples_content += CODE_BLOCK_OPEN_HTML

            for line in lines:
                examples_content += line
                    
            examples_content += CODE_BLOCK_CLOSE_HTML

        # In mac and linux os, IsADirectoryError is raised if the file is a directory.
        except (FileNotFoundError, IsADirectoryError):
            # If the file is not found, examples_content remains empty.
            examples_content = None
        
        # If the examples content is not empty, then add the notes for the corresponding API.
        if examples_content:
            if api_data['examples'] in ["examples/to_utc_timestamp.txt", "examples/from_utc_timestamp.txt", "examples/convert_timezone.txt",
                                        "examples/make_timestamp_ltz.txt", "examples/to_timestamp_ntz.txt", "examples/conf_set.txt"]:
                examples_content+= CODE_BLOCK_OPEN_HTML

                # Add the notes for the corresponding API.
                notes_file_path = os.path.join(os.path.dirname(__file__), "examples/time_notes.txt")
                with open(notes_file_path, 'r') as notes_file:
                    notes_lines = notes_file.readlines()
                    for notes_line in notes_lines:
                        examples_content += notes_line

            examples_content += CODE_BLOCK_CLOSE_HTML

        elif api_data['examples'] in ["examples/to_char.txt", "examples/to_varchar.txt"]:
            examples_content = CODE_BLOCK_OPEN_HTML
            notes_file_path = os.path.join(os.path.dirname(__file__), "examples/char_notes.txt")

            # Add the notes for the corresponding API.
            with open(notes_file_path, 'r') as notes_file:
                notes_lines = notes_file.readlines()
                for notes_line in notes_lines:
                    examples_content += notes_line
            
            examples_content += CODE_BLOCK_CLOSE_HTML
                    

        # Format the heading based on the name.
        if name is None and api_data['Name'] in ["Syntax Error", "Utility Error"]:
            heading_html = f"<h2 class='head-2'>{api_data['Name']}</h2>"
            section_heading = ""
        else:
            heading_html = HEADER_HTML.format(name=name) if name else HEADER_HTML_API.format(name=api_data['Name'])
            section_heading = '<h3 class="head-3">Differences</h3>'
        
        # Format notes and user actions using the same template
        notes_html = "".join([LIST_ITEM_HTML_TEMPLATE.format(item=note) 
                              for note in api_data['notes']])
        user_action_html = "".join([LIST_ITEM_HTML_TEMPLATE.format(item=action) 
                                    for action in api_data['user_action']])

        # Generate the examples section if content is available.
        if examples_content:
            examples_section = EXAMPLES_SECTION_HTML_TEMPLATE.format(examples_content=examples_content)
        else:
            examples_section = ""  # Omit section if content is empty


        env = Environment(loader=FileSystemLoader(os.path.dirname(self.api_template)))
        # Load and render the template
        template = env.get_template(os.path.basename(self.api_template))
        return template.render(heading_html=heading_html,
                               section_heading=section_heading,
                               notes_html=notes_html,
                               examples_section=examples_section,
                               user_action_html=user_action_html)

    @staticmethod
    def _get_notes(notes):
        """ Get the notes in HTML format string."""
        if isinstance(notes, list):
            return "".join([LIST_ITEM_HTML_TEMPLATE.format(item=note) for note in notes])
        return notes

    @staticmethod
    def _get_html_cls(notification_type):
        """ Get the HTML class based on the notification type."""
        if notification_type == UserNoteType.PARTIALLY_SUPPORTED.name:
            return "partially_supported"
        elif notification_type == UserNoteType.NOT_SUPPORTED.name:
            return "not_supported"
        return "notification"

    def extract_cell_no_key(self, cell_no):
        # Extract the non-numeric and numeric parts of the cell_no for sorting in html table.
        match = re.match(r"([^\d]*)(\d*)", str(cell_no))
        # Return a tuple of the non-numeric part and the numeric part as an integer.
        return (match.group(1), int(match.group(2) or 0))

    @staticmethod
    def process_notification_type(self, type_notes):
        """
        DECSRIPTION:
            Process notes of a specific notification type and combine line numbers.

        PARAMETERS:
            type_notes
                List of UserNote or NotebookUserNote objects of the same notification type.

        RETURNS:
            A dictionary containing the combined record for the notification type.
        """

        for note in type_notes:
            if note.start_line_no and note.end_line_no:
                # Group notes by line numbers for tracking, which is further used
                # in displaying bell icons for these lines to indicate where notes apply.
                # If the line number is already present, append the note to the existing list.
                if note.start_line_no in self.lines:
                    # Add only if the note is not already present.
                    self.lines[note.start_line_no].add((note.object_name, note.note_type.name))
                else:
                    self.lines[note.start_line_no] = {(note.object_name, note.note_type.name)}
  
class ScriptNotes(UserNotes):
    def __init__(self, user_notes, filepath):
        super().__init__(user_notes)
        self.filepath = filepath
    
    def _get_combined_user_note(self):
        """
        DESCRIPTION:
            Processes user notes to get the combined record for the notification type.
            It flattens nested user notes, groups them by object_name and combines 
            relevant information for the line numbers.

        PARAMETERS:
            None

        RETURNS:
            None
        """

        # Flatten the nested list of user notes into a single list.
        if isinstance(self._user_notes, UserNote):
            flat_user_notes = [self._user_notes]
        elif isinstance(self._user_notes, list):
            flat_user_notes = self._flatten_list(self._user_notes)

        # Group notes by object_name
        grouped_notes = defaultdict(list)
        for note in flat_user_notes:
            grouped_notes[note.object_name].append(note)

        for _ , notes in grouped_notes.items():
            notes_by_type = defaultdict(list)

            for note in notes:
                notes_by_type[note.note_type].append(note)

            for _ , type_notes in notes_by_type.items():
                self.process_notification_type(self, type_notes)

     
class DirectoryNotes(UserNotes):

    def __init__(self, user_notes, filepath, file_name=None):
        super().__init__(user_notes)
        self.filepath = filepath
        self.file_name = file_name

    def _get_tables(self, object_summary_rows, consolidated_rows, csv_report=False):
        """
        DESCRIPTION:
            Generates HTML content for the right pane report by processing conversion data.
            Performs three main operations:
            1. Processes consolidated rows to calculate conversion statistics
            2. Generates HTML tables for overview and consolidated data
            3. Populates a Jinja template with calculated metrics and generated tables

        PARAMETERS:
            object_summary_rows:
                Required Argument.
                List of dictionaries containing object summaries.
                Type: List[Dict]

            consolidated_rows:
                Required Argument.
                List of dictionaries containing consolidated data per file.
                Type: List[Dict]

            csv_report:
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

        RETURNS:
            None
        """
        with open(self.right_template, "r", encoding="utf-8") as file:
            template = Template(file.read())

        total_files_processed = 0
        total_files_converted = 0
        total_files_not_converted = 0
        py_files_processed = 0
        ipynb_files_processed = 0
        total_user_errors = 0
        total_utility_errors = 0
        total_empty_files = 0

        # Iterate through the files and check the statuses
        for row in consolidated_rows:
            total_files_processed += 1
             
            # Determine file type
            if row["filename"].endswith(".py"):
                py_files_processed += 1
            elif row["filename"].endswith(".ipynb"):
                ipynb_files_processed += 1

            # Converted files
            if row["user_error"] == 0 and row["utility_error"] == 0 and row["empty_file"] == 0:  
                total_files_converted += 1

            # Not converted (errored files)
            else:
                # Empty files
                if row["empty_file"] == 1:
                    total_empty_files += 1
                else:
                    total_files_not_converted += 1
                    if row["user_error"] == 1:
                        total_user_errors += 1
                    if row["utility_error"] == 1:
                        total_utility_errors += 1

        # Get the HTML representation of the overview and consolidated tables.
        consolidated_table = self.get_consolidated_table(consolidated_rows)
        overview_table = self.get_overview_table(object_summary_rows, csv_report=csv_report)

        # Generate the total summary for the directory.
        total_summary = TOTAL_SUMMARY.format(total_files_processed=total_files_processed,
                                            py_files_processed=py_files_processed,
                                            ipynb_files_processed=ipynb_files_processed,
                                            total_files_converted=total_files_converted,
                                            total_files_not_converted=total_files_not_converted,
                                            total_user_errors=total_user_errors,
                                            total_empty_files=total_empty_files,
                                            total_utility_errors=total_utility_errors)


        # safe_substitute replaces placeholders with the provided dynamic values.
        self.right_pane_html =  template.safe_substitute(file_name=os.path.basename(self.filepath),
                                                        not_supported = ICON_TYPE["NOT_SUPPORTED"],
                                                        partially_supported = ICON_TYPE["PARTIALLY_SUPPORTED"],
                                                        notification = ICON_TYPE["NO_ACTION"],
                                                        bug_report = ICON_TYPE["BUG_REPORT"],
                                                        empty_file = ICON_TYPE["EMPTY_FILE"],
                                                        success_file = ICON_TYPE["SUCCESS_FILE"],
                                                        total_summary = total_summary,
                                                        overview_table = overview_table,
                                                        consolidated_table = consolidated_table)

    def _get_combined_user_note(self):
        """
        DESCRIPTION:
            Processes user notes to get the combined record for the notification type 
            for the directory files

        PARAMETERS:
            None

        RETURNS:
            None
        """

        if self.file_name.endswith('.py'):
            ScriptNotes._get_combined_user_note(self)
        else:
            NotebookNotes._get_combined_user_note(self)

class NotebookNotes(UserNotes):
    
    def __init__(self, user_notes, filepath):
        super().__init__(user_notes)
        self.filepath = filepath

    def _process_cells(self, notebook, is_tdmlspk=False):
        """
        DESCRIPTION:
            Processes the code lines and markdown cells of a pyspark and teradatamlspk 
            notebook to highlight them, generates an HTML representation of the code along 
            with their API descriptions.
            - For PySpark notebooks, function details are also extracted.
            - For teradatamlspk notebooks, only code highlighting is performed.

        PARAMETERS:
            notebook:
                Required Argument.
                The notebook object.
                Type: nbformat.NotebookNode

            is_tdmlspk:
                Optional Argument.
                Flag to check if the notebook is a teradatamlspk notebook.
                Type: bool

        RETURNS:
            for PySpark notebook:
                left_pane_content:
                    The processed HTML content for the left pane.
                    Type: str
                
                function_details:
                    Extracted function details from the code cells.
                    Type: List[str]

            for teradatamlspk notebook:
                left_pane_content:
                    The processed HTML content for the left pane.
                    Type: str
            
        """
        left_pane_content = ""
        empty_cell = 1
        # Function details are only collected for PySpark notebook.
        function_details = [] if not is_tdmlspk else None
        for cell in notebook.cells:

            # Process code cells.
            if cell.cell_type == "code":
                notification_lines = dict()
                code_lines = cell.source.splitlines()
                # Prepare execution count text
                execution_count = f"[{cell.execution_count}]:" if cell.execution_count else "[&nbsp;]:"
                cell_no = cell.execution_count if cell.execution_count else f"Empty Cell {empty_cell}"
                if cell_no in self.nb_lines:
                    notification_lines = self.nb_lines[cell_no]

                # For teradatamlspk notebook, only highlight the code lines, 
                # as bell icons are not required for tdmlspk.
                if is_tdmlspk:
                    highlighted_lines, _ = self.highlight_code_lines(code_lines)

                # For pyspark notebook, highlight the code lines and collect function details.
                else:
                    highlighted_lines, function_details_ = self.highlight_code_lines(code_lines,
                                                                                     notification_lines, 
                                                                                     os.path.basename(self.filepath),
                                                                                     cell_no)
                    function_details.extend(function_details_)

                # Combine highlighted lines and function details into HTML.
                left_pane_content += LEFT_PANE_NB_CELL.format(execution_count=execution_count,
                                                              highlighted_code="\n".join(highlighted_lines))
                
                # Only increment the empty cell counter if the cell is empty.
                if cell.execution_count is None:
                    empty_cell += 1
                    
            # Process markdown cells.
            elif cell.cell_type == "markdown":
                html_content = mistune.create_markdown()(cell.source)
                left_pane_content += LEFT_PANE_NB_MARKDOWN.format(highlighted_code=html_content)


        return (left_pane_content, function_details) if not is_tdmlspk else left_pane_content

    def _get_html_data(self, file_path=None):
        """
        DESCRIPTION:
            Reads the content of a specified pyspark and teradatamlspk notebook file, gets the
            combined user notes, and processes both notebooks for generating content for the 
            left pane and function details.

        PARAMETERS:
            file_path:
                Optional Argument. 
                The path to the file.
                Type: str

        RETURNS:
            left_pane_content:
                The content to be displayed in the left pane processed from the pyspark notebook.
                Type: str

            tdmlspk_content:
                The content to be displayed in the left pane processed from the teradatamlspk notebook.
                Type: str

            function_details:
                The function details to be displayed in the right pane.
                Type: str

        """
        
        file_name = file_path if file_path else self.filepath
        with open(file_name, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        tdmlspk_path = self.filepath[:-6]+"_tdmlspk.ipynb"
        if os.path.exists(tdmlspk_path):
            with open(tdmlspk_path, 'r', encoding='utf-8') as f:
                tdmlspk_notebook = nbformat.read(f, as_version=4)
        
        self._get_combined_user_note()
        left_pane_content, function_details = self._process_cells(notebook)
        tdmlspk_content = self._process_cells(tdmlspk_notebook, is_tdmlspk=True)

        return left_pane_content, tdmlspk_content, function_details
      
    def _get_combined_user_note(self):
        """
        DESCRIPTION:
            Processes user notes to to get the combined record for the notification type.
            It flattens nested user notes, groups them by cell_no and object_name,
            and combines relevant information for the line numbers.

        PARAMETERS:
            None

        RETURNS:
            None
        """
        # Flatten the nested list of user notes into a single list, handling both UserNote and list cases.
        if isinstance(self._user_notes, NotebookUserNote):
            flat_user_notes = [self._user_notes]
        elif isinstance(self._user_notes, list):
            flat_user_notes = []
            for item in self._user_notes:
                if isinstance(item, list):
                    flat_user_notes.extend(item)
                elif isinstance(item, NotebookUserNote):
                    flat_user_notes.append(item)

        # Group notes by cell_no first and then by object_name.
        grouped_cell_no = defaultdict(list)
        for note in flat_user_notes:
            grouped_cell_no[note.cell_no].append(note)

        for _, cell_notes in grouped_cell_no.items():
            # Group notes by object_name and combine them.
            grouped_notes = defaultdict(list)
            for note in cell_notes:
                grouped_notes[note.object_name].append(note)

            # Create combined records.
            for _, object_notes in grouped_notes.items():
                notes_by_type = defaultdict(list)
                for note in object_notes:
                    notes_by_type[note.note_type].append(note)

                for _, type_notes in notes_by_type.items():
                    self.process_notification_type(self, type_notes)

            self.nb_lines[note.cell_no] = self.lines
            self.lines = dict()                    


class PyCode:

    def __init__(self, code_or_ast, parse_function_body=False):
        self.__ast = code_or_ast
        self.__parse_function_body = parse_function_body
        
    def get_statements(self):
        """
        DESCRIPTION:
            Function to get all the corresponding python statements one by one.

        PARAMETERS:
            None

        RETURNS:
            generator:
                Yields AST objects from the script.
                Type: ast.AST
        """
        # If input is of code then parse it.
        if isinstance(self.__ast, str):
            self.__ast = ast.parse(self.__ast)

        for node in self._get_python_stmts(self.__ast):
            yield node  


    def _get_python_stmts(self, node):
        """
        DESCRIPTION:
            Yields Python statements from an AST node, recursively processing nested structures.

        PARAMETERS:
            node:
                Required Argument.
                The AST node to process.
                Type: ast.AST

        RETURNS:
            generator:
                Yields individual AST nodes representing Python statements.
                Type: ast.AST
        """
        # Check if the node is one of the target types and yield it.
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Expr, ast.Assign,
                             ast.AnnAssign, ast.Constant)):
            yield node

        elif isinstance(node, ast.Return):
            if node.value:  # Check if there's a return value
                yield node.value
            else:
                yield node 
        elif isinstance(node, ast.FunctionDef):
            # If the node has a body, recursively yield statements from it.
            for decorator in node.decorator_list:
                yield decorator
            yield node
            if self.__parse_function_body:
                for stmt in node.body:
                    yield from self._get_python_stmts(stmt)

        elif isinstance(node, ast.Try):
            # Yield the try node itself.
            yield node
            # Yield all statements in the try block.
            for stmt in node.body:
                yield from self._get_python_stmts(stmt)
            # Yield all handlers (except blocks)
            for handler in node.handlers:
                yield from self._get_python_stmts(handler)
            # Yield all statements in the finally block, if it exists.
            for stmt in node.finalbody:
                yield from self._get_python_stmts(stmt)

        # Some of the objects will have body. Make sure to process it too.
        # However, do not yield function body. They should be processed during
        # the call of function.
        elif hasattr(node, 'body') and (not isinstance(node, ast.FunctionDef)):
            for stmt in node.body:
                yield from self._get_python_stmts(stmt)

        if hasattr(node, 'orelse'):
            # If the node has an orelse, recursively yield statements from it.
            for stmt in node.orelse:
                yield from self._get_python_stmts(stmt)

class _ImportParser:
    """
    DESCRIPTION:
        Parses the individual import statement.
    """
    def __init__(self, ast_obj, invalid_imports):
        self.node = ast_obj
        self.invalid_imports = invalid_imports

    def get_imports(self):
        """
        DESCRIPTION:
            Parses an import statement and returns the new import statement along with any invalid imports.

        PARAMETERS:
            node:
                Required Argument.
                The AST node representing an import statement.
                Types: ast.Import, ast.ImportFrom

        RETURNS:
            tuple:
                A tuple containing four elements:
                 str: The new import statement as a string.
                 list: A list of invalid imports.
                 list: A list of spark imports.
                 dict: A dictionary mapping aliases to original module/function names.
        """
        alias_mapping = None
        
        if isinstance(self.node, ast.Import):
            new_import, invalid_imports, spark_imports = self.parse_import()

        elif isinstance(self.node, ast.ImportFrom):
            new_import, invalid_imports, spark_imports, alias_mapping = self.parse_from_import()
            
        else:
            return None, None, None, None # Indicate that there are no valid imports.
            
        return new_import, invalid_imports, spark_imports, alias_mapping

    def parse_from_import(self):
        """
        DESCRIPTION:
            Parses an AST node representing a regular 'from... import' statement.
            This method handles PySpark imports, validating PySpark imports.
            It constructs a new import statement for valid imports and collects
            information about invalid imports.

        PARAMETERS:
            node:
                Required Argument.
                An AST node representing an 'importFrom' statement.
                Types: ast.Import

        RETURNS:
            tuple: A tuple containing two elements:
                - str: A string representing the new import statement for valid imports.
                Empty string if no valid imports are found.
                - list: A list of dictionaries containing information about invalid imports.
                Each dictionary includes 'statement', 'obj.
                - list: A list of spark imports.
        """
   
        valid_imports = []
        invalid_imports = []
        spark_imports = []

        # Check if the module starts with 'pyspark'.
        if self.node.module and self.node.module.startswith('pyspark'):
            if self.node.names[0].name == "*":
                # Handle * imports
                current_dict = spark_objects_ 
                module_parts = self.node.module.split('.')
                for part in module_parts:
                    current_dict = current_dict.get(part, {})
                
                # Add all keys from the current_dict to spark imports.
                for key in current_dict.keys():
                    spark_imports.append(key)
                
                # Create a new import statement for * import
                new_import = f"from {self.node.module} import *"
                return new_import, [], spark_imports, {}
            else:
                # Dictionary to store alias mappings {alias_name: original_name}
                alias_mapping = {}
                
                for imported_lib in self.node.names:
                    # Construct the import statement, handling aliases if present.
                    imported_stmt_ = imported_lib.name if (imported_lib.asname is None) else f"{imported_lib.name} as {imported_lib.asname}"
                    
                    # Track alias mapping if an alias is used
                    if imported_lib.asname is not None:
                        alias_mapping[imported_lib.asname] = imported_lib.name
                    
                    # Create a dictionary with import information 
                    import_info = {
                        'statement': imported_stmt_,
                        'obj': imported_lib.name
                    }
                    # Add directly to spark_imports since it is a pyspark import.
                    spark_imports.append(imported_lib.name)
                    # Check if the import is invalid (in invalid_imports).
                    if imported_lib.name in self.invalid_imports:
                        invalid_imports.append(import_info)
                    else:
                        valid_imports.append(import_info)
        
                # Construct the new import statement if there are valid imports.
                if valid_imports:
                    new_import = f"from {self.node.module} import {', '.join([imp['statement'] for imp in valid_imports])}"
                    return new_import, invalid_imports, spark_imports, alias_mapping
                else:
                    return "", invalid_imports, spark_imports, alias_mapping
        else:
            return None, None, None, None
        
    def parse_import(self):
        """
        DESCRIPTION:
            Parses an AST node representing a regular 'import' statement.
            This method handles both PySpark and non-PySpark imports, validating
            PySpark imports and considering all non-PySpark imports as valid.
            It constructs a new import statement for valid imports and collects
            information about invalid imports.

        PARAMETERS:
            node:
                Required Argument.
                An AST node representing an 'import' statement.
                Types: ast.Import

        RETURNS:
            tuple: A tuple containing two elements:
                - str: A string representing the new import statement for valid imports.
                Empty string if no valid imports are found.
                - list: A list of dictionaries containing information about invalid imports.
                Each dictionary includes 'statement', 'obj'.
                - list: A list of spark imports.
        """
        valid_imports = []
        invalid_imports = []
        spark_imports = []
        is_valid = True
        leaf_part = None

        for name in self.node.names:
            # Split the import name into parts.
            parts = name.name.split('.')
            
            # Check if the import starts with 'pyspark'.
            if parts[0] == 'pyspark':
                leaf_part = parts[-1]
                is_valid =  leaf_part not in self.invalid_imports
                spark_imports.append(leaf_part)
            else:
                is_valid = True

            # Construct the import statement, handling aliases if present.
            imported_stmt_ = name.name if name.asname is None else f"{name.name} as {name.asname}"
            
            # Create a dictionary with import information including line numbers.
            import_info = {
                'statement': imported_stmt_,
                'obj' : leaf_part
            }

            if is_valid:
                valid_imports.append(import_info)
            else:
                invalid_imports.append(import_info)

        # If there are valid imports, construct the new import statement.
        if valid_imports:
            new_import = f"import {', '.join([imp['statement'] for imp in valid_imports])}"
            if new_import == ast.unparse(self.node):
                # If same as original import then don't need to consider the new one.
                return None, None, None
            return new_import, invalid_imports, spark_imports
        else:
            if spark_imports and invalid_imports:
                return  "", invalid_imports, spark_imports
            return None, None, None

class Script:
    def __init__(self, path):
        """
        DESCRIPTION:
            Specifies the file path for the script to be processed.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the absolute or relative path for the script file.
                Type: str
        """
        self._path = path
        self.python_statements = []
        self.__code = None
        self.content = None
        self._udf_ids = set()
        self._spark_variables = {"spark"}
        self._spark_imports = set()
        self._import_aliases = {}  # Maps alias names to original function names
        self._python_functions = {}
        self.cell_no = None
        self._script_notes = []
        self.is_dir = False
        self.pyspark_to_tdmlspk= {            
            "pyspark": "teradatamlspk",
            "SparkSession": "TeradataSession",
            "SparkContext": "TeradataContext",
            'SparkConf': "TeradataConf",
            '.sparkContext': ".teradataContext",
            "sparkUser": "teradataUser",
            "dbutils.widgets.text": "tdnb.text",
            "dbutils.widgets.dropdown": "tdnb.drop_down",
            "dbutils.widgets.getAll": "tdnb.get_all",
            "dbutils.widgets.removeAll": "tdnb.remove_all",
            "dbutils.widgets.getArgument": "tdnb.get_argument",
            "dbutils.widgets.multiselect": "tdnb.multi_select",
            "dbutils.widgets.remove": "tdnb.remove",
            "dbutils.widgets.get": "tdnb.get",
            "dbutils.notebook.run": "tdnb.run_notebook",
            "dbutils.notebook.exit": "tdnb.exit",
            'getOrCreate()': "getOrCreate(host=getpass.getpass('Enter host: '), user=getpass.getpass('Enter user: '), password=getpass.getpass('Enter password: '))"
        }

        with open(self._path, encoding='utf-8') as fp:
            self.content = fp.readlines()

            # If empty file, raise an error.
            if not self.content or all(line.strip() == "" for line in self.content):
                raise ValueError("The script '{}' is empty. Provide a valid script.".format(self._path))
            self.content.insert(0, "")

            # readlines already makes pointer to go end.
            fp.seek(0) 
            self.__code = PyCode(fp.read())

    def _get_name(self, arg):
        """Get the name of argument"""
        if isinstance(arg, ast.Name):
            return arg.id
        elif isinstance(arg, ast.Attribute):
            return arg.attr

    def _process_function_definition(self, func_def, cell_count=None, cell_no=None, interactive_mode=False):
        """
        DESCRIPTION:
            Processes a function definition, analyzing its body for PySpark related statements
            and updating the script's content with any necessary modifications.

        PARAMETERS:
            func_def:
                Required Argument.
                The AST node representing the function definition to process.
                Type: ast.FunctionDef

            cell_count:
                Required Argument.
                The cell number in order. Required to fetch cell content.
                Type: int

            cell_no:
                Required Argument.
                The cell number displayed in the notebook. Required for user guide.
                Type: int, str

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool
            
        RETURNS:
            None
        """
        function_notes = set()
        # Create a new PyCode instance with the function definition.
        py_code = PyCode(func_def, parse_function_body=True)

        # Process each statement in the function body.
        for stmt in py_code.get_statements():
            # Handle content based on whether it's a notebook or script.
            if cell_count is not None: 
                self.content = self.notebook['cells'][cell_count - 1]['source'].splitlines()
                self.content.insert(0, "")
            statement = PythonStatement(stmt, cell_no)

            imports, variables, _, aliases = statement.process(self._spark_imports, self._spark_variables, import_aliases=self._import_aliases, 
                                                                file_path=self._path, interactive_mode=interactive_mode)
            # Update the sets of PySpark variables and imports.
            self._spark_variables = self._spark_variables.union(variables)
            self._spark_imports = self._spark_imports.union(imports)
            self._import_aliases.update(aliases)

            # Collect any user guide notes for this statement.
            user_guide = statement.get_user_guide()
            if user_guide:
                function_notes = function_notes.union(set(user_guide))

            # If the statement was modified, update the content.
            if statement.modified_statement is not None:
                start_line = statement.ast_obj.lineno
                end_line = statement.ast_obj.end_lineno

                # Get the indentation of the original line
                original_indent = self._get_indentation(self.content[start_line])

                # Apply the original indentation to the modified statement.
                indented_modified_statement = original_indent + statement.modified_statement.lstrip()

                # Replace the line(s) in self.content.
                self.content[start_line] = indented_modified_statement if cell_count is not None \
                    else indented_modified_statement + '\n'

                for line in range(start_line + 1, end_line + 1):
                    self.content[line] = '\n'

            # Set the modified content back to the appropriate structure
            if cell_count is not None:
                self.content.pop(0)
                self.notebook['cells'][cell_count - 1]['source'] = '\n'.join(self.content)
            
            # Recursively process nested function calls
            self._process_call_objects(statement, cell_count)

        # Add all collected notes to the notes list.
        self._script_notes = list(set(self._script_notes).union(function_notes))

    def _get_indentation(self, line):
        """Get indentation for the given line."""
        return line[:len(line) - len(line.lstrip())]

    def process(self, dir_path=None, csv_report=False, interactive_mode=False):
        """
        DESCRIPTION:
            Processes each and every statement in the script.

        PARAMETERS:
            dir_path:
                Optional Argument.
                Contains the directory path if the script is part of a directory.
                Type: str

            csv_report:
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool

        RETURNS:
            None
        """
        self.is_dir = True if dir_path else False
        # Think like this as running a python script. Below are the steps during the actual run of script:
        #   First process all the statements. This step will ensure script has no syntax errors.
        #   Then load all the functions. Once functions are loaded, then process the statements one by one.
        #   While looking at statements, identify function calls. When such function call is identified,
        #   then process the corresponding function.
        try:
            for py_statement in self.__code.get_statements():
                if isinstance(py_statement, ast.FunctionDef):
                    # Find function have decorator or not,
                    # If yes then check decorator id is 'pandas_udf'
                    # If yes then add to 'self._udf_ids'
                    for decorators in py_statement.decorator_list:
                        if isinstance(decorators, ast.Call) and \
                                isinstance(decorators.func, ast.Name) and \
                                decorators.func.id == 'pandas_udf':
                            self._udf_ids.add(py_statement.name)
                    self._python_functions[py_statement.name] = py_statement
                else:
                    self.python_statements.append(PythonStatement(py_statement))
        except SyntaxError:
            # throw error if syntax error
            raise SyntaxError("The script '{}' has Syntax error. Unable to parse it.".format(self._path))
    
        # If you are here, script is good and all statements are in hand.
        for statement in self.python_statements:
            imports, variables, udf_ids, aliases = statement.process(self._spark_imports, self._spark_variables, self._udf_ids, 
                                                                      import_aliases=self._import_aliases, file_path=self._path, 
                                                                      interactive_mode=interactive_mode, dir_path=dir_path)
            # Add the returned variable to script variables so subsequent
            # statements consume the variables.
            self._spark_variables = self._spark_variables.union(variables)
            self._spark_imports = self._spark_imports.union(imports)
            self._udf_ids = self._udf_ids.union(udf_ids)
            self._import_aliases.update(aliases)

            # process call objects in the statement.
            self._process_call_objects(statement)

        # After processing all the functions that are called, and 
        # still if self._python_functions is not empty then call for those.
        if self._python_functions:
            remaining_functions = list(self._python_functions.items())
            for func_name, func_def in remaining_functions:
                if func_name in self._python_functions:
                    # Delete these in python functions to avoid reprocessing.
                    del self._python_functions[func_name]

                # Add all the function args in the self.spark_variables.
                for arg in func_def.args.args:
                    if isinstance(arg, ast.arg):
                        arg_name = arg.arg
                        self._spark_variables = self._spark_variables.union(arg_name)

                # Process the function definition.
                self._process_function_definition(func_def, interactive_mode=interactive_mode)

        self.publish_tdmlspk_script()

        # publish user guide.
        self.publish_user_guide(csv_report=csv_report)

    def _process_function_args(self, obj, cell_no=None):
        """
        DESCRIPTION:
            Processes the arguments of a function call, including both positional and keyword arguments.
            It analyzes each argument for PySpark-related content and collects user notes.

        PARAMETERS:
            obj:
                Required Argument.
                The AST node representing the function call.
                Type: ast.Call

            cell_no:
                Optional Argument.
                The cell number in order. Required to fetch cell content.
                Type: int

        RETURNS:
            None
        """
        # Process arguments if the object is a function call
        for arg in obj.args:
            arg_statement = PythonStatement(arg, cell_no)
            arg_imports, arg_variables, _, arg_aliases = arg_statement.process(self._spark_imports, self._spark_variables, self._udf_ids, 
                                                                                 import_aliases=self._import_aliases)

            self._spark_variables = self._spark_variables.union(arg_variables)
            self._spark_imports = self._spark_imports.union(arg_imports)
            self._import_aliases.update(arg_aliases)
            
            # Process the call objects in the argument.
            self._process_call_objects(arg_statement, cell_no)
            user_guide = arg_statement.get_user_guide()

            # Add the user guide to the script notes.
            if user_guide:
                self._script_notes = list(set(self._script_notes).union(user_guide))

        # Process keyword arguments
        for keyword in obj.keywords:
            keyword_statement = PythonStatement(keyword.value, cell_no)
            keyword_imports, keyword_variables, _, keyword_aliases = keyword_statement.process(self._spark_imports, self._spark_variables, 
                                                                                                 self._udf_ids, import_aliases=self._import_aliases)

            self._spark_variables = self._spark_variables.union(keyword_variables)
            self._spark_imports = self._spark_imports.union(keyword_imports)
            self._import_aliases.update(keyword_aliases)
            
            # Process the call objects in the keyword argument.
            self._process_call_objects(keyword_statement, cell_no)
            user_guide = keyword_statement.get_user_guide()

            # Add the user guide to the script notes.
            if user_guide:
                self._script_notes = list(set(self._script_notes).union(user_guide))

    def _process_call_objects(self, statement, cell_count=None):
        """
        DESCRIPTION:
            Processes the callable objects within a statement and also identifies
            function calls if any and processes them.

        PARAMETERS:
            statement:
                Required Argument.
                The statement to process.
                Type: PythonStatement

            cell_count:
                Optional Argument.
                The cell count of the function definition.
                Type: int
                Default: None

        RETURNS:
            None
        """
        if statement._deque:
            for obj in statement._deque:
                # If it is a call then process the arguments.
                if isinstance(obj, ast.Call):
                    self._process_function_args(obj, cell_no=statement.cell_no)

            # Check if the statement contains a single function call.
            if  len(statement._deque) == 1 and isinstance(statement._deque[0], ast.Call):
                func_call = statement._deque[0]
                func_name = self._get_name(func_call.func)

                # Check if the function is in stored functions.
                if func_name in self._python_functions:

                    # Get the function definition, cell_count and cell_no.
                    func_data = self._python_functions[func_name]
                    func_def = func_data[0] if cell_count else func_data
                    cell_count = func_data[1] if cell_count else None
                    cell_no = func_data[2] if cell_count else None
                    # Remove the function from _python_functions to avoid reprocessing.
                    del self._python_functions[func_name]

                    # Process each argument of the function call.
                    for i, arg in enumerate(func_call.args):
                        if i < len(func_def.args.args):
                            corresponding_arg = func_def.args.args[i]
                            corresponding_arg_name = corresponding_arg.arg

                            # Check if the argument is passed from Spark variables.
                            if self._is_spark_related(arg):
                                self._spark_variables.add(corresponding_arg_name)

                            # Check if the argument type annotation is spark related.
                            if hasattr(corresponding_arg, 'annotation'):
                                annotation = self._get_name(corresponding_arg.annotation)
                                if annotation in self._spark_imports or annotation in self._spark_variables:
                                    self._spark_variables.add(corresponding_arg_name)

                    # Process the function definition.
                    self._process_function_definition(func_def, cell_count, cell_no)

    def _is_spark_related(self, node):
        """
        Recursively check if a node or its attributes are Spark-related.
        """
        if isinstance(node, ast.Name):
            return node.id in self._spark_imports or node.id in self._spark_variables
        elif isinstance(node, ast.Attribute):
            return self._is_spark_related(node.value) or node.attr in self._spark_imports or node.attr in self._spark_variables
        elif isinstance(node, ast.Call):
            return self._is_spark_related(node.func) or any(self._is_spark_related(arg) for arg in node.args)
        return False          

    def is_multiple_statements_involved(self, start_line, end_line):
        """Check if there are multiple statements involved between start_line and end_line."""
        # Extract the relevant lines from content.
        relevant_lines = self.content[start_line:end_line + 1]
    
        # Join the lines into a single string for parsing.
        combined_statement = '\n'.join((line.strip() for line in relevant_lines))
        try:
            parsed_ast = ast.parse(combined_statement)
        except IndentationError:
            return True
        # If length is more than 1 multiple statements are involved.
        return len(parsed_ast.body) > 1

    def publish_tdmlspk_script(self):
        """
        DESCRIPTION:
            Look at processed statements and replaces 'self.content' with the modified script.
        """
        for statement in self.python_statements:
            # Only update the self.content for those which are modified.
            if statement.modified_statement is not None:
                start_line = statement.ast_obj.lineno
                end_line = statement.ast_obj.end_lineno

                if isinstance(statement.ast_obj, (ast.Import, ast.ImportFrom)):

                    if(start_line ==  end_line):
                        if not self.is_multiple_statements_involved(start_line, end_line):
                            self.content[start_line] = statement.modified_statement + '\n'
                        
                    else:
                        # only update the start_line with the statement.modified_statement and put the next line empty.
                        self.content[start_line] = statement.modified_statement + '\n'

                        for line in range(start_line+1, end_line+1):
                            self.content[line] = '\n'
                else: 
                    # If multiple statements are involved in same line don't replace it.
                    if not self.is_multiple_statements_involved(start_line, end_line):
                        # If the statement is related to passing multiple columns to ML function 
                        # then update the arguemnt with placeholders in the orginal statement.
                        if "<Specify list of column names>" in statement.modified_statement:
                            self._replace_ml_str_arguments(start_line, end_line, statement.modified_statement)
                        else:
                            self._update_line_with_insertion(start_line, end_line, statement)

        # Adding getpass for the 1st import statememt.
        for idx, line in enumerate(self.content):
            if line.startswith("import ") or line.startswith("from "):
                self.content[idx] = f"import getpass; {line}"  
                break
        
        # Updating pyspark to tdmlspk.
        for idx, line in enumerate(self.content):
            for pyspark_script, tdmlspk_script in self.pyspark_to_tdmlspk.items():
                self.content[idx] = self.content[idx].replace(pyspark_script, tdmlspk_script)
        
        new_file_path = new_file_path = self.generate_output_file_path_for_file(is_script=True)
        with open(new_file_path, 'w', encoding='utf-8') as fp:
            fp.writelines(self.content)

        # Print the message if it is not a directory(when single script is processed).
        if not self.is_dir:
            print("Python script '{}' converted to '{}' successfully.".format(self._path, new_file_path))

    def _replace_ml_str_arguments(self, start_line, end_line, modified_statement):
        """ 
        DESCRIPTION:
            Updates ML function argument placeholders in the original script lines.
            Specifically, this function replaces arguments for ML-related functions
            such as setFeaturesCol, setInputCol, setInputCols, and their keyword arguments
            (inputCol, inputCols, featuresCol) with the placeholder string
            "<Specify list of column names>" in the original code line.

        PARAMETERS:
            start_line:
                Required Argument.
                The starting line number of the statement to be updated.
                Type: int

            end_line:
                Required Argument.
                The ending line number of the statement to be updated.
                Type: int

            modified_statement:
                Required Argument.
                The modified statement containing the placeholder.
                Type: str

        RETURNS:
            None

        EXAMPLES:
            # Example 1: Function-style replacement
            # Original line: model.setInputCols("col1")
            >>> script = Script("example.py")
            >>> script._replace_ml_str_arguments(10, 10, "model.setInputCols("<Specify list of column names>")")
            (Updates the original script lines with the placeholder)
            # model.setInputCols("<Specify list of column names>")

            # Example 2: Keyword-style replacement
            # Original line: StandardScaler(inputCol="features")
            >>> script = Script("example.py")
            >>> script._replace_ml_str_arguments(20, 20, "StandardScaler(inputCol="<Specify list of column names>")")
            (Updates the original script lines with the placeholder)
            # StandardScaler(inputCol="<Specify list of column names>")

        """
        placeholder = "<Specify list of column names>"
        replacements = [
            # For function calls like .setInputCol("<placeholder>").
            ("func", ["setFeaturesCol", "setInputCol", "setInputCols"], True),
            # For keyword args like inputCol="<placeholder>".
            ("key", ["inputCol", "inputCols", "featuresCol"], False),
        ]

        for rep_type, names, is_func in replacements:
            for name in names:
                if is_func:
                    # For function calls.
                    pattern_in_modified = rf'\.{name}\s*\(\s*["\']{re.escape(placeholder)}["\']\s*\)'
                    pattern_in_original = rf'\.{name}\s*\(\s*[^)]*\)'
                else:
                    # For keyword args.
                    pattern_in_modified = rf'{name}\s*=\s*["\']{re.escape(placeholder)}["\']'
                    pattern_in_original = rf'{name}\s*=\s*[^,\)\n]+'

                modified_match = re.search(pattern_in_modified, modified_statement)
                if modified_match:
                    for i in range(start_line, end_line + 1):
                        original_line = self.content[i]
                        updated_line = re.sub(pattern_in_original, modified_match.group(0), original_line)
                        if updated_line != original_line:
                            self.content[i] = updated_line
                            break

    def _update_line_with_insertion(self, start_line, end_line, statement):
        """
        DESCRIPTION:
            This helper method iterates the original statement between start_line and end_line, 
            passing each line to `_insert_options_from_modified_statement` to check 
            if any insertions (e.g., `.options(...)`) are needed. 
            It updates only the first line that results in a change.
            
        PARAMETERS:
            start_line:
                Required Argument.
                The starting line number of the statement to be updated.
                Type: int
                
            end_line:
                Required Argument.
                The ending line number of the statement to be updated.
                Type: int
                
            statement:
                Required Argument.
                The statement object containing the modified statement.
                Type: str
                
        RETURNS:
            None
        """
        for line_num in range(start_line, end_line + 1):
            original_line = self.content[line_num]
            updated_line = self._insert_options_from_modified_statement(original_line, statement.modified_statement)

            # Only update if the line was modified
            if original_line != updated_line:
                self.content[line_num] = updated_line
                break

    def _insert_options_from_modified_statement(self, original_line, modified_statement):
        """
        DESCRIPTION:
            Inserts `.options(...)` or other relevant options (such as authorization or primary_index)
            into the original PySpark read/write statement, based on the options found in the
            modified statement. This function uses regular expressions to identify where to insert
            the options, handling both single-line and multi-line chained calls.
            
        PARAMETERS:
            original_line:
                Required Argument.
                The original line of code to be modified.
                Type: str
                
            modified_statement:
                Required Argument.
                The modified statement containing options to be inserted.
                Type: str
                
        RETURNS:
            The modified line of code with options inserted at the correct location.
            Type: str

        EXAMPLES:
            # Example 1: Inserting options into a single-line read statement.
            original_line = "df.read.format('csv').load('path/to/file')"
            modified_statement = "df.read.format('csv').options(authorization={...})"
            >>> _insert_options_from_modified_statement(original_line, modified_statement)
            # Output: "df.read.format('csv').options(authorization={...}).load('path/to/file')"

            # Example 2: Inserting options into a multi-line read statement.
            original_line = 'df.write.\'
            modified_statement = 'df.write.options(authorization = {"Access_ID": "...", "Access_Key": "..." }).\\n    format("csv").save("file.csv")'
            >>> _insert_options_from_modified_statement(original_line, modified_statement)
            # Output: 'df.write.options(authorization = {"Access_ID": "...", "Access_Key": "..." }).\'
            
        """

        insert_parts = []
        # Check for .options(authorization=...).
        auth_match = re.search(r'options\s*\(\s*authorization\s*=\s*\{[^}]+\}\s*\)', modified_statement)
        if auth_match:
            insert_parts.append(auth_match.group(0))

        # Only include primary_index option if writeTo and partitionedBy are present.
        if "writeTo" in modified_statement and "partitionedBy" in modified_statement:
            pi_match = re.search(r'options\s*\(\s*primary_index\s*=\s*"[^"]+"\s*\)', modified_statement)
            if pi_match:
                insert_parts.append(pi_match.group(0))

        # If nothing to insert, return original line unchanged.
        if not insert_parts:
            return original_line

        insert_text = '.'.join(insert_parts)

        # Case 1: spark.read/write.format(...).
        pattern_format = r'\b(read|write)\s*\.(?=\s*(format|json|csv|parquet)\s*\()'
        if re.search(pattern_format, original_line):
            return re.sub(pattern_format, r'\1.' + insert_text + '.', original_line)

        # Case 2: df.read/write.\ or df.read/write\
        pattern_with_or_without_dot = r'^(.*?\b(read|write))(\.?)(\\\s*)$'
        match = re.match(pattern_with_or_without_dot, original_line)
        if match:
            before = match.group(1)      # e.g. df.read
            dot = match.group(3)         # '.' or ''
            backslash = match.group(4)   # the backslash + trailing spaces

            if dot == '.':
                # If line ends with .\
                return before + '.' + insert_text + '.' + backslash
            else:
                # If line ends with \ (no dot)
                return before + '.' + insert_text + backslash

        # Case 3: writeTo.partitionedBy(...).
        pattern_writeTo = r'writeTo\s*\.(?=\s*partitionedBy\s*\()'
        if re.search(pattern_writeTo, original_line) and pi_match:
            return re.sub(pattern_writeTo, 'writeTo.' + pi_match.group(0) + '.', original_line)

        # No pattern matched return unchanged.
        return original_line

    def generate_output_file_path_for_file(self, is_script=True):
        """
        Generates the output file path for the processed script/ notebook.

        PARAMETERS:
            is_script:
                Optional Argument.
                Determines if the output file is a script or a notebook.
                Type: bool
                Default: True

        RETURNS:
            The full path of the output file.
            Type: str
        """
        dir_name = os.path.dirname(self._path)
        base_name = os.path.basename(self._path)

        # Remove the .py extension if it exists.
        file_name = os.path.splitext(base_name)[0]

        # Create a new file name with _tdmlspk suffix.
        new_file_name = f"{file_name}_tdmlspk.py" if is_script else f"{file_name}_tdmlspk.ipynb"
        return os.path.join(dir_name, new_file_name)
    
    def _get_tdmlspk_html_name(self, file_name, ext, dir_name):
        """
        DESCRIPTION:
            Helper function to generate the HTML file name.
            Note:
                * If the file is a Jupyter notebook and a corresponding Python file exists,
                  '_nb_tdmlspk' suffix is added to the file name. If not, only '_tdmlspk' 
                  suffix is added.

        PARAMETERS:
            file_name:
                Required Argument.
                The base name of the file without extension.
            
            ext:
                Required Argument.
                The file extension of the original file.

            dir_name:
                Required Argument.
                The directory name where the file is located.
        
        RETURNS:
            The generated HTML file name based on the file type.
            Type: str
        """
        py_file_path = os.path.join(dir_name, f"{file_name}.py")
        if ext == ".ipynb" and os.path.exists(py_file_path):
            return f"{file_name}_nb_tdmlspk.html"
        else:
            return f"{file_name}_tdmlspk.html"

    def generate_output_file_path_for_user_guide(self):
        """
        Generates the output file path for the processed script.

        RETURNS:
            The full path of the output file.
            Type: str
        """
        dir_name = os.path.dirname(self._path)
        base_name = os.path.basename(self._path)
        file_name, ext = os.path.splitext(base_name)
        py_file_path = os.path.join(dir_name, f"{file_name}.py")

        new_file_name = self._get_tdmlspk_html_name(file_name, ext, dir_name)
        return os.path.join(dir_name, new_file_name)

    def publish_user_guide(self, csv_report=False):
        """
        DESCRIPTION:
            Loop through all the statements. Collect the individual user guide for every
            statement. Sort it according to line number. Then use the template for script
            and publish the HTML report.

        PARAMETERS:
            csv_report:
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

        Note: Incase if python script has syntax errors, then it won't have any
              individual statements. In such cases also, this function should publish the report
              stating the file has syntax errors.
        """
        html_data =  ScriptNotes(self.get_user_notes(), self._path).to_html(csv_report=csv_report)

        new_file_path = self.generate_output_file_path_for_user_guide()
        with open(new_file_path, 'w', encoding='utf-8') as fp:
            fp.writelines(html_data)

        # Print the message if it is not a directory(when single script is processed).
        if not self.is_dir:
            print("Script conversion report '{}' published successfully. ".format(new_file_path))

    def get_user_notes(self):
        """
        DESCRIPTION:
            Retrieves and combines the list of user notes from the script and individual statements.

        PARAMETERS:
            None

        RETURNS:
            list:
                A combined list of user notes from the script and all processed statements.
                Elements are a combination of:
                    - Script-level notes (self._script_notes).
                    - User guides from each processed statement.
                Type: List[UserNote]
        """
        return self._script_notes + [statement.get_user_guide() for statement in self.python_statements]


class Notebook(Script):
    def __init__(self, path):
        super().__init__(path)
        self.python_statements = {}
        with open(self._path, encoding='utf-8') as fp:
            self.notebook = nbformat.read(fp, nbformat.NO_CONVERT)

        if len(self.notebook.cells) == 1 and self.notebook.cells[0].source.strip() == "":
            raise ValueError("The notebook '{}' is empty. Provide a valid notebook.".format(self._path))

    def _process_magic_and_shell_commands(self, comment=True):
        """
        DESCRIPTION:
            Comments out or removes the `# ` prefix from lines that start with '!' or '%'
            in each code cell based on the value of the `comment` flag.
            When %sql is found, it comments the %sql and wraps the query around spark.sql(query).
            Note:
                * %sql will not be uncommented.
            
        PARAMETERS:
            comment:
                Optional Argument.
                Determines whether to comment out or uncomment lines.
                Type: bool
                Default: True
        """
        for cell in self.notebook['cells']:
            if cell['cell_type'] == 'code':
                is_modified = False
                # Split the cell source into lines
                lines = cell['source'].splitlines()
                # Check if cell has sql query started with %sql
                sql_idx = None
                for i, line in enumerate(lines):
                    if line.strip().startswith('%sql'):
                        sql_idx=i
                        break
                # If cell contains %sql
                # 1. Comment the %sql
                # 2. Wrap the query around spark.sql(query)
                # 3. Replace $var or ${var} with tdnb.get('var') in query
                if sql_idx is not None:
                    lines[sql_idx] = '# ' + lines[sql_idx]
                    lines[sql_idx+1] = "{}{}".format("spark.sql(f\"\"\"", lines[sql_idx+1])
                    lines[-1] = "{}{}".format(lines[-1], "\"\"\")")
                    for i, line in enumerate(lines):
                        for value in re.findall(r"(?<!\\)\$([a-zA-Z_]\w+)", line):
                            line=line.replace('$'+value, f"{{tdnb.get('{value}')}}")
                        for value in re.findall(r"(?<!\\)\$\{(\w+)\}", line):
                            line=line.replace(f'${{{value}}}', f"{{tdnb.get('{value}')}}")
                        lines[i]=line
                    is_modified = True
                else:
                    for i in range(len(lines)):
                        # Determine action based on the comment flag
                        if comment:
                            # Check if the line starts with '# !' or '# %'
                            if lines[i].strip().startswith(('!', '%')):
                                # Add a '#' at the beginning of the line.
                                lines[i] = '# ' + lines[i]
                                is_modified = True
                        else:
                            # Check if the line starts with '# !' or '# %'
                            if lines[i].strip().startswith(('# !', '# %')) and not lines[i].strip().startswith('# %sql'):
                                # Remove the leading `# ` and update the line directly
                                lines[i] = lines[i][2:]
                                is_modified = True

                # Update the cell source only if modifications were made
                if is_modified:
                    cell['source'] = "\n".join(lines)

    def process(self, dir_path=None, csv_report=False, interactive_mode=False):
        empty_cell = 0
        cell_count = 1
        self.is_dir = True if dir_path else False
        # Process all the statements in the cells of a notebook. To ensure each cell does not have syntax errors.
        # Store the statements in a dictionary with cell count(in order) as key and list of statements as value.
        # Then load all the functions. Once functions are loaded, then process the statements one by one.
        # While looking at statements, identify function calls. When such function call is identified,
        # then process the corresponding function.
        
        # Comment out all lines in code cells that start with '!' or '%'.
        self._process_magic_and_shell_commands()

        # cell_count is the cell number in order.
        for cell in self.notebook['cells']:
            cell_no = cell['execution_count'] if cell['cell_type'] == 'code' else 0
            if cell_no is None:
                # If execution count is None add 'Empty Cell <No of empyty cell>' i.e. 'Empty Cell 1'
                # to track cell with no execution count in the HTML report.
                empty_cell = empty_cell+1
                cell_no = 'Empty Cell {}'.format(empty_cell)
            # Process the source code.
            self.__code = PyCode(cell['source'])

            try:
                self.python_statements[cell_count] = []
                # When %sql appears in the cell then don't process the cell.
                if cell['cell_type'] == 'code' and '# %sql' not in cell['source']:
                    for py_statement in self.__code.get_statements():
                        if isinstance(py_statement, ast.FunctionDef):
                            # Check if the function has a decorator 'pandas_udf'
                            # If yes then add to 'self._udf_ids'
                            for decorators in py_statement.decorator_list:
                                if isinstance(decorators, ast.Call) and \
                                    isinstance(decorators.func, ast.Name) and decorators.func.id == 'pandas_udf':
                                    self._udf_ids.add(py_statement.name)
                            self._python_functions[py_statement.name] = (py_statement, cell_count, cell_no)
                        else:
                            # Create a PythonStatement object for each statement
                            python_statement = PythonStatement(py_statement, cell_no)
                            # Append the PythonStatement object to the list of statements for the cell
                            self.python_statements[cell_count].append(python_statement)
                cell_count = cell_count + 1

            except SyntaxError:
                raise SyntaxError("The notebook '{}' has Syntax error. Unable to parse it.".format(self._path))

        for cell_count, cell_statements in self.python_statements.items():
            for statement in cell_statements:
                imports, variables, udf_ids, aliases = statement.process(self._spark_imports, self._spark_variables, self._udf_ids, \
                                                          import_aliases=self._import_aliases, file_path=self._path, 
                                                          interactive_mode=interactive_mode, dir_path=dir_path)

                # Add the returned variable to notebook variables so subsequent
                # statements consume the variables.
                self._spark_variables = self._spark_variables.union(variables)
                self._spark_imports = self._spark_imports.union(imports)
                self._udf_ids = self._udf_ids.union(udf_ids)
                self._import_aliases.update(aliases)
                
                # Process call objects in the statement.
                self._process_call_objects(statement, cell_count)

        # After processing all the functions that are called, and 
        # still if self._python_functions is not empty then call for those.
        if self._python_functions:
            remaining_functions = list(self._python_functions.items())
            for func_name, func_data in remaining_functions:

                # Get the function definition, cell_count and cell_no.
                func_def = func_data[0]
                cell_count = func_data[1]
                cell_no = func_data[2]
                if func_name in self._python_functions:
                    # Delete these in python functions to avoid reprocessing.
                    del self._python_functions[func_name]

                # Add all the function args in the self.spark_variables.
                for arg in func_data[0].args.args:
                    if isinstance(arg, ast.arg):
                        arg_name = arg.arg
                        self._spark_variables.add(arg_name)

                # Process the function definition.
                self._process_function_definition(func_def, cell_count, cell_no, interactive_mode=interactive_mode)

        self.publish_tdmlspk_notebook()

        # publish user guide.
        self.publish_user_guide(csv_report=csv_report)

    def publish_tdmlspk_notebook(self):
        """
        DESCRIPTION:
            Look at processed statements and replaces 'self.content' with the modified script.
        """
        getpass_added = False
        for cell_data, (cell_count, cell_statements) in zip(self.notebook['cells'], self.python_statements.items()):
            if cell_data['cell_type'] == 'code':
                # Remove output cell
                cell_data['outputs'] = []
                # Split the cell code string into list based on line breaks
                self.content = cell_data['source'].splitlines() 
                self.content.insert(0, "") 
                for statement in cell_statements:
                    # Only update the self.content for those which are modified.
                    if statement.modified_statement is not None:
                        start_line = statement.ast_obj.lineno
                        end_line = statement.ast_obj.end_lineno

                        if isinstance(statement.ast_obj, (ast.Import, ast.ImportFrom)):
                            if(start_line ==  end_line):
                                if not self.is_multiple_statements_involved(start_line, end_line):
                                    self.content[start_line] = statement.modified_statement
                            else:
                                # only update the start_line with the statement.modified_statement and put the next line empty.
                                self.content[start_line] = statement.modified_statement
                                for line in range(start_line+1, end_line+1):
                                    self.content[line] = '\n'
                                
                        else:
                            # If multiple statements are involved in same line don't replace it.
                            if not self.is_multiple_statements_involved(start_line, end_line):
                                if "<Specify list of column names>" in statement.modified_statement:
                                    self._replace_ml_str_arguments(start_line, end_line, statement.modified_statement)
                                else:
                                    self._update_line_with_insertion(start_line, end_line, statement)

                self.content.pop(0)

                for idx, line in enumerate(self.content):
                    # Adding getpass for the 1st import statememt.
                    if not getpass_added:
                        if line.startswith("import ") or line.startswith("from "):
                            getpass_added = True
                            self.content[idx] = f"import getpass; {line}"
                    for pyspark_script, tdmlspk_script in self.pyspark_to_tdmlspk.items():
                        self.content[idx] = self.content[idx].replace(pyspark_script, tdmlspk_script)

                cell_data['source'] = '\n'.join(self.content)

        # Comment out all lines in code cells that start with '!' or '%'.
        self._process_magic_and_shell_commands(comment=False)
        
        new_file_path = new_file_path = self.generate_output_file_path_for_file(is_script=False)
        with open(new_file_path, 'w', encoding='utf-8') as fp:
                nbformat.write(self.notebook, fp, version=nbformat.NO_CONVERT)

        # Print the message if it is not a directory(when single script is processed).
        if not self.is_dir:
            print("Python Notebook '{}' converted to '{}' successfully.".format(self._path, new_file_path))

    def publish_user_guide(self, csv_report=False):
        """
        DESCRIPTION:
            Loop through all the statements. Collect the individual user guide for every
            statement. Sort it according to line number. Then use the template for script
            and publish the HTML report.

        PARAMETERS:
            csv_report:
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

        Note: Incase if Notebook script has syntax errors, then it won't have any
              individual statements. In such cases also, this function should publish the report
              stating the file has syntax errors.
        """
        html_data =  NotebookNotes(self.get_user_notes(), self._path).to_html(csv_report=csv_report)

        new_file_path = self.generate_output_file_path_for_user_guide()
        with open(new_file_path, 'w', encoding='utf-8') as fp:
            fp.writelines(html_data)

        # Print the message if it is not a directory(when single script is processed).
        if not self.is_dir:
            print("Notebook conversion report '{}' published successfully. ".format(new_file_path))

    def get_user_notes(self):
        """
        DESCRIPTION:
            Retrieves and combines the list of user notes from the notebook and individual statements.
        PARAMETERS:
            None
        RETURNS:
            list:
                A combined list of user notes from the notebook and all processed statements.
                Elements are a combination of:
                    - Script-level notes (self._script_notes).
                    - User guides from each processed statement.
                Type: List[NotebookUserNote]
        """

        for cell, cell_statements in self.python_statements.items():
            for statement in cell_statements:
                self._script_notes.append(statement.get_user_guide())
        return self._script_notes

class Directory(Script):
    def __init__(self, path):
        self._path = path
        self._user_notes = []
        self._errored_files = {}
        self.script_objects = []

    def __get_files(self):
        """
        DESCRIPTION:
            Internal function that recursively traverses the directory structure
            starting from self._path and yields the absolute path for each Python
            file (.py) encountered.

        PARAMETERS:
            None

        RETURNS:
                Yields absolute paths of Python files.
                Type: str
        """
        # Absolute path of each Python file found in the directory and its subdirectories.
        for root, dirs, files in os.walk(self._path):
            for file in files:
                if (file.endswith('.py') or file.endswith('.ipynb')) and "_tdmlspk." not in file:
                    yield os.path.join(root, file)

    def process(self, csv_report=False, interactive_mode=False):
        """
        DESCRIPTION:
            Processes each file in the directory based on its extension (.py or .ipynb)
            and stores the processed objects in the script_objects list.If a file has 
            syntax errors, it is stored in the errored_files dictionary.
            
        PARAMETERS:
            csv_report:
                Optional Argument.
                If True, the function will also generate the CSV files for File summary ad Object summary.
                Type: bool
                Default Value: False

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool
            
        RETURNS:
            None
        """
        files = sorted(self.__get_files())
        total_files = len(files)

        # Initialize the progress bar
        progress_bar = _ProgressBar(jobs=total_files, prefix="Processing Files", verbose=1)
        # Process each file based on its extension.
        for file_ in sorted(self.__get_files()):
            try:
                if file_.endswith(".py"):
                    obj = Script(file_)
                elif file_.endswith(".ipynb"):
                    obj = Notebook(file_)
                # Process the object (script or notebook).
                obj.process(dir_path=self._path, interactive_mode=interactive_mode)
                # Collect the objects
                self.script_objects.append(obj)
                # Update the progress bar for processed file.
                progress_bar.update()

            except SyntaxError as err:
                full_traceback = traceback.format_exc()
                self._errored_files[file_] = (full_traceback, "user_error")
                progress_bar.update()  # Update progress even for errored files

            except ValueError as err:
                # Mo error is shown for empty file, just need to log it separately in summary by file table.
                self._errored_files[file_] = ("It is an empty file", "empty_file")
                progress_bar.update()  # Update progress even for errored files

            except Exception as e:
                full_traceback = traceback.format_exc()
                self._errored_files[file_] = (full_traceback, "utility_error")
                progress_bar.update()  # Update progress even for errored files
    
        # Publish the user guide for the directory.
        self.publish_user_guide(csv_report=csv_report)

    def publish_user_guide(self, csv_report=False):
        """
        DESCRIPTION:
            Loop through all the script objects. Collect the individual user guide for every
            statement. Sort it according to line number. Then use the template for script
            and publish the HTML report.
        """ 
        consolidated_rows = []
        object_summary_rows = []
        file_data = {}
        _user_notes = []

        print("\n\nProcessing conversion report for '{}'...".format(self._path))
        # Iterate through each script object.
        for sc in self.script_objects:
            file_name = sc._path
            _user_notes = sc.get_user_notes()

            # Check if the object is a Notebook.
            if isinstance(sc, Notebook):  
                notes = NotebookNotes(_user_notes, file_name)
            else:  # Otherwise, it's a Script
                notes = DirectoryNotes(_user_notes, self._path, file_name)

            # Collect the consolidated summary row.
            consolidated_row = notes._get_consolidated_rows(filename=file_name)
            consolidated_rows.append(consolidated_row)

            # Collect the object summary row.
            object_summary_rows.append(notes._get_object_summary_rows(filename=file_name))

            # If the file has no issues (total is 0 and not in the error list), no attention is required.
            if consolidated_row["total"] == 0 and file_name not in self._errored_files:
                file_data[file_name] = {"attention_required": 0}
            # Otherwise, attention is required.
            else:
                file_data[file_name] = {"attention_required": 1}

        # Add consolidated rows for errored files.
        for errored_file, (_, error_type) in self._errored_files.items():
            consolidated_rows.append({
                "filename": os.path.basename(errored_file),
                "notification": 0,
                "partially_supported": 0,
                "not_supported": 0,
                "total": 0,
                "user_error": 1 if error_type == "user_error" else 0,
                "utility_error": 1 if error_type == "utility_error" else 0,
                "empty_file": 1 if error_type == "empty_file" else 0
            })

        dir_notes = DirectoryNotes(_user_notes, self._path)
        dir_notes._get_tables(object_summary_rows, consolidated_rows, csv_report=csv_report) 
            
        left_files = ""
        for file in sorted(self.__get_files()):
            file_name = os.path.basename(file)
            filedir = os.path.relpath(file, self._path)
            file_base, file_ext = os.path.splitext(filedir)
            # Get the converted file name for HTML.
            filedir_converted = self._get_tdmlspk_html_name(file_base, file_ext, self._path)

            # For files which has no issues, display as per attention required.
            if file_data.get(file):
                if file_data[file]["attention_required"] == 1:
                    filedir_display = FILEDIR_DISPLAY_BASE.format(file)
                else:
                    icon = ICON_TYPE["SUCCESS_FILE"]
                    filedir_display = FILEDIR_DISPLAY_SUCCESS.format(icon, file)
            # For files with issues, display as per error type.
            else:
                # Get error details.
                error_details = self._errored_files.get(file, ("", "", ""))
                error_type = error_details[1]
                
                # Choose the correct icon based on error type.
                if error_type in ["user_error", "utility_error"]:
                    # Error style.
                    icon = ICON_TYPE["BUG_REPORT"]
                    filedir_display = FILEDIR_DISPLAY_ERROR.format(icon, file)
                elif error_type == "empty_file":
                    # Empty styling.
                    icon = ICON_TYPE["EMPTY_FILE"]
                    filedir_display = FILEDIR_DISPLAY_EMPTY.format(icon, file)

                highlighted_code = self._errored_files.get(file, ('', ''))[0]
                
                # Create consolidated row for errored file.
                consolidated_row = [{
                    "filename": os.path.basename(filedir),
                    "notification": 0,
                    "partially_supported": 0,
                    "not_supported": 0,
                    "total": 0,
                    "user_error": 1 if error_type == "user_error" else 0,
                    "utility_error": 1 if error_type == "utility_error" else 0,
                    "empty_file": 1 if error_type == "empty_file" else 0
                }]

                # Call to_html() with error-specific arguments.
                error_html = DirectoryNotes("", file_name, "").to_html(consolidated_rows=consolidated_row,
                                                                       highlighted_code=highlighted_code,
                                                                       error_type=error_type)
                file_path = file.rsplit('.', 1)[0] + "_tdmlspk.html"
                with open(file_path, "w", encoding="utf-8") as fp:
                    fp.write(error_html)

            left_files += LEFT_FILES_TEMPLATE.format(filedir_converted=filedir_converted,
                                                     filedir_display=filedir_display)
        
        # Load the Jinja2 template environment.
        env = Environment(loader=FileSystemLoader(os.path.dirname(dir_notes.dir_template)))

        # Load the template.
        template = env.get_template(os.path.basename(dir_notes.dir_template))

        # Create complete HTML using main template, including Pygments CSS.
        full_html = template.render(dir_files =left_files, 
                                    right_pane=dir_notes.right_pane_html)
    
        file_name = os.path.splitext(os.path.basename(self._path))[0]
        
        # Create a new file name with _tdmlspk suffix.
        new_file_name = f"{file_name}_index.html"
        new_file_path =  os.path.join(self._path, new_file_name)

        with open(new_file_path, 'w', encoding='utf-8') as fp:
            fp.writelines(full_html)

        print("\nScript conversion report '{}' published successfully. ".format(new_file_path))

class PythonStatement:

    tdmlspk_notes = None
    dynamic_notes = None
    ARRAY_FUNCTIONS = {'arrays_overlap', 'array_contains', 'array_join', 'slice', 'array_prepend',
                       'array_append','array_distinct', 'array_intersect', 'array_union', 'array_except', \
                       'array_compact', 'sort_array', 'sequence', 'array_repeat', 'reverse', 'concat', 'shuffle'}

    def __init__(self, ast_obj, cell_no=None):

        self.ast_obj = ast_obj
        self.cell_no = cell_no
        self.start_line = ast_obj.lineno
        self.end_line = ast_obj.end_lineno
        self.is_spark_component_involved = False
        self.modified_statement = None

        # Store instances of User notes. Key should be the name of the pyspark
        # API. Value should be user notes. Example: {'Vectors': <UserNote Object>}
        self._user_notes = {}
        self.__udf_ids = set()
        self.__spark_variables = set()
        self.__spark_imports = set()
        self.__import_aliases = {}  # Maps alias names to original function names
        self._current_targets = set()


        # Tracks which array functions are present in the current statement.
        # This is a per-statement record used for user notes, translation checks,
        # and identifying whether the statement involves array-related operations.
        # Stored as a set because a single statement may contain multiple array functions.
        self._array_functions_in_statement = set()

        # Stores the individual elements in the statement. All the actions on
        # all types of statements except imports, be it generating user notes
        # or translating statement is done on stack.
        self._deque = deque()
        self._ml_function_args_string = '"<Specify list of column names>"'

        # populate notes.
        if PythonStatement.tdmlspk_notes is None:
            PythonStatement.tdmlspk_notes = _get_json(os.path.join(os.path.dirname(__file__), "user_notes.json"))
        if PythonStatement.dynamic_notes is None:
            PythonStatement.dynamic_notes = _get_json(os.path.join(os.path.dirname(__file__), "dynamic_user_notes.json"))

    def _process_setFeaturesCol_inputCols(self, actual_statement):
        # Initialize variables for tracking modifications
        modified_statement = actual_statement

        # Process function calls that set feature or input columns.
        for function in ["setFeaturesCol", "setInputCol", "setInputCols"]:
            # Regex pattern to match function calls with string or list arguments.
            # Regex pattern explanation:
            # \b({function}\s*\()  : Match the function name at a word boundary, followed by optional whitespace and an opening parenthesis
            # (                    : Start capturing group for the argument
            #  [\'"]([^\'"]*)[\'"] : Match a string argument (either single or double quotes)
            #  |                   : OR
            #  \[[^\]]*\]          : Match a list argument (anything inside square brackets)
            # )                    : End capturing group for the argument
            # (\))                 : Match the closing parenthesis
            #
            # Examples:
            #   setFeaturesCol("column_name")
            #   setInputCols(["col1", "col2"])
            pattern = rf'\b({function}\s*\()([\'"]([^\'"]*)[\'"]|\[[^\]]*\])(\))'
            matches = list(re.finditer(pattern, modified_statement))

            # Process matches in reverse order to avoid index issues when replacing.
            # We process in reverse because replacing text can change the indices of subsequent matches.
            for match in reversed(matches):
                # match.group(0): The entire matched string
                # match.group(1): The function name with opening parenthesis
                # match.group(2): The argument (either a string or a list)
                # match.group(3): The content of the string argument (if it's a string)
                # match.group(4): The closing parenthesis
                arg = match.group(2)
                if arg.startswith('"') or arg.startswith("'"):  # Check if arg is a string

                    # Replace the argument with the target string
                    # Example: If we match setFeaturesCol("column_name"),
                    # arg would be "column_name" (including the quotes)
                    replacement = f'{match.group(1)}{self._ml_function_args_string}{match.group(4)}'
                    modified_statement = modified_statement[:match.start()] + replacement + modified_statement[match.end():]
                    self.modified_statement = modified_statement
                    # Add a user note.
                    if self.cell_no:
                        self._user_notes[function] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, function,
                            "Replace following string `Specify list of column names` with list of column names manually",
                            UserNoteType.PARTIALLY_SUPPORTED)
                    else:
                        self._user_notes[function] = UserNote(self.start_line, self.end_line, function,
                            "Replace following string `Specify list of column names` with list of column names manually",
                            UserNoteType.PARTIALLY_SUPPORTED)

        # Process keyword arguments
        for keyword in ["inputCol", "inputCols", "featuresCol"]:
            # Regex pattern to match keyword arguments with string values, variable names, or lists
            # Regex pattern explanation:
            # \b({keyword}\s*=\s*)  : Match the keyword at a word boundary, followed by '=' and optional whitespace
            # (                     : Start capturing group for the entire value
            #   ([\'"]([^\'"]*)[\'"]): Match a string value (quoted content)
            #   |(\w+)              : OR match a variable name (word characters)
            #   |\[.*?\]            : OR match a list (anything between square brackets)
            # ) 
            pattern = rf'\b({keyword}\s*=\s*)(([\'"]([^\'"]*)[\'"])|(\w+)|\[.*?\])'
            
            # Find all matches of the pattern in the modified statement.
            matches = list(re.finditer(pattern, modified_statement))
            # Process matches in reverse order to avoid offsetting issues when replacing.
            for match in reversed(matches):
                full_match = match.group(0)   # The entire matched string
                keyword_part = match.group(1) # The keyword and '=' part
                value_part = match.group(2)   # The value part (string, variable, or list)
                
                # Check if the value is a string or a variable name (not a list).
                if (value_part.startswith('"') or value_part.startswith("'")) or value_part.isidentifier():
                    # Replace the matched part with the keyword and the new string.
                    replacement = f'{keyword_part}{self._ml_function_args_string}'
                    modified_statement = modified_statement[:match.start()] + replacement + modified_statement[match.end():]
                    self.modified_statement = modified_statement

                    # Add a user note.
                    if self.cell_no:
                        self._user_notes[keyword] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, keyword,
                            "Replace following string `Specify list of column names` with list of column names manually",
                            UserNoteType.PARTIALLY_SUPPORTED)
                    else:
                        self._user_notes[keyword] = UserNote(self.start_line, self.end_line, keyword,
                            "Replace following string `Specify list of column names` with list of column names manually",
                            UserNoteType.PARTIALLY_SUPPORTED)

    def process(self, pyspark_imports, pyspark_variables, udf_ids=None, import_aliases=None, file_path=None, interactive_mode=False, dir_path=None):
        """
        DESCRIPTION:
            Processes a single statement, storing individual components if required in this object.

        PARAMETERS:
            pyspark_imports:
                Required Argument.
                Import statements specific to Spark.
                Should be provided by the Script/Notebook.
                Type: List[str]

            pyspark_variables:
                Required Argument.
                Variables which refer to Spark objects.
                Should be provided by the Script/Notebook.
                Type: List[str]

            udf_ids:
                Optional Argument.
                Function names which contains either 'lambda' or 'pandas_udf' functions.
                Type: set()

            import_aliases:
                Optional Argument.
                Dictionary mapping alias names to original function names.
                Type: dict

            file_path:
                Optional Argument.
                Path to the file being processed.
                Type: str

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool

            dir_path:
                Optional Argument.
                Path of directory being processed.
                Type: str

            import_aliases:
                Optional Argument.
                Dictionary mapping alias names to module names for imports.
                Type: dict

        RETURNS:
            tuple:
                Names of Spark variables, Spark imports, lambda functions, and import aliases.
                Type: (set, set, set, dict)
        """
        if import_aliases is None:
            import_aliases = {}
        
        # Store import_aliases in instance variable BEFORE parsing so __parse_statement can use them
        self.__import_aliases.update(import_aliases)
        
        if isinstance(self.ast_obj, (ast.Import, ast.ImportFrom)):
            self.__process_import(self.ast_obj)
        else:
            # Parse the statement. Once statement is parsed, 'self._deque' will have
            # details of statement.
            self.__parse_statement(self.ast_obj)

            # Check if stack is populated. It can be a Name or Call object.
            # If something else, do not parse.
            if self._deque:
                variable_name = self._get_variable_name(self._deque[0])
                # If stack is populated and if variable is a spark variable, then process further.
                if variable_name and (variable_name in pyspark_imports or variable_name in pyspark_variables):
                    # Consider the whole stack as spark statements.
                    self.is_spark_component_involved = True
                    if self._current_targets:
                        self.__spark_variables = self.__spark_variables.union(self._current_targets)

                    # Handle combined attributes like read.csv, read.parquet.
                    self.process_combined_attributes(file_path=file_path, interactive_mode=interactive_mode, dir_path=dir_path)

                    for obj in self._deque:
                        keyword = self._get_variable_name(obj)

                        if keyword in ('udf', 'register'):
                            self._check_udf_register_functions(keyword, udf_ids, obj)
                            continue
                        if keyword in self.ARRAY_FUNCTIONS:
                            continue
                        self._process_keywords_call_args(obj, keyword)

        if self._array_functions_in_statement:
            for node in ast.walk(self.ast_obj):
                if isinstance(node, ast.Call):
                    func_name = self._get_variable_name(node)
                    # Resolve alias to original function name if it exists
                    original_func_name = import_aliases.get(func_name, func_name)
                    if original_func_name in self.ARRAY_FUNCTIONS:
                        if self.has_nested_array(node, pyspark_variables):
                            self._process_user_notes(original_func_name)

        actual_statement = ast.unparse(self.ast_obj)

        if self.is_spark_component_involved:
            # Updation of setFeaturesCol and inputCols.
            self._process_setFeaturesCol_inputCols(actual_statement)

        return self.__spark_imports, self.__spark_variables, self.__udf_ids, self.__import_aliases

    def _check_udf_register_functions(self, keyword, udf_ids, ast_obj):
        """
        DESCRIPTION:
            Function to check if the keyword 'register' contains 'pandas_udf' function or 
            'udf' or 'register' contains 'ArrayType' as return type.
            If yes, then process user notes.

        PARAMETERS:
            keyword:
                Required Argument.
                Specifies the keyword 'register' being processed.
                Type: str

            udf_ids:
                Required Argument.
                Set of function names assigned to 'pandas_udf' functions.
                Type: set()

            ast_obj:
                Required Argument.
                ast object of 'register'.
                Type: ast object

        RETURNS:
            None
        """
        array_type_alias = self.__import_aliases.get('ArrayType', None)
        # Check for ArrayType in arguments
        if keyword in ['udf', 'register']:
            # Check positional arguments: 2nd argument (index 1) for udf, 3rd argument (index 2) for register
            if hasattr(ast_obj, 'args') and isinstance(ast_obj.args, list) and \
               ((len(ast_obj.args) > 1 and keyword == 'udf') or (len(ast_obj.args) > 2 and keyword == 'register')):
                arg_node = ast_obj.args[1] if keyword == 'udf' else ast_obj.args[2]
                if isinstance(arg_node, ast.Call) and isinstance(arg_node.func, ast.Name):
                        # Check if it's ArrayType or any of its aliases
                        if arg_node.func.id in ['ArrayType' , array_type_alias]:
                            if self.cell_no:
                                self._user_notes["udf"] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, "udf", None, UserNoteType.PARTIALLY_SUPPORTED)
                            else:
                                self._user_notes["udf"] = UserNote(self.start_line, self.end_line, "udf", None, UserNoteType.PARTIALLY_SUPPORTED)
            
            # Check keyword arguments for returnType parameter
            if hasattr(ast_obj, 'keywords') and len(ast_obj.keywords) > 0:
                for keyword_arg in ast_obj.keywords:
                    if hasattr(keyword_arg, 'arg') and hasattr(keyword_arg, 'value') and keyword_arg.arg == 'returnType':
                        value_node = keyword_arg.value
                        if isinstance(value_node, ast.Call) and isinstance(value_node.func, ast.Name):
                            # Check if it's ArrayType or any of its aliases
                            if value_node.func.id in ['ArrayType' , array_type_alias]:
                                if self.cell_no:
                                    self._user_notes["udf"] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, "udf", None, UserNoteType.PARTIALLY_SUPPORTED)
                                else:
                                    self._user_notes["udf"] = UserNote(self.start_line, self.end_line, "udf", None, UserNoteType.PARTIALLY_SUPPORTED)

        if keyword == 'register':
            # Check if the ast object has 'keywords' attribute and contains 'f'.
            if hasattr(ast_obj, 'keywords') and len(ast_obj.keywords) > 0:
                for keyword_arg in ast_obj.keywords:
                    # Check if the keyword argument is 'f' and contains 'pandas_udf' functions, then process user notes.
                    if hasattr(keyword_arg, 'arg') and hasattr(keyword_arg, 'value') and keyword_arg.arg == 'f' \
                        and isinstance(keyword_arg.value, ast.Name) and udf_ids is not None and keyword_arg.value.id in udf_ids:
                        self._process_user_notes(keyword)
            
            elif hasattr(ast_obj, 'args') and isinstance(ast_obj.args, list) and len(ast_obj.args) > 1 and \
                isinstance(ast_obj.args[1], ast.Name) and udf_ids is not None and ast_obj.args[1].id in udf_ids:
                        self._process_user_notes(keyword)

    def _check_and_process_user_notes_for_cast(self, arg, keyword):
        """Check if the argument is in specified types and process user notes."""
        not_supported_types = ['BooleanType', 'BinaryType', 'ArrayType', 'StructType', 'MapType']
        
        if arg in not_supported_types:
            self._process_user_notes(keyword, type=UserNoteType.NOT_SUPPORTED)
        elif arg == 'TimestampNTZType':
            self._process_user_notes(keyword, type=UserNoteType.PARTIALLY_SUPPORTED)

    def _check_and_process_call_for_cast(self, node, keyword):
        """Check if the node is a Call and process it."""
        if isinstance(node, ast.Call):
            # Determine the argument to process
            arg = node.func.attr if hasattr(node.func, 'attr') else node.func.id
            # Call the processing function with the determined argument
            self._check_and_process_user_notes_for_cast(arg, keyword)

    def _traverse_and_check_condition(self, node, keyword):
        """
        DESCRIPTION:
            Traverses the AST node and checks for specific conditions based on the keyword.
            It processes the user notes based on the specific conditions for each keyword.

        PARAMETERS:
            node:
                Required Argument.
                The AST node being processed.
                Type: ast.Node

            keyword:
                Required Argument.
                The specific keyword being processed (for 'cast', 'astype').
                Type: str

        RETURNS:
            None
        """
        if isinstance(node, ast.Call):
            # Handle 'cast' and 'astype' keywords.
            if keyword in ['cast', 'astype']:
                arg = node.func.attr if hasattr(node.func, 'attr') else node.func.id
                self._check_and_process_user_notes_for_cast(arg, keyword)
                
        # Recursively traverse the child nodes.
        for child in ast.iter_child_nodes(node):
            self._traverse_and_check_condition(child, keyword)

    def _process_keywords_call_args(self, obj, keyword):
        """
        DESCRIPTION:
            Processes specific PySpark keywords and their associated function calls.
            It handles different logic for 'get', 'cast', 'agg' keywords,
            analyzing their arguments and generating appropriate user notes based on
            the specific conditions for each keyword.

        PARAMETERS:
            obj:
                Required Argument.
                The AST node representing the function call or attribute being processed.
                Type: ast.Call or ast.Attribute

            keyword:
                Required Argument.
                The specific keyword being processed (for 'get', 'cast').
                Type: str

        RETURNS:
            None
        """
        # Check for keyword arguments.
        keyword_args = {}
        if hasattr(obj, 'keywords'):
            keyword_args = {kwarg.arg: kwarg.value for kwarg in obj.keywords}

        if keyword == 'get':
            stmt = ast.unparse(self.ast_obj)
            if "conf.get"  not in stmt:
                self._process_user_notes(keyword)
        
        elif keyword in ['cast', 'astype']:
            self._traverse_and_check_condition(obj, keyword)

            # Check keyword arguments.
            for kwarg_value in keyword_args.values():
                self._traverse_and_check_condition(kwarg_value, keyword)

        else:
            self._process_user_notes(keyword)

    def process_combined_attributes(self, file_path=None, interactive_mode=False, dir_path=None):
        """
        DESCRIPTION:
            Processes the stack to identify and handle combined attributes,
            adding appropriate user notes.

        PARAMETERS:
            file_path:
                Optional Argument.
                Path to the file being processed.
                Type: str

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool

            dir_path:
                Optional Argument.
                Path of directory being processed.
                Type: str

        RETURNS:
            None
        """
        for i, obj in enumerate(self._deque):
            current_name = self._get_variable_name(obj)
            self._update_readwrite_statements(current_name, file_path=file_path, interactive_mode=interactive_mode, dir_path=dir_path)
            if current_name in combined_attributes:
                unparsed_str = ast.unparse(self.ast_obj)
                # Check the next item in the stack for a matching attribute
                for attribute in combined_attributes[current_name]:
                    if attribute in unparsed_str:
                        combined_attr = f"{current_name}.{attribute}"
                        self._process_user_notes(combined_attr)

    def _update_readwrite_statements(self, name, file_path=None, interactive_mode=False, dir_path=None):
        """
        DESCRIPTION:
            Add the options method to read, write and writeTo attributes,
            which user can refer or use.

        PARAMETERS:
            name:
                Required Argument.
                Specifies whether it is 'read', 'write' or 'writeTo'.
                Type: str

            file_path:
                Optional Argument.
                Path to the file being processed.
                Type: str

            interactive_mode:
                Optional Argument.
                If True, the function will ask interactive questions for the DataFrameReader and DataFrameWriter operations.
                Type: bool

            dir_path:
                Optional Argument.
                Path of directory being processed.
                Type: str

        RETURNS:
            None.
            Note:
                Update the script based on 'name' arg.

        EXAMPLES:
            #  Examples when interactive_mode is False.
            >>> script = pyspark2teradataml("pyspark_session.read.csv('admissions_train.csv').show()")
            >>> self._update_readwrite_statements('read', file_path='train.py', interactive_mode=False)
            >>> print(self.modified_statement)
            teradatamlspk_session.read.options(authorization = {"Access_ID": "<Specify id(Required Argument)>", "Access_Key": "Specify key(Required Argument)"}).csv('admissions_train.csv').show()

            >>> script = pyspark2teradataml("df.write.parquet('output_dir')")
            >>> self._update_readwrite_statements('write', file_path='output.py', interactive_mode=False)
            >>> print(self.modified_statement)
            df.write.options(authorization = {"Access_ID": "<Specify id(Required Argument)>", "Access_Key": "Specify key(Required Argument)"}).parquet('output_dir')

            >>> script = pyspark2teradataml("df.writeTo('tablename').partitionedBy('column')")
            >>> self._update_readwrite_statements('writeTo')
            >>> print(self.modified_statement)
            df.writeTo.options(primary_index="column name or tuple of column names(Required Argument)").partitionedBy('column')

            # Interactive example (user input required for local/cloud and optional credentials)
            >>> self._update_readwrite_statements('read', file_path='train.py', interactive_mode=True)
            (prompts user for preference and updates statement accordingly)
        """
        stmt = ast.unparse(self.ast_obj)
        if name == "read":
            idx = stmt.index('read') + len('read')
            if 'json' in stmt or 'csv' in stmt or 'parquet' in stmt:
                if interactive_mode:
                    preference = cloud_handler.handle_preference(file_path=file_path, operation="read", line_number=self.start_line,
                                                                 dir_path=dir_path, cell_no=self.cell_no)
                    if preference == "cloud":
                        creds = cloud_handler.get_credentials()
                        new_stmt = "".join([
                            stmt[:idx],
                            f'.options(authorization = {{"Access_ID": "{creds["Access_ID"]}", "Access_Key": "{creds["Access_Key"]}"}})',
                            stmt[idx:]
                        ])
                        self.modified_statement = new_stmt
                else:
                    new_stmt = "".join([
                        stmt[:idx],
                        '.options(authorization = {"Access_ID": "<Specify id(Required Argument)>", "Access_Key": "Specify key(Required Argument)"})',
                        stmt[idx:]
                    ])
                    self.modified_statement = new_stmt

        elif name == "write":
            idx = stmt.index('write') + len('write')
            if 'csv' in stmt or 'parquet' in stmt:
                if interactive_mode:
                    preference = cloud_handler.handle_preference(file_path=file_path, operation="write", line_number=self.start_line,
                                                                 dir_path=dir_path, cell_no=self.cell_no)
                    if preference == "cloud":
                        creds = cloud_handler.get_credentials()
                        new_stmt = "".join([
                            stmt[:idx],
                            f'.options(authorization = {{"Access_ID": "{creds["Access_ID"]}", "Access_Key": "{creds["Access_Key"]}"}})',
                            stmt[idx:]
                        ])
                        self.modified_statement = new_stmt
                else:
                    new_stmt = "".join([
                        stmt[:idx],
                        '.options(authorization = {"Access_ID": "<Specify id(Required Argument)>", "Access_Key": "Specify key(Required Argument)"})',
                        stmt[idx:]
                    ])
                    self.modified_statement = new_stmt

        elif name == "writeTo":
            idx = stmt.index('writeTo') + len('writeTo')
            # When user uses 'partitionedBy' primary_index is only option Supported and Required.
            if "partitionedBy" in stmt:
                new_stmt = "".join([stmt[:idx],
                                    '.options(primary_index="column name or tuple of column names(Required Argument)")',
                                    stmt[idx:]])
                self.modified_statement = new_stmt

    @staticmethod
    def _get_variable_name(ast_obj):
        """Get the name from ast_obj"""
        if isinstance(ast_obj, ast.Name):
            return ast_obj.id
        elif isinstance(ast_obj, ast.Call):
            if isinstance(ast_obj.func, ast.Attribute):
                return ast_obj.func.attr
            elif isinstance(ast_obj.func, ast.Name):
                return ast_obj.func.id
            elif isinstance(ast_obj.func, ast.Call):
                # Nested call like func()(), return None or handle recursively
                return None
        elif isinstance(ast_obj, ast.Attribute):
            return ast_obj.attr
        return 

    def _process_user_notes(self, keyword, type=None):
        """
        DESCRIPTION:
            Creates user notes.

        PARAMETERS:
            keyword:
                Required Argument.
                To check and add the corresponding UserNote a keyword.

            type:
                Optional Argument.
                Specifies the type of user note to be created.
                Type: UserNoteType
                Default: None
            
        RETURNS:
            None.
        """

        not_supported = self.tdmlspk_notes.get("not_supported")
        partially_supported = self.tdmlspk_notes.get("partially_supported")
        notifications = self.tdmlspk_notes.get("notification")
        dynamic_user_notes = self.dynamic_notes

        # Check if type is provided(it is only provided for cast and astype).
        if type:
            notes_ = dynamic_user_notes[type.name][keyword]
            notes_type = type
        else:
            # Check for keyword and get the corresponding user notes.
            if keyword in not_supported:
                notes_ = not_supported[keyword]
                notes_type = UserNoteType.NOT_SUPPORTED
            elif keyword in partially_supported:
                notes_ = partially_supported[keyword]
                notes_type = UserNoteType.PARTIALLY_SUPPORTED
            elif keyword in notifications:
                notes_ = notifications[keyword]
                notes_type = UserNoteType.NO_ACTION
            elif keyword in dynamic_user_notes:
                    notes_ = dynamic_user_notes[keyword]
                    notes_type = UserNoteType.PARTIALLY_SUPPORTED if keyword== "register" else UserNoteType.NOT_SUPPORTED
            else:
                notes_ = None
                notes_type = None

        # Populate the notes here.
        if notes_:
            if self.cell_no:
                self._user_notes[keyword] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, keyword, notes_, notes_type)
            else:
                self._user_notes[keyword] = UserNote(self.start_line, self.end_line, keyword, notes_, notes_type)

    def __parse_statement(self, ast_obj):
        """
        DESIPTION:
            Recursively parses an AST node and stores in self.stack.

        PARAMETERS:
            ast_obj:
                Required Argument.
                The AST node to be parsed.
                Types: ast.AST
            
        RETURNS:
            None.
        """
        # If it is an expression, simply pass the value to it.
        # Do not consider anything else.
        if isinstance(ast_obj, ast.Expr):
            # Expression statement .
            # Example: print("Hello")
            self.__parse_statement(ast_obj.value)

        elif isinstance(ast_obj, (ast.Name, ast.Constant)):
            # A variable name and  constants.
            self._deque.appendleft(ast_obj)

        elif isinstance(ast_obj, (ast.Subscript)):
            # Subscript: An indexing or slicing operation.
            # Example: list[0], dict['key']
            self._deque.appendleft(ast_obj)
            self.__parse_statement(ast_obj.value)

        elif isinstance(ast_obj, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            # Assign: A regular assignment (x = y)
            # AnnAssign: An annotated assignment (x: int = 5)
            # AugAssign: An augmented assignment (x += 1)
            target_names = set()
            if isinstance(ast_obj, ast.Assign):
                target_names = {target.id for target in ast_obj.targets if isinstance(target, ast.Name)}
            elif isinstance(ast_obj, ast.AnnAssign):
                if isinstance(ast_obj.target, ast.Name):
                    target_names = {ast_obj.target.id}
            elif isinstance(ast_obj, ast.AugAssign):
                if isinstance(ast_obj.target, ast.Name):
                    target_names = {ast_obj.target.id}
            
            self._current_targets = target_names
            # Only parse the value if it is not None.
            if ast_obj.value:
                self.__parse_statement(ast_obj.value)

            # Check if value is an array function call, then add targets to array_variables.
            if isinstance(ast_obj.value, ast.Call):
                func_name = self._get_variable_name(ast_obj.value)
                # Resolve alias to check if it's an array function
                original_func_name = self.__import_aliases.get(func_name, func_name)
                if original_func_name in self.ARRAY_FUNCTIONS:
                    for target_name in target_names:
                        self._array_functions_in_statement.add(target_name)
                        # Also add to spark_variables so it persists across statements
                        self.__spark_variables.add(target_name)

        elif isinstance(ast_obj, (ast.Tuple, ast.List)):
            # Tuple or List: A tuple or list literal.
            for element in ast_obj.elts:
                self._deque.appendleft(element)
                self.__parse_statement(element)

        elif isinstance(ast_obj, ast.Call):
            # A function call
            # If it is a call object, it will have a func. If func is Name, then store it as it is.
            if isinstance(ast_obj.func, ast.Name):
                self._deque.appendleft(ast_obj)
            elif isinstance(ast_obj.func, ast.Attribute):
                # Construct Call object.
                call_obj = ast.Call(func=ast.Name(id=ast_obj.func.attr, ctx=ast.Load()),
                                    args=ast_obj.args,
                                    keywords=ast_obj.keywords)
                self._deque.appendleft(call_obj)
                self.__parse_statement(ast_obj.func.value)
            # In rare cases, even func also can have another function 'tdmlspk_dummy'.
            # In such cases, create another Call object with dummy name.
            # When populating the user guide in such cases, one should look at
            # function name and take call appropriately.
            # Nested function call: func()()
            elif isinstance(ast_obj.func, ast.Call):
                call_obj = ast.Call(func=ast.Name(id="tdmlspk_dummy", ctx=ast.Load()),
                                    args=ast_obj.args,
                                    keywords=ast_obj.keywords)
                self._deque.appendleft(call_obj)
                self.__parse_statement(ast_obj.func)
            
            # Track array functions for this call
            func_name = self._get_variable_name(ast_obj)
            # Resolve alias to check if it's an array function
            original_func_name = self.__import_aliases.get(func_name, func_name)
            if original_func_name in self.ARRAY_FUNCTIONS:
                self._array_functions_in_statement.add(func_name)

        elif isinstance(ast_obj, ast.Attribute):
            self._deque.appendleft(ast.Name(id=ast_obj.attr, ctx=ast.Load()))
            self.__parse_statement(ast_obj.value)

        elif isinstance(ast_obj, ast.BinOp):
            # A binary operation (e.g., x + y)
            # Process the left and right operands
            self._deque.appendleft(ast_obj.left)
            self.__parse_statement(ast_obj.left)  
            self._deque.appendleft(ast_obj.right)
            self.__parse_statement(ast_obj.right)  
        else:
            # Here walk through the ast_obj and extract all names, if attribute then attr,
            # if function then func.id, if name then id and blindly populate the UserNotes.
            for sub_node in ast.walk(ast_obj):
                if isinstance(sub_node, (ast.Name, ast.Attribute)):
                    name = sub_node.id if isinstance(sub_node, ast.Name) else sub_node.attr
                    if self.start_line == self.end_line:
                        if name in ['cast', 'astype']:
                            self._process_keywords_call_args(ast_obj, name)
                        elif name in self.ARRAY_FUNCTIONS:
                            pass  # Skip, handle later
                        else:
                            self._process_user_notes(name)
                        self.is_spark_component_involved=True
                # Skip Call nodes in the walk - they're already handled and added to _deque
                elif isinstance(sub_node, ast.Call):
                    # Get the function name from the call
                    func_name = self._get_variable_name(sub_node)
                    # Resolve alias to check if it's an array function
                    original_func_name = self.__import_aliases.get(func_name, func_name)
                    # Only track array functions, don't process user notes here
                    if original_func_name in self.ARRAY_FUNCTIONS:
                        self._array_functions_in_statement.add(func_name)

    def _contains_nested_array_functions(self, node, pyspark_variables):
        """
        DESCRIPTION:
            Unified method to check if a node contains nested functions including:
            array functions, lambda functions, arithmetic operations, or tracked variables.

        PARAMETERS:
            node:
                Required Argument.
                The AST node being checked.
                Type: ast.Node

            pyspark_variables:
                Required Argument.
                Set of variable names containing PySpark data.
                Type: set

        RETURNS:
            bool: True if nested functions are found, False otherwise.
        """
        if isinstance(node, ast.Name) and node.id in pyspark_variables:
            return True
        if isinstance(node, ast.Lambda):
            return True
        if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare)):
            return True

        if isinstance(node, ast.Call):
            func_name = self._get_variable_name(node)
            # Apart from 'col' and 'lit', consider all function calls as nested functions.
            if func_name not in ['col', 'lit']:
                return True
            # Recursively check arguments even for col/lit
            return any(self._contains_nested_array_functions(arg, pyspark_variables) for arg in node.args) or \
                any(self._contains_nested_array_functions(kw.value, pyspark_variables) for kw in node.keywords)
        return False

    def has_nested_array(self, node, pyspark_variables):
        """
        DESCRIPTION:
            Checks if an array function contains nested/derived expressions.

        PARAMETERS:
            node:
                Required Argument.
                The AST node being checked.
                Type: ast.Node

            pyspark_variables:
                Required Argument.
                Set of variable names containing PySpark data.
                Type: set

        RETURNS:
            bool: True if nested/derived expressions are found, False otherwise.
        """
        if isinstance(node, ast.Call):
            for arg in node.args:
                if self._contains_nested_array_functions(arg, pyspark_variables):
                    return True
            for kw in node.keywords:
                if self._contains_nested_array_functions(kw.value, pyspark_variables):
                    return True

        return False

    def __process_import(self, ast_obj):
        """
        DESCRIPTION:
            Parses the import statement and populates corresponding user notes.

        PARAMETERS:
            ast_obj:
                Required Argument.
                The AST object representing the import statement to be parsed.
                Type: ast.Import or ast.ImportFrom

        RETURNS:
            None
        """
        not_supported = self.tdmlspk_notes.get("not_supported")

        #  Pass ast obj to the _ImportParser class.
        translated_line, invalid_imports, spark_imports, alias_mapping = _ImportParser(ast_obj, not_supported).get_imports() 
        if spark_imports:
            self.__spark_imports = self.__spark_imports.union(set(spark_imports))
        if alias_mapping:
            self.__import_aliases.update(alias_mapping)
        # Create UserNotes for all the invalid imports.
        if invalid_imports:
            for import_info in invalid_imports:
                obj_name = import_info['obj']
                notes_ = not_supported[obj_name]
                notes_ = f"It's an Import statement. {notes_} <span style='font-style: italic;'> Import is ignored for {obj_name}. </span>"
                if self.cell_no:
                    self._user_notes[obj_name] = NotebookUserNote(self.cell_no, self.start_line, self.end_line, obj_name, notes_, UserNoteType.NO_ACTION)
                else:
                    self._user_notes[obj_name] = UserNote(self.start_line, self.end_line, obj_name, notes_, UserNoteType.NO_ACTION)

        # If line is modified then add that into self.modified_statement.
        if translated_line is not None:
            self.modified_statement = translated_line
                
    def get_user_guide(self):
        """
        DESCRIPTION:
            Retrieves the user guide for the corresponding statement.

        PARAMETERS:
            None

        RETURNS:
            list:
                A list of user notes associated with the statement.
                Each element represents a user note.
                Type: List[UserNote]
        """
        return list(self._user_notes.values()) 