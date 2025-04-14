import logging
import pathlib
from typing import Tuple

import great_expectations as gx
import pandas as pd


class Parse_GXValidator:
    def __init__(self, data_source_name: str):
        """Initializes the GXValidator class with the data source name and logger."""
        self.data_source_name = data_source_name
        self.log = logging.getLogger("GX validation")
        self.context = gx.data_context.get_context()  # Instantiate a GX data context (adjust as needed)

    def extract_validation_result_from_checkpoint_result(
            self, checkpoint_result: gx.checkpoint.checkpoint.CheckpointResult
    ) -> dict:
        """Extracts the first validation result from a Checkpoint run result."""
        # Assuming the checkpoint result has multiple batches being validated, so we access the first one
        validation_result = checkpoint_result.run_results[
            list(checkpoint_result.run_results.keys())[0]
        ]
        return validation_result

    def separate_valid_and_invalid_rows(
            self, df: pd.DataFrame, validation_result: dict
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Separate valid and invalid rows based on validation results."""
        failing_expectations = [result for result in validation_result["results"] if not result["success"]]

        invalid_row_indices = []

        # Check if any expectations failed
        if not failing_expectations:
            self.log.warning("No expectations failed. Returning all rows as valid.")
            return df, pd.DataFrame()

        # Loop over failed expectations to find invalid rows
        for expectation in failing_expectations:
            # Access the 'unexpected_index_list' from the validation result
            unexpected_index_list = expectation["result"].get("unexpected_index_list", [])

            # If unexpected indices exist, add them to the invalid list
            if unexpected_index_list:
                invalid_row_indices.extend(unexpected_index_list)
            else:
                self.log.warning(
                    f"No unexpected indices found for expectation: {expectation['expectation_config']['id']}")

        # Deduplicate invalid row indices
        invalid_row_indices = list(set(invalid_row_indices))

        # If invalid rows exist, separate them
        if invalid_row_indices:
            df_invalid = df.iloc[invalid_row_indices].reset_index(drop=True)
        else:
            df_invalid = pd.DataFrame()

        # Separate valid rows (everything except the invalid ones)
        df_valid = df.drop(df.index[invalid_row_indices]).reset_index(drop=True)

        return df_valid, df_invalid

    def write_invalid_rows_to_file(self, filepath: pathlib.Path, df: pd.DataFrame):
        """Write invalid rows to an error file."""
        try:
            df.to_csv(filepath, index=False)
            self.log.warning(f"{df.shape[0]} invalid rows written to error file.")
        except Exception as e:
            self.log.error(f"Error writing invalid rows to file: {e}")

    def parse_validation_result(self, checkpoint_result: gx.checkpoint.checkpoint.CheckpointResult, df: pd.DataFrame) -> \
            Tuple[pd.DataFrame, pd.DataFrame]:
        """Helper function to parse the validation result and separate valid/invalid rows."""
        try:
            # Extract the validation result from the checkpoint result
            validation_result = self.extract_validation_result_from_checkpoint_result(checkpoint_result)

            # Separate valid and invalid rows based on validation results
            return self.separate_valid_and_invalid_rows(df, validation_result)
        except Exception as e:
            self.log.error(f"Error during result parsing: {e}")
            raise ValueError(f"Error during result parsing: {e}")
