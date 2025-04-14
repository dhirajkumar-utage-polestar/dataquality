import re
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd

from dataquality.checks.file_validation_checks import FileValidator
from dataquality.config.settings import CONFIG_YAML_PATH, S3_REGION, DATA_QUALITY_PATH, BUCKET_NAME
from dataquality.utils.ExpectationMapper import ExpectationMapper
from dataquality.utils.file_utils import load_yaml_config
from dataquality.utils.parse_validation_result import Parse_GXValidator
from dataquality.validators.validate import DataValidator


class StopProcessError(Exception):
    """
    Custom Exception to Raise for Failure Action
    """
    pass


class ValidationProcessor:
    def __init__(self, file_path: str, yaml_config_path: str,
                 dataframe: pd.DataFrame, process_id: str,
                 invalid_file_path: str = None, site_name: str = None):
        """Initializes the ValidationProcessor with necessary configurations and file paths."""

        self.process_id = process_id
        self.file_path = file_path
        self.yaml_config_path = yaml_config_path
        self.invalid_file_path = invalid_file_path
        self.df = dataframe

        ## GX setting
        self.site_name = self.generate_dynamic_value(site_name, "DATA_DOCS_SITE")
        self.data_source_name = self.generate_dynamic_value(process_id, "DATA_SOURCE")
        self.data_asset_name = self.generate_dynamic_value(process_id, "DATA_ASSET")
        self.expectation_suite_name = self.generate_dynamic_value(process_id, "EXPECTATION_SUITE")
        self.checkpoint_name = self.generate_dynamic_value(process_id, "CHECKPOINT")
        self.validation_definition_name = self.generate_dynamic_value(process_id, "VALIDATION_DEFINITION")

        self.validation_config = None
        self.mapped_expectations = None
        self.validation_results = None
        self.expectation_mapping_config_path = CONFIG_YAML_PATH

        # S3 Config
        self.s3_client = boto3.client('s3', region_name=S3_REGION)
        self.bucket_name = BUCKET_NAME
        self.data_quality_path = DATA_QUALITY_PATH
        self.process_id = process_id

    def generate_dynamic_value(self, process_id: str, suffix: str) -> str:
        """
        Generates dynamic values for attributes by combining the `process_id` with a suffix.
        e.g., if process_id = 'AIS' and suffix = 'DATA_SOURCE', it returns 'AIS_DATA_SOURCE'.
        """
        return f"{process_id}_{suffix}"

    def load_data(self):
        """Load the validation configuration.
           using YAML file
        """
        self.validation_config = load_yaml_config(self.yaml_config_path)

    def validate_file(self):
        """
        Run file validations.
        """
        file_validator = FileValidator(self.file_path, self.validation_config)
        file_validation_results = file_validator.validate()
        return file_validation_results

    def validate_expectations(self):
        """Validate expectations using mapped expectations."""
        mapped_expectation = ExpectationMapper(self.expectation_mapping_config_path)
        val_dict = self.validation_config.get('expectations', [])
        self.mapped_expectations = mapped_expectation.map_user_expectations(val_dict)

        expectation_validator = DataValidator(
            dataframe=self.df,
            data_source_name=self.data_source_name,
            data_asset_name=self.data_asset_name,
            docs_build_action=True,
            site_name=self.site_name,
            expectation_suite_name=self.expectation_suite_name,
            checkpoint_name=self.checkpoint_name,
            validation_definition_name=self.validation_definition_name
        )

        expectation_validation_results, context = expectation_validator.validate(self.mapped_expectations)
        return expectation_validation_results, context

    def process_results(self, expectation_validation_results):
        """Process the validation results to separate valid and invalid rows."""
        gx_parse_val = Parse_GXValidator(data_source_name=self.data_source_name)
        result = gx_parse_val.extract_validation_result_from_checkpoint_result(expectation_validation_results)
        return result

    def save_invalid_rows(self, df_invalid):
        """Save the invalid rows to a file if the invalid file path is provided."""
        if self.invalid_file_path and not df_invalid.empty:
            try:
                df_invalid.to_csv(self.invalid_file_path, index=False)
                print(f"Invalid records have been saved to: {self.invalid_file_path}")
            except Exception as e:
                print(f"Error saving invalid rows: {e}")

    def save_invalid_rows_S3(self, df_invalid):
        """Save the invalid rows to S3 in a structured path with date-based folders."""
        if not df_invalid.empty:
            try:

                current_date = datetime.now()
                year_folder = current_date.strftime('%Y')
                month_folder = current_date.strftime('%m')
                day_folder = current_date.strftime('%d')

                file_key = f"{self.data_quality_path}/{year_folder}/{month_folder}/{day_folder}/{self.process_id}_data_{current_date.strftime('%Y%m%d%H%M%S')}.csv"

                csv_buffer = StringIO()
                df_invalid.to_csv(csv_buffer, index=False)

                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=file_key,
                    Body=csv_buffer.getvalue(),
                    ContentType="text/csv"  # Optional: Content type for the file
                )

                print(f"Invalid records have been saved to S3: {self.bucket_name}/{file_key}")

            except Exception as e:
                print(f"Error saving invalid rows to S3: {e}")

    def display_results(self, file_validation_results, df_valid, df_invalid):
        """Display the validation results."""
        print("File Validation Results:")
        for result in file_validation_results:
            if isinstance(result, dict):  # Check if result is a dictionary
                print(
                    f"Check Name: {result['check_name']}, Result: {'Passed' if result['result'] else 'Failed'}, Details: {result['details']}")
            else:
                print(f"Unexpected result format: {result}")

        print("\nData Expectation Results:")
        print(f"Valid Rows Count: {df_valid.count()}")
        print(f"Invalid Rows Count: {df_invalid.count()}")
        if not df_invalid.empty:
            print("Invalid rows are present.")
        else:
            print("No invalid rows found.")

    def normalize_to_camel_case(self, name):
        """Convert snake_case to camelCase."""
        name_parts = name.split('_')
        name = name_parts[0] + ''.join(word.capitalize() for word in name_parts[1:])
        return name

    def normalize_expectation_name(self, name):
        """Normalize expectation names to snake_case."""
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        return name.strip().lower()

    def normalize_to_pascal_case(self, name):
        """Convert snake_case to PascalCase."""
        name_parts = name.split('_')
        name = ''.join(word.capitalize() for word in name_parts)
        return name

    def run(self):
        """Main method to run all the validation steps."""
        # Load validation configuration
        self.load_data()

        # Validate file
        file_validation_results = self.validate_file()
        print(file_validation_results)

        # Validate expectations
        expectation_validation_results, _ = self.validate_expectations()
        action_dict = self.validation_config.get('expectations', [])
        result = self.process_results(expectation_validation_results)

        expectations_action_dict = {(expectation['name'], expectation['column']): expectation['action'] for expectation
                                    in action_dict}

        invalid_rows = []
        invalid_row_indices = []

        # Collecting invalid rows and adding the expectation failed info
        for result in result["results"]:
            if not result["success"]:
                expectation_name = result["expectation_config"]["type"]
                expectation_column = result['expectation_config']['kwargs']['column']
                normalized_expectation_name = self.normalize_to_pascal_case(expectation_name)

                action = expectations_action_dict.get((normalized_expectation_name, expectation_column), None)

                if action == "skip":
                    # Get the indices of the invalid rows
                    unexpected_index_list = result["result"]["unexpected_index_list"]

                    if unexpected_index_list:
                        invalid_row_indices.extend(unexpected_index_list)

                    # Add the failed expectation info to the invalid rows
                    for idx in unexpected_index_list:
                        invalid_row = self.df.iloc[idx].copy()  # Copy the invalid row
                        invalid_row['expectation_failed_name'] = normalized_expectation_name
                        invalid_row['expectation_failed_column'] = expectation_column
                        invalid_rows.append(invalid_row)

                elif action == "failure":
                    # Raise an exception to stop the process
                    raise StopProcessError(
                        f"Action 'failure' encountered for expectation {normalized_expectation_name} on column {expectation_column}. Stopping the process.")

        invalid_row_indices = list(set(invalid_row_indices))

        # If invalid rows exist, save them to a file
        if invalid_rows:
            invalid_df = pd.DataFrame(invalid_rows)
            self.save_invalid_rows(invalid_df)
            self.save_invalid_rows_S3(invalid_df)

        # Separate invalid rows
        if invalid_row_indices:
            df_invalid = self.df.iloc[invalid_row_indices].reset_index(drop=True)
        else:
            df_invalid = pd.DataFrame()

        # Separate valid rows
        df_valid = self.df.drop(self.df.index[invalid_row_indices]).reset_index(drop=True)
        print("Process completed.")

        self.display_results(file_validation_results, df_valid, df_invalid)

        return df_valid
