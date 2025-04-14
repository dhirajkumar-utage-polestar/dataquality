
import pathlib
from typing import Tuple

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

DATA_SOURCE_NAME = "pandas"

# Define short name types to keep function type hints cleaner.
GxDataContext = gx.data_context.data_context.ephemeral_data_context
GxValidationResult = (
    gx.core.expectation_validation_result.ExpectationSuiteValidationResult
)
GxCheckpointResult = gx.checkpoint.checkpoint.CheckpointResult
context = gx.get_context(mode="ephemeral")
def validate_data(
    context: GxDataContext, df: pd.DataFrame
) -> GxValidationResult:

    data_source = context.data_sources.add_pandas(name=DATA_SOURCE_NAME)

    data_asset = data_source.add_dataframe_asset(name="product categories")
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        "product category batch definition"
    )

    expectation_suite = context.suites.add(
        gx.ExpectationSuite(name="product category expectations")
    )

    expectations = [
        gxe.ExpectTableColumnsToMatchOrderedList(
            column_list=["product_category_id", "name"]
        )
    ]

    for expectation in expectations:
        expectation_suite.add_expectation(expectation)

    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            name="product category validation definition",
            data=batch_definition,
            suite=expectation_suite,
        )
    )

    checkpoint = context.checkpoints.add(
        gx.Checkpoint(
            name="product category checkpoint",
            validation_definitions=[validation_definition],
            result_format={
                "result_format": "COMPLETE",
                "unexpected_index_column_names": ["product_category_id"],
            },
        )
    )

    checkpoint_result = checkpoint.run(batch_parameters={"dataframe": df})

    return checkpoint_result


df = pd.read_csv("/src/data/products.csv")

print(validate_data(context ,df))