import os
from teradatamlspk.converter.utils import Script, Directory, Notebook


def pyspark2teradataml(file_path, csv_report=False, interactive_mode=False):
    """
    DESCRIPTION:
        Utility which analyses and produces the script/notebook to run on Teradata Vantage.
        It supports PySpark scripts, Jupyter notebooks, and directories containing such files.
        Notes:   
            1. If a notebook is analyzed by utility, it expects all the code cells are syntactically correct.
               If any of the code cell is syntactically incorrect, the utility will not convert the entire notebook.
            2. teradatamlspk can read and write files from both the local file system and cloud 
               storage. To access cloud storage, it requires an access ID and access key. User 
               can set the environment variables "Access_ID" and "Access_Key", allowing pyspark2teradataml 
               to automatically include these credentials in the converted script.

    PARAMETERS:
        file_path : 
            Required Argument.
            Specifies the path to the file or directory to be converted.
            Type: str
        
        csv_report :
            Optional Argument.
            When set to True, function generates csv file which has summary for every python script/notebook 
            along with alert details.
            Type: bool

        interactive_mode :
            Optional Argument.
            Specifies whether to ask questions for DataFrame operations which reads from file or 
            writes to file. When set to True, function asks questions whether to consider reading 
            or writing from cloud storage or from local file system. Otherwise, function considers 
            the file is in cloud storage and generates the corresponding teradatamlspk script/notebook.
            Type: bool
    
    RAISES:
        FileNotFoundError:
            If the provided file path does not exist.

    EXAMPLES:
        >>> from teradatamlspk import pyspark2teradataml
        >>> pyspark2teradataml('path/to/your/script.py')
        >>> pyspark2teradataml('path/to/your/notebook.ipynb')
        >>> pyspark2teradataml('path/to/your/directory')
    """
    if (not os.path.exists(file_path)):
        raise FileNotFoundError("Path '{}' not found.".format(file_path))
    
    if os.path.isdir(file_path):
        Directory(file_path).process(csv_report=csv_report, interactive_mode=interactive_mode)
    elif os.path.splitext(file_path)[1] == '.ipynb':
        Notebook(file_path).process(csv_report=csv_report, interactive_mode=interactive_mode)
    else:
        Script(file_path).process(csv_report=csv_report, interactive_mode=interactive_mode)
