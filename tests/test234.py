import csv
import json

# The updated input JSON data
data = {
    "ValidationResultIdentifier::AIS_suite_name/__none__/20250401T092921.526407Z/AIS_source-AIS_asset": {
        "success": True,
        "results": [
            {
                "success": True,
                "expectation_config": {
                    "type": "expect_column_values_to_be_of_type",
                    "kwargs": {
                        "batch_id": "AIS_source-AIS_asset",
                        "column": "ReceivedTimestamp",
                        "type_": "int64"
                    },
                    "meta": {},
                    "id": "30e2ccc1-0005-44ff-ac1a-85efcb082e7f"
                },
                "result": {
                    "observed_value": "int64"
                },
                "meta": {},
                "exception_info": {
                    "raised_exception": False,
                    "exception_traceback": None,
                    "exception_message": None
                }
            },
            {
                "success": True,
                "expectation_config": {
                    "type": "expect_column_values_to_be_of_type",
                    "kwargs": {
                        "batch_id": "AIS_source-AIS_asset",
                        "column": "ProcessedTimestamp",
                        "type_": "int64"
                    },
                    "meta": {},
                    "id": "4c054bb4-c9a9-41e9-86ad-fa189b346e7d"
                },
                "result": {
                    "observed_value": "int64"
                },
                "meta": {},
                "exception_info": {
                    "raised_exception": False,
                    "exception_traceback": None,
                    "exception_message": None
                }
            }
        ]
    }
}

# Flatten the data structure
flattened_data = []

# Iterate through the JSON structure
for key, value in data.items():
    for result in value["results"]:
        # Flatten each result
        flattened_row = {
            "validation_result_identifier": key,
            "success": result["success"],
            "expectation_config_type": result["expectation_config"]["type"],
            "expectation_config_kwargs_batch_id": result["expectation_config"]["kwargs"]["batch_id"],
            "expectation_config_kwargs_column": result["expectation_config"]["kwargs"]["column"],
            "expectation_config_kwargs_type": result["expectation_config"]["kwargs"]["type_"],
            "expectation_config_id": result["expectation_config"]["id"],
            "result_observed_value": result["result"]["observed_value"],
            "exception_info_raised_exception": result["exception_info"]["raised_exception"],
            "exception_info_exception_traceback": result["exception_info"]["exception_traceback"],
            "exception_info_exception_message": result["exception_info"]["exception_message"]
        }
        flattened_data.append(flattened_row)

# Write the flattened data to a CSV file
csv_filename = "/home/aumni/PycharmProjects/PythonProject/src/data/test.csv"

# Get the column headers (keys of the first row)
fieldnames = flattened_data[0].keys()


# Write to CSV
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row
    writer.writerows(flattened_data)  # Write the data rows

print(f"CSV file '{csv_filename}' has been created successfully.")