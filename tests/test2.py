import great_expectations as gx
from great_expectations import exceptions as exc
import  pandas as pd

try:
    df = pd.read_csv("/src/data/avocado.csv")
    #context

    print(df.head())
    context = gx.get_context(mode='ephemeral')

    #data Source
    datasource = context.data_sources.add_pandas("test")

    #data Asset
    data_asset = datasource.add_dataframe_asset(name= "testing_asset")

    # Batch def
    batch_definition = data_asset.add_batch_definition_whole_dataframe(name="batch_def")

     #get Batch
    batch = batch_definition.get_batch()

    suite = context.suites.add(
        gx.core.expectation_suite.ExpectationSuite(name="expectations")
    )
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="Date"))
    suite.add_expectation(gx.expectations.ExpectColumnMinToBeBetween(column="Total Volume", min_value=1, max_value=5))

    # Create Validation Definition.
    validation_definition = context.validation_definitions.add(
        gx.core.validation_definition.ValidationDefinition(
            name="validation definition",
            data=batch_definition,
            suite=suite,
        )
    )

    # Create Checkpoint, run Checkpoint, and capture result.
    checkpoint = context.checkpoints.add(
        gx.checkpoint.checkpoint.Checkpoint(
            name="checkpoint", validation_definitions=[validation_definition]
        )
    )
    print(context.get_available_data_asset_names())

    checkpoint_result = checkpoint.run()
    print(checkpoint_result.describe())
    validation_result = validation_definition.run(batch_parameters={"dataframe": df})
    print(validation_result)
except:
    pass
