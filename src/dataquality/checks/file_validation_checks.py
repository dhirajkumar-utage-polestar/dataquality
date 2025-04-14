import gzip
import logging
import os
import zipfile
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FileValidator:
    def __init__(self, filepath: str, validation_config: dict):
        """
        Initialize the FileValidator with the file and validation criteria from YAML.

        Args:
            filepath (str): The file path to validate.
            validation_config (dict): The validation config loaded from YAML.
        """
        self.filepath = filepath
        self.validation_config = validation_config

    def validate(self) -> list:
        """
        Perform file and data validation checks based on the provided config.
        Returns:
            List of validation results, each containing a check name, result, and details.
        """

        results = []
        # Validate file properties (format, size, compression, date)
        for check in self.validation_config.get('file_validation', []):
            check_name = check['name']
            result_dict = None  # Initialize result dictionary for each check

            if check_name == "ValidateFileFormat":
                result_dict = self.validate_file_format(check)
            elif check_name == "ValidateFileSize":
                result_dict = self.validate_file_size(check)
            elif check_name == "ValidateCompressed":
                result_dict = self.validate_compressed_file(check)
            elif check_name == "ValidateFileDate":
                result_dict = self.validate_file_date(check)

            if result_dict:  # Ensure the result_dict is always appended
                results.append(result_dict)

        return results

    # File Validations
    def validate_file_format(self, check) -> dict:
        """Ensure the file has an allowed format based on its extension."""
        filename = os.path.basename(self.filepath)
        file_extension = os.path.splitext(filename)[1].lower()
        allowed_extensions = check.get('allowed_extensions', [])
        if file_extension in allowed_extensions:
            return {"check_name": "File Format", "result": True, "details": f"Valid format: {file_extension}"}
        return {"check_name": "File Format", "result": False, "details": f"Invalid format: {file_extension}"}

    def validate_file_size(self, check) -> dict:
        """Ensure the file is not too large."""
        file_size_mb = os.path.getsize(self.filepath) / (1024 * 1024)
        max_size_mb = check.get('max_size_mb', 100)
        if file_size_mb <= max_size_mb:
            return {"check_name": "File Size", "result": True, "details": f"Acceptable size: {file_size_mb:.2f} MB"}
        return {"check_name": "File Size", "result": False,
                "details": f"File size exceeds the limit: {file_size_mb:.2f} MB"}

    def validate_compressed_file(self, check) -> dict:
        """Ensure the file is correctly compressed."""
        allowed_compressions = check.get('allowed_compressions', [])
        try:
            if self.filepath.endswith('.zip') and 'zip' in allowed_compressions:
                with zipfile.ZipFile(self.filepath, 'r') as zip_ref:
                    zip_ref.testzip()
                return {"check_name": "Compressed File", "result": True, "details": "Valid zip file."}
            elif self.filepath.endswith('.gz') and 'gz' in allowed_compressions:
                with gzip.open(self.filepath, 'rb') as f:
                    f.read()
                return {"check_name": "Compressed File", "result": True, "details": "Valid gzip file."}
        except (zipfile.BadZipFile, gzip.BadGzipFile) as e:
            return {"check_name": "Compressed File", "result": False, "details": f"Compression failed: {e}"}
        return {"check_name": "Compressed File", "result": False, "details": "Not a valid compressed file."}

    def validate_file_date(self, check) -> dict:
        """Ensure the file's modification date matches the business date."""
        business_date_str = check.get('business_date')
        if not business_date_str:
            return {"check_name": "File Date", "result": False, "details": "Business date not provided in the config."}

        try:
            business_date = datetime.strptime(business_date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"check_name": "File Date", "result": False,
                    "details": f"Invalid business date format: {business_date_str}"}

        file_modification_time = os.path.getmtime(self.filepath)
        file_modification_date = datetime.fromtimestamp(file_modification_time).date()

        if file_modification_date == business_date:
            return {"check_name": "File Date", "result": True,
                    "details": f"Modification date matches business date: {file_modification_date}"}
        return {"check_name": "File Date", "result": False,
                "details": f"Modification date does not match business date: {file_modification_date}"}
