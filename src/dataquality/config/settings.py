from importlib.resources import files

CONFIG_YAML_PATH = str(files(__package__).joinpath("expectation_mapping_config.yaml"))
MAX_FILE_SIZE_MB = 50
VALID_FILE_FORMATS = ['csv', 'parquet', 'json']
# CONFIG_YAML_PATH = 'dataquality/src/config/expectation_mapping_config.yaml'
S3_REGION = 'us-east-1'
BUCKET_NAME = 'ps-test-data-platform-extracts'
DATA_QUALITY_PATH = 'data_quality/error_records'
