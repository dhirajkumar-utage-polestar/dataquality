import logging
from typing import List

import great_expectations.expectations as gxe
import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ExpectationMapper:
    def __init__(self, master_yaml_path: str):
        """Initialize with the path to the master YAML configuration for expectations."""
        self.master_yaml_path = master_yaml_path
        self.master_config = self.load_master_config()

    def load_master_config(self) -> dict:
        """Load the master YAML configuration for expectations."""
        with open(self.master_yaml_path, 'r') as file:
            return yaml.safe_load(file)

    def map_user_expectations(self, user_expectations: List[dict]) -> List[gxe.Expectation]:
        """Maps the user expectations from the YAML input to Great Expectations expectations."""
        mapped_expectations = []
        for user_expectation in user_expectations:
            name = user_expectation['name']
            if name in self.master_config['expectation_mapping']:
                # Get the corresponding expectation config
                expectation_config = self.master_config['expectation_mapping'][name]

                # Dynamically create the corresponding Great Expectations expectation
                if name == "ExpectColumnValuesToBeNull":
                    column = user_expectation['column']
                    mapped_expectations.append(gxe.ExpectColumnValuesToBeNull(column=column))
                    logger.info(f"Mapped expectation: {name} for column {column}")

                elif name == "ExpectColumnValuesToNotBeNull":
                    column = user_expectation['column']
                    mapped_expectations.append(gxe.ExpectColumnValuesToNotBeNull(column=column))
                    logger.info(f"Mapped expectation: {name} for column {column}")

                elif name == "ExpectColumnToExist":
                    column = user_expectation['column']
                    mapped_expectations.append(gxe.ExpectColumnToExist(column=column))
                    logger.info(f"Mapped expectation: {name} for column {column}")

                elif name == "ExpectColumnValuesToBeOfType":
                    column = user_expectation['column']
                    column_type = user_expectation['type']
                    mapped_expectations.append(gxe.ExpectColumnValuesToBeOfType(column=column, type_=column_type))
                    logger.info(f"Mapped expectation: {name} for column {column} with type {column_type}")

                elif name == "ExpectColumnValuesToBeInTypeList":
                    column = user_expectation['column']
                    type_list = user_expectation['type_list']
                    mapped_expectations.append(gxe.ExpectColumnValuesToBeInTypeList(column=column, type_list=type_list))
                    logger.info(f"Mapped expectation: {name} for column {column} with types {type_list}")

                elif name == "ExpectTableColumnCountToBeBetween":
                    min_column_count = user_expectation['min']
                    max_column_count = user_expectation['max']
                    mapped_expectations.append(gxe.ExpectTableColumnCountToBeBetween(min_column_count=min_column_count,
                                                                                     max_column_count=max_column_count))
                    logger.info(f"Mapped expectation: {name} with min: {min_column_count}, max: {max_column_count}")

                elif name == "ExpectTableColumnsToMatchOrderedList":
                    column_list = user_expectation['columns']
                    mapped_expectations.append(gxe.ExpectTableColumnsToMatchOrderedList(columns=column_list))
                    logger.info(f"Mapped expectation: {name} for columns {column_list}")

                elif name == "ExpectTableColumnsToMatchSet":
                    column_set = user_expectation['columns']
                    mapped_expectations.append(gxe.ExpectTableColumnsToMatchSet(columns=column_set))
                    logger.info(f"Mapped expectation: {name} for columns {column_set}")

                # --- Uniqueness Expectations ---
                elif name == "ExpectColumnDistinctValuesToBeInSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(
                        gxe.ExpectColumnDistinctValuesToBeInSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectColumnDistinctValuesToContainSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(
                        gxe.ExpectColumnDistinctValuesToContainSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectColumnDistinctValuesToEqualSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(
                        gxe.ExpectColumnDistinctValuesToEqualSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectColumnProportionOfUniqueValuesToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnProportionOfUniqueValuesToBeBetween(column=column, min_value=min_value,
                                                                            max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnUniqueValueCountToBeBetween":
                    column = user_expectation['column']
                    min_count = user_expectation['min']
                    max_count = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnUniqueValueCountToBeBetween(column=column, min_count=min_count,
                                                                    max_count=max_count))
                    logger.info(
                        f"Mapped expectation: {name} for column {column} with count range ({min_count}, {max_count})")

                elif name == "ExpectColumnValuesToBeUnique":
                    column = user_expectation['column']
                    mapped_expectations.append(gxe.ExpectColumnValuesToBeUnique(column=column))
                    logger.info(f"Mapped expectation: {name} for column {column}")

                elif name == "ExpectCompoundColumnsToBeUnique":
                    columns = user_expectation['columns']
                    mapped_expectations.append(gxe.ExpectCompoundColumnsToBeUnique(columns=columns))
                    logger.info(f"Mapped expectation: {name} for columns {columns}")

                elif name == "ExpectSelectColumnValuesToBeUniqueWithinRecord":
                    columns = user_expectation['columns']
                    mapped_expectations.append(gxe.ExpectSelectColumnValuesToBeUniqueWithinRecord(columns=columns))
                    logger.info(f"Mapped expectation: {name} for columns {columns}")

                # --- Validity Expectations ---
                elif name == "ExpectColumnMostCommonValueToBeInSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(
                        gxe.ExpectColumnMostCommonValueToBeInSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectColumnPairValuesToBeEqual":
                    column_A = user_expectation['column_A']
                    column_B = user_expectation['column_B']
                    mapped_expectations.append(
                        gxe.ExpectColumnPairValuesToBeEqual(column_A=column_A, column_B=column_B))
                    logger.info(f"Mapped expectation: {name} for columns {column_A}, {column_B}")

                # --- Numeric Expectations ---
                elif name == "ExpectColumnMaxToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnMaxToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnMeanToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnMeanToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnMedianToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnMedianToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnMinToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnMinToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnQuantileValuesToBeBetween":
                    column = user_expectation['column']
                    quantile_values = user_expectation['quantile_values']
                    mapped_expectations.append(
                        gxe.ExpectColumnQuantileValuesToBeBetween(column=column, quantile_values=quantile_values))
                    logger.info(f"Mapped expectation: {name} for column {column} with quantiles {quantile_values}")

                elif name == "ExpectColumnStdevToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnStdevToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnSumToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnSumToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnValueZScoresToBeLessThan":
                    column = user_expectation['column']
                    threshold = user_expectation['threshold']
                    mapped_expectations.append(
                        gxe.ExpectColumnValueZScoresToBeLessThan(column=column, threshold=threshold))
                    logger.info(f"Mapped expectation: {name} for column {column} with threshold {threshold}")

                elif name == "ExpectColumnValuesToBeBetween":
                    column = user_expectation['column']
                    min_value = user_expectation['min']
                    max_value = user_expectation['max']
                    mapped_expectations.append(
                        gxe.ExpectColumnValuesToBeBetween(column=column, min_value=min_value, max_value=max_value))
                    logger.info(f"Mapped expectation: {name} for column {column} with range ({min_value}, {max_value})")

                elif name == "ExpectColumnValuesToBeInSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(gxe.ExpectColumnValuesToBeInSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectColumnValuesToNotBeInSet":
                    column = user_expectation['column']
                    value_set = user_expectation['value_set']
                    mapped_expectations.append(gxe.ExpectColumnValuesToNotBeInSet(column=column, value_set=value_set))
                    logger.info(f"Mapped expectation: {name} for column {column} with set {value_set}")

                elif name == "ExpectMulticolumnSumToEqual":
                    columns = user_expectation['columns']
                    value = user_expectation['value']
                    mapped_expectations.append(gxe.ExpectMulticolumnSumToEqual(columns=columns, value=value))
                    logger.info(f"Mapped expectation: {name} for columns {columns} with value {value}")

                elif name == "ExpectColumnValueLengthsToBeBetween":
                    column = user_expectation.get('column')
                    min_length = user_expectation.get('min')
                    max_length = user_expectation.get('max')

                    # Check if all required keys are present
                    if column and min_length is not None and max_length is not None:
                        mapped_expectations.append(
                            gxe.ExpectColumnValueLengthsToBeBetween(column=column, min_value=min_length,
                                                                    max_value=max_length)
                        )
                        logger.info(
                            f"Mapped expectation: {name} for column {column} with length range ({min_length}, {max_length})")
                    else:
                        if not column:
                            logger.error(f"Missing 'column' for expectation: {name}")
                        if min_length is None:
                            logger.error(f"Missing 'min' for expectation: {name}")
                        if max_length is None:
                            logger.error(f"Missing 'max' for expectation: {name}")

        return mapped_expectations
