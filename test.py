import pandas as pd

from dataquality.validation_processor import ValidationProcessor

# Paths and configuration
yaml_config_path = '/home/aumni/PycharmProjects/dataquality/src/dataquality/data/testing.yaml'
invalid_file_path = '/src/dataquality/data/test.csv'

aisfused_columns = [
    "ReceivedTimestamp", "ProcessedTimestamp", "Source", "TransceiverClass", "MessageType",
    "SentenceCount", "MMSI", "RawSentences", "Error", "NavigationalStatus",
    "Latitude", "Longitude", "Course", "Heading", "Speed", "CallSign", "Destination",
    "Draught", "ETA", "IMONumber", "Name", "ShipType", "ToPort", "ToStarboard",
    "ToBow", "ToStern"
]
file_path = 'src/dataquality/data/stage-ais-cleaned-data-delivery-stream-1-2025-03-27-08-14-57'
process_id = 'ttt_DHIRAJ'
# Load data
df = pd.read_csv(file_path, header=None, names=aisfused_columns, quotechar='"')

# Run the validation processor
validation_processor = ValidationProcessor(
    file_path,  ## file to path to read
    yaml_config_path,  ## User YAML File
    df,  # dataFrame
    process_id,  ## Process for each Airflow job ,can pick the job name and pass heere
    invalid_file_path  ## where to store the Bad Records on Action of SKIP
)
valid_df = validation_processor.run()
print(valid_df.head())
