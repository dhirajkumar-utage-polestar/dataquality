import great_expectations as gx
import great_expectations.exceptions as exc
import great_expectations.expectations as gxe
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.datasource.fluent.interfaces import Datasource
import pandas as pd

#contstant
DB_CONNECTION_STRING = "postgresql+psycopg2://postgres:password@localhost:5432/demo"
TABLE_NAME = "yellow_tripdata"

DATASOURCE_NAME = "Postgres"

BATCH_DEFINITION_NAME_PARTIONED = "Partition by Month"
BATCH_DEFINITION_NAME_PARTIONED_DESC = "Partition by Month Desc"
BATCH_DEFINITION_NAME_WHOLE_TABLE = "My Batch Definition"
CHECKPOINT_NAME = "My Checkpoint"
CHECKPOINT_NAME_PARTITIONED = "My Partitioned Checkpoint"
SUITE_NAME = "Passenger Count Checker"

#-------------------------
## Context
#-------------------------


# Data Source & Asset
DATASOURCE_NAME = "testing_source"
ASSET_NAME = "testing_asset"

context = gx.get_context(mode="ephemeral") ##file
aisfused_columns = [
    "ReceivedTimestamp", "ProcessedTimestamp", "Source", "TransceiverClass", "MessageType",
    "SentenceCount", "MMSI", "RawSentences", "Error", "NavigationalStatus",
    "Latitude", "Longitude", "Course", "Heading", "Speed", "CallSign", "Destination",
    "Draught", "ETA", "IMONumber", "Name", "ShipType", "ToPort", "ToStarboard",
    "ToBow", "ToStern"
]
file_path = '/home/aumni/PycharmProjects/PythonProject/src/data/stage-ais-cleaned-data-delivery-stream-1-2025-03-27-08-14-57'
# result_csv_filename = os.path.join(result_csv_filepath,".".join([data_source_name,'csv'])

df = pd.read_csv(file_path, header=None, names=aisfused_columns, quotechar='"')
print(df.head())
datasource = context.data_sources.add_pandas(DATASOURCE_NAME)
dataasset = datasource.add_dataframe_asset(name="testing_asset")

batch_def = dataasset.add_batch_definition_whole_dataframe(name="testing Asset BAtch ")
batch = batch_def.get_batch(batch_parameters={'dataframe':df})
print("Created entities")

expectation = gxe.ExpectColumnValuesToBeOfType(column="ReceivedTimestamp", type_="int64")
validation_result = batch.validate(expectation)
print(validation_result)

