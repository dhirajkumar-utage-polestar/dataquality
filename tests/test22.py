
import pandas as pd

aisfused_columns = [
    "ReceivedTimestamp", "ProcessedTimestamp", "Source", "TransceiverClass", "MessageType",
    "SentenceCount", "MMSI", "RawSentences", "Error", "NavigationalStatus",
    "Latitude", "Longitude", "Course", "Heading", "Speed", "CallSign", "Destination",
    "Draught", "ETA", "IMONumber", "Name", "ShipType", "ToPort", "ToStarboard",
    "ToBow", "ToStern"
]
file_path = '../src/data/stage-ais-cleaned-data-delivery-stream-1-2025-03-27-08-14-57'

df = pd.read_csv(file_path, header=None, names=aisfused_columns, quotechar='"')

print(df.head())

df = df.astype({
    "ReceivedTimestamp": "Int64",
    "ProcessedTimestamp": "Int64",
    "Source": "object",
    "TransceiverClass": "object",
    "MessageType": "Int64",
    "SentenceCount": "Int64",
    "MMSI": "object",
    "RawSentences": "object",
    "Error": "object",
    "NavigationalStatus": "object",
    "Latitude": "float64",
    "Longitude": "float64",
    "Course": "float64",
    "Heading": "float64",
    "Speed": "float64",
    "CallSign": "object",
    "Destination": "object",
    "Draught": "float64",
    "ETA": "Int64",
    "IMONumber": "object",
    "Name": "object",
    "ShipType": "object",
    "ToPort": "Int64",
    "ToStarboard": "Int64",
    "ToBow": "Int64",
    "ToStern": "Int64"
})


