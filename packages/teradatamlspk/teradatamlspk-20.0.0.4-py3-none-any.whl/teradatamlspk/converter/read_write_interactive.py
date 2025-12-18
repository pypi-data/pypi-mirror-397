import os, json
class InteractivePreferenceHandler:
    """
    DESCRIPTION:
        This class handles user preferences for read/write operations in an interactive manner.
        It allows users to set directory preferences, file-specific preferences, and manage cloud credentials.

    """
    def __init__(self):
        self.cloud_credentials = {"Access_ID": None, "Access_Key": None}
        self.directory_preference = {"read": None, "write": None}
        self.file_preferences = {} # e.g., {filename: {"read": "local/cloud", "write": "local/cloud"}}
        self.asked_directory = {}  # e.g., {"read": True, "write": False}

    def set_directory_preference(self, operation, preference):
        """
        DESCRIPTION:
            Set the directory preference for a given operation.

        PARAMETERS:
            operation:
                Required Argument.
                The operation type, either 'read' or 'write'.
                Type: str

            preference:
                Required Argument.
                The preferred storage type, either 'local' or 'cloud'.
                Type: str

        RETURNS:
            None.

        EXAMPLES:
            >>> handler.set_directory_preference('read', 'cloud')
        """
        self.directory_preference[operation] = preference

    def get_directory_preference(self, operation):
        """
        DESCRIPTION:
            Get the directory preference for a specific operation.

        PARAMETERS:
            operation:
                Required Argument.
                The operation type, either 'read' or 'write'.
                Type: str

        RETURNS:
            str or None: 'local', 'cloud', or None if not set.

        EXAMPLES:
            >>> handler.get_directory_preference('read')
            'cloud'
        """
        return self.directory_preference[operation]

    def set_file_preference(self, filename, operation, preference):
        """
        DESCRIPTION:
            Set file-specific preference for read/write operations.
            Initializes preferences for the file if not already present.

        PARAMETERS:
            filename:
                Required Argument.
                The name/path of the file to set preferences for.
                Type: str

            operation:
                Required Argument.
                The operation type, either 'read' or 'write'.
                Type: str

            preference:
                Required Argument.
                The preferred storage type, either 'local' or 'cloud'.
                Type: str

        RETURNS:
            None.

        EXAMPLES:
            >>> handler.set_file_preference('train.py', 'read', 'local')
        """
        if filename not in self.file_preferences:
            self.file_preferences[filename] = {}
        self.file_preferences[filename][operation] = preference

    def get_file_preference(self, filename, operation):
        """
        DESCRIPTION:
            Get the file-specific preference for a specific operation.
            
        PARAMETERS:
            filename:
                Required Argument.
                The name/path of the file to get preferences for.
                Type: str
                
            operation:
                Required Argument.
                The operation type, either 'read' or 'write'.
                Type: str

        RETURNS:
            str or None: 'local', 'cloud', or None if not set.

        EXAMPLES:
        >>> handler.get_file_preference('train.py', 'read')
        'local'

        """
        return self.file_preferences.get(filename, {}).get(operation, None)

    def set_credentials(self):
        """
        DESCRIPTION:
            Set cloud credentials from environment variables and 
            store them in the cloud_credentials dictionary.
            The credentials are expected to be set in the environment variables:
            - Access_ID
            - Access_Key

        PARAMETERS:
            None.

        RETURNS:
            None.

        EXAMPLES:
            >>> handler.set_credentials()
        """
        self.cloud_credentials["Access_ID"] = os.getenv("Access_ID", "<Specify id (Required Argument)>")
        self.cloud_credentials["Access_Key"] = os.getenv("Access_Key", "<Specify key (Required Argument)>")
    def get_credentials(self):
        """
        DESCRIPTION:
            Get credentials for cloud storage.

        PARAMETERS:
            None.

        RETURNS:
            A dictionary containing the cloud credentials.
            Type: dict

        EXAMPLES:
            >>> handler.get_credentials()
            {'Access_ID': 'your_access_id', 'Access_Key': 'your_access_key'}
        """
        return self.cloud_credentials

    def _build_operation_prompt(self, operation, file_path, line_number=None, cell_no=None):
        """
        DESCRIPTION:
            Build a prompt message for the user based on the operation type and file path.

        PARAMETERS:
            operation:
                Required Argument.
                The operation type, either 'read' or 'write'.
                Type: str

            file_path:
                Required Argument.
                The file path from which the operation was encountered.
                Type: str

            line_number:
                Optional Argument.
                The line number where the operation was found (for display only).
                Type: int

            cell_no:
                Optional Argument.
                The cell number in a notebook where the operation was found (for display only).
                Type: int

        RETURNS:
            The choice of user preference: 'local' or 'cloud'.
            Type: str
        """
        op_type = "read" if operation == "read" else "write"
        action = "read from local file or cloud storage" if operation == "read" else "write to local file or cloud storage"
        if cell_no is not None:
            if isinstance(cell_no, str) and cell_no.startswith("Empty"):
                cell_info = f'\'{cell_no}\''
            else:
                cell_info = f'cell number \'{cell_no}\''
            return (
                f"\n\nEncountered {op_type} operation in {cell_info} line \'{line_number}\' from {file_path}, "
                f"would you like to {action}? (local/cloud): "
            )
        else:
            return (
                f"\n\nEncountered {op_type} operation in line \'{line_number}\' from {file_path}, "
                f"would you like to {action}? (local/cloud): "
            )
    
    def handle_preference(self, file_path, operation, line_number=None, dir_path=None, cell_no=None):
        """
        DESCRIPTION:
            Determine user preference (local or cloud) for a specific read/write operation.
            Follows this flow:
              1. Check for existing directory preference.
              2. Check for file-specific preference.
              3. Prompt the user interactively.
              4. If cloud is selected, fetch from environmen variables.
              5. Ask if the preference should apply for directory or just for the file.

         PARAMETERS:
            file_path:
                Required Argument.
                The file path from which the operation was encountered.
                Type: str

            operation:
                Required Argument.
                The operation type ('read' or 'write').
                Type: str

            line_number:
                Optional Argument.
                The line number where the operation was found (for display only).
                Type: int

            dir_path:
                Optional Argument.
                The directory path from which the operation was encountered.
                Type: str

            cell_no:
                Optional Argument.
                The cell number in a notebook where the operation was found (for display only).
                Type: int 

        RETURNS:
            str:
                The user's chosen preference: 'local' or 'cloud'.
        EXAMPLES:
            >>> handler.handle_preference('data.py', 'read', line_number=22)
            (Prompts the user and returns 'local' or 'cloud')
        """
        # Check directory preference.
        directory_pref = self.get_directory_preference(operation)
        if directory_pref:
            self.set_file_preference(file_path, operation, directory_pref)
            return directory_pref

        # Check file-level preference.
        file_pref = self.get_file_preference(file_path, operation)
        if file_pref:
            return file_pref

        # Prompt the user.
        while True:
            choice = input(self._build_operation_prompt(operation, file_path, line_number, cell_no)).strip().lower()
            if choice in ["local", "cloud"]:
                break
            print("Invalid input. Type 'local' or 'cloud'.")

        # If cloud, ask for cloud system.
        if choice == "cloud":
              self.set_credentials()
                
        # Ask if preference should be applied to all files.
        if dir_path and not self.asked_directory.get(operation):
            while True:
                apply_directory = input(f"Would you like to apply this setting to the directory '{dir_path}'? (y/n): ").strip().lower()
                if apply_directory in ["y", "n", "yes", "no"]:
                    break
                print("Answer with 'yes/y' or 'no/n'.")
            # Mark as asked.
            self.asked_directory[operation] = True

            if apply_directory == "y":
                self.set_directory_preference(operation, choice)
                return choice

        # Ask if preference should be applied to this file.
        while True:
            apply_file = input("Would you like to apply this setting on this file? (y/n): ").strip().lower()
            if apply_file in ["y", "n", "yes", "no"]:
                break
            print("Answer with 'yes/y' or 'no/n'.")

        if apply_file == "y":
            self.set_file_preference(file_path, operation, choice)

        return choice
