import logging
from typing import List

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Validate_Without_Batch:
    def __init__(self,
                 df: pd.DataFrame,
                 expectations: List[gxe.Expectation],
                 data_source_name: str = "testing_source",
                 asset_name: str = "testing_asset",
                 expectation_suite_name: str = "Passenger Count Checker",
                 validation_definition_name: str = "validation_definition",
                 checkpoint_name: str = "validation_checkpoint"):
        """
        Initialize the class with a Pandas DataFrame and a list of expectations.

        Args:
            df (pd.DataFrame): Pandas dataframe.
            expectations (List[gxe.Expectation]): List of expectations to apply to the dataframe.
            data_source_name (str): Name of the data source.
            asset_name (str): Name of the asset.
            expectation_suite_name (str): Name of the expectation suite.
            validation_definition_name (str): Name of the validation definition.
            checkpoint_name (str): Name of the checkpoint.
        """
        # Initialize the Great Expectations context
        self.context = gx.get_context(mode="ephemeral")

        self.df = df
        self.expectations = expectations
        self.data_source_name = data_source_name
        self.asset_name = asset_name
        self.expectation_suite_name = expectation_suite_name
        self.validation_definition_name = validation_definition_name
        self.checkpoint_name = checkpoint_name

        # Initialize placeholders
        self.datasource = None
        self.data_asset = None
        self.batch_definition = None
        self.batch = None
        self.expectation_suite = None
        self.validation_definition = None
        self.checkpoint = None

    def add_data_source(self):
        """Add the data source (Pandas DataFrame)."""
        try:
            self.datasource = self.context.data_sources.add_pandas(self.data_source_name)
            logger.info(f"Data source '{self.data_source_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding data source: {e}")
            raise ValueError(f"Error while adding data source: {e}")

    def add_data_asset(self):
        """Add a data asset to the data source."""
        try:
            self.data_asset = self.datasource.add_dataframe_asset(name=self.asset_name)
            self.batch_definition = self.data_asset.add_batch_definition_whole_dataframe(name="Whole Table Batch")
            logger.info(f"Data asset '{self.asset_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding data asset: {e}")
            raise ValueError(f"Error while adding data asset: {e}")

    def define_expectations(self):
        """Define expectations for the validation."""
        try:
            self.expectation_suite = self.context.suites.add(gx.ExpectationSuite(name=self.expectation_suite_name))

            # Add the passed expectations dynamically to the suite
            for expectation in self.expectations:
                self.expectation_suite.add_expectation(expectation)
                logger.info(f"Added expectation: {expectation}")

            # Save the expectation suite
            self.expectation_suite.save()
            logger.info(f"Expectation suite '{self.expectation_suite_name}' created and saved.")
        except Exception as e:
            logger.error(f"Error while defining expectations: {e}")
            raise ValueError(f"Error while defining expectations: {e}")

    def create_batch(self):
        """Create a batch from the Pandas DataFrame."""
        try:
            self.batch = self.batch_definition.get_batch(batch_parameters={'dataframe': self.df})
            logger.info(f"Batch created successfully.")
        except Exception as e:
            logger.error(f"Error while creating batch: {e}")
            raise ValueError(f"Error while creating batch: {e}")

    def validate(self):
        """Run the validation and return the result."""
        try:
            validation_result = self.batch.validate(self.expectation_suite)
            logger.info(f"Validation result: {validation_result}")
            return validation_result
        except Exception as e:
            logger.error(f"Error while running validation: {e}")
            raise ValueError(f"Error while running validation: {e}")

    def run(self):
        """Run the full validation flow."""
        self.add_data_source()
        self.add_data_asset()
        self.define_expectations()
        self.create_batch()
        return self.validate()
