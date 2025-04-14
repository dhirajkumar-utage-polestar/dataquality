import logging
from typing import List
import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataValidator:
    def __init__(self,
                 dataframe: pd.DataFrame,
                 data_source_name: str = "pandas",
                 data_asset_name: str = "product categories",
                 expectation_suite_name: str = "product category expectations",
                 checkpoint_name: str = "product category checkpoint",
                 validation_definition_name: str = "product category validation definition"):
        # Store the context, dataframe, and names
        self.context = gx.get_context(mode="ephemeral")
        self.df = dataframe
        self.data_source_name = data_source_name
        self.data_asset_name = data_asset_name
        self.expectation_suite_name = expectation_suite_name
        self.checkpoint_name = checkpoint_name
        self.validation_definition_name = validation_definition_name

        # Initialize internal variables
        self.data_source = None
        self.data_asset = None
        self.expectation_suite = None
        self.validation_definition = None
        self.checkpoint = None

    def add_data_source(self) -> None:
        """Adds a pandas data source."""
        try:
            self.data_source = self.context.data_sources.add_pandas(name=self.data_source_name)
            logger.info(f"Data source '{self.data_source_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding data source: {e}")
            raise ValueError(f"Error while adding data source: {e}")

    def add_data_asset(self) -> None:
        """Adds a pandas data asset."""
        try:
            self.data_asset = self.data_source.add_dataframe_asset(name=self.data_asset_name)
            self.batch_definition = self.data_asset.add_batch_definition_whole_dataframe("test")
            logger.info(f"Data asset '{self.data_asset_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding data asset: {e}")
            raise ValueError(f"Error while adding data asset: {e}")

    def add_expectations(self, expectations: List[gxe.Expectation]) -> None:
        """Defines and adds expectations to the suite dynamically."""
        self.expectation_suite = self.context.suites.add(
            gx.ExpectationSuite(name=self.expectation_suite_name)
        )

        # Add the expectations dynamically from the passed list
        for expectation in expectations:
            self.expectation_suite.add_expectation(expectation)
            logger.info(f"Added expectation: {expectation}")

        # Save the expectation suite after modifications
        try:
            self.expectation_suite.save()
            logger.info(f"Expectation suite '{self.expectation_suite_name}' saved successfully.")
        except Exception as e:
            logger.error(f"Error saving ExpectationSuite: {e}")
            raise ValueError(f"Error saving ExpectationSuite: {e}")

        # Explicitly reload the suite to ensure changes are persisted
        self.expectation_suite = self.context.suites.get(self.expectation_suite_name)
        logger.info(f"Expectation suite '{self.expectation_suite_name}' reloaded successfully.")

    def add_validation_definition(self) -> None:
        """Defines the validation configuration."""
        try:
            self.validation_definition = self.context.validation_definitions.add(
                gx.ValidationDefinition(
                    name=self.validation_definition_name,
                    data=self.batch_definition,
                    suite=self.expectation_suite,
                )
            )
            logger.info(f"Validation definition '{self.validation_definition_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding validation definition: {e}")
            raise ValueError(f"Error while adding validation definition: {e}")

    def add_checkpoint(self) -> None:
        """Adds a checkpoint to run validation."""
        try:
            self.checkpoint = self.context.checkpoints.add(
                gx.Checkpoint(
                    name=self.checkpoint_name,
                    validation_definitions=[self.validation_definition],
                    result_format={
                        "result_format": "COMPLETE",
                        "unexpected_index_column_names": ["product_category_id"],
                    },
                )
            )
            logger.info(f"Checkpoint '{self.checkpoint_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding checkpoint: {e}")
            raise ValueError(f"Error while adding checkpoint: {e}")

    def run_validation(self) -> gx.checkpoint.checkpoint.CheckpointResult:
        """Runs the validation and returns the checkpoint result."""
        try:
            result = self.checkpoint.run(batch_parameters={"dataframe": self.df})
            logger.info(f"Validation run successful.")
            return result
        except Exception as e:
            logger.error(f"Error while running validation: {e}")
            raise ValueError(f"Error while running validation: {e}")

    def validate(self, expectations: List[gxe.Expectation]) -> gx.checkpoint.checkpoint.CheckpointResult:
        """Complete flow for adding data source, asset, expectations, and validation."""
        self.add_data_source()
        self.add_data_asset()
        self.add_expectations(expectations)  # Pass expectations here
        self.add_validation_definition()
        self.add_checkpoint()
        return self.run_validation()


# Example usage:
df = pd.read_csv("/src/data/products.csv")


# Example list of expectations
expectations = [
    gxe.ExpectColumnValuesToBeInSet(column="product_category_id", value_set={1, 2, 3}),
    gxe.ExpectColumnValuesToBeInSet(column="name", value_set={"electronics", "clothing", "books"})
]

validator = DataValidator(df)
result = validator.validate(expectations)

# Print the validation result
print(result)
