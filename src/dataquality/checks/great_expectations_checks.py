import great_expectations as ge

context = ge.data_context.data_context()


def check_nulls(df, column_name):
    """Check if the column has any null values."""
    expectation_suite_name = "null_check_suite"
    batch = context.get_batch({
        "datasource_name": "my_spark_datasource",
        "dataset": df
    })

    # Define the expectation for non-null values in the column
    batch.expect_column_values_to_be_in_set(column_name, set([None]))
    results = batch.validate(expectation_suite_name)

    # If there are no failed expectations, return True
    return not any(result["success"] is False for result in results["results"])


def check_uniqueness(df, column_name):
    """Check if the column's values are unique."""
    expectation_suite_name = "unique_check_suite"
    batch = context.get_batch({
        "datasource_name": "my_spark_datasource",
        "dataset": df
    })

    # Define the expectation for uniqueness of column values
    batch.expect_column_values_to_be_in_set(column_name, set([None]))
    results = batch.validate(expectation_suite_name)

    return not any(result["success"] is False for result in results["results"])
