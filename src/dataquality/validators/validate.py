import datetime
import logging
import uuid
from typing import List

import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd
from great_expectations import RunIdentifier

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from importlib.resources import files
from pathlib import Path


class DataValidator:
    def __init__(self,
                 dataframe: pd.DataFrame,
                 data_source_name: str = "DEFAULT_SOURCE_NAME",
                 data_asset_name: str = "DEFAULT_ASSET_NAME",
                 expectation_suite_name: str = "DEFAULT_SUITE_NAME",
                 checkpoint_name: str = "DEFAULT_CHECKPOINT_NAME",
                 validation_definition_name: str = "DEFAULT_VALIDATION_NAME",
                 docs_build_action: bool = False,
                 site_name: str = "DEFAULT_SITE_NAME"):
        # Store the context, dataframe, and names
        # self.context = gx.get_context(context_root_dir="gx")

        self.gx_config_path = Path(str(files("dataquality.gx")))
        self.gx_config_path_str = str(self.gx_config_path).split("'", 2)[1]
        self.context = gx.get_context(
            context_root_dir=self.gx_config_path_str)  # "/home/aumni/.cache/pypoetry/virtualenvs/testing--4ivKCBK-py3.11/lib/python3.11/site-packages/dataquality/gx")

        # Data Docs setup
        # site_config = {
        #     "class_name": "SiteBuilder",
        #     "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
        #     "store_backend": {
        #         "class_name": "TupleFilesystemStoreBackend",
        #         "base_directory": "uncommitted/data_docs/pole_star/",
        #     },
        # }

        site_config = {
            "class_name": "SiteBuilder",
            "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
            "store_backend": {
                "class_name": "TupleS3StoreBackend",
                "bucket": "ps-test-data-platform-extracts",
                "prefix": "dataquality/uncommitted/"
            },
        }
        # Create or update the data docs site once

        # if docs_build_action:
        #     self.context.add_data_docs_site(site_name="pole_star", site_config=site_config)
        #     logger.info(f"Data docs site '{site_name}' created/updated.")

        ##
        self.df = dataframe
        self.data_source_name = data_source_name
        self.data_asset_name = data_asset_name
        self.expectation_suite_name = expectation_suite_name
        self.checkpoint_name = checkpoint_name
        self.validation_definition_name = validation_definition_name
        self.docs_build_action = docs_build_action
        self.site_name = site_name

        self.data_source = None
        self.data_asset = None
        self.expectation_suite = None
        self.validation_definition = None
        self.checkpoint = None

    def add_data_source(self) -> None:
        """Adds a pandas data source."""
        try:
            self.data_source = self.context.data_sources.add_or_update_pandas(name=self.data_source_name)
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
        self.expectation_suite = self.context.suites.add_or_update(
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
            self.validation_definition = self.context.validation_definitions.add_or_update(
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
            #  Related to Data Docs
            # base_directory = "uncommitted/data_docs/local_site/"  # this is the default path (relative to the root folder of the Data Context) but can be changed as required
            # """site_config = {
            #    "class_name": "SiteBuilder",
            #    "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
            #    "store_backend": {
            #        "class_name": "TupleFilesystemStoreBackend",
            #        "base_directory": base_directory,
            #    },
            # } """
            site_config = {
                "class_name": "SiteBuilder",
                "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
                "store_backend": {
                    "class_name": "TupleS3StoreBackend",
                    "bucket": "ps-test-data-platform-extracts",
                    "prefix": "dataquality"
                },
            }

            if self.docs_build_action:
                site_name_new = "pole_star_data_quality"
                name_s = "update"
                site_name_update = '_'.join([name_s, site_name_new])
                actions = [
                    gx.checkpoint.actions.UpdateDataDocsAction(
                        name=site_name_update
                    )
                ]
                self.checkpoint = self.context.checkpoints.add_or_update(
                    gx.Checkpoint(
                        name=self.checkpoint_name,
                        validation_definitions=[self.validation_definition],
                        result_format={
                            "result_format": "COMPLETE",
                            "unexpected_index_column_names": [],

                        },
                        actions=actions,

                    )
                )
                logger.info(f"Checkpoint '{self.checkpoint_name}' added successfully.")

            else:
                self.checkpoint = self.context.checkpoints.add_or_update(
                    gx.Checkpoint(
                        name=self.checkpoint_name,
                        validation_definitions=[self.validation_definition],
                        result_format={
                            "result_format": "COMPLETE",

                        },
                    )
                )
                logger.info(f"Checkpoint '{self.checkpoint_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error while adding checkpoint: {e}")
            raise ValueError(f"Error while adding checkpoint: {e}")

        # site_name = "my_data_docs_site_new"
        # self.context.add_data_docs_site(site_name=site_name, site_config=site_config)
        self.context.build_data_docs()

    def run_validation(self) -> gx.checkpoint.checkpoint.CheckpointResult:
        """Runs the validation and returns the checkpoint result."""
        try:
            run_name = uuid.uuid4()
            custom_run_id = RunIdentifier(
                run_name=str(run_name),
                run_time=datetime.datetime.now()
            )

            result = self.checkpoint.run(batch_parameters={"dataframe": self.df}, run_id=custom_run_id)
            logger.info(f"Validation run successful.")
            # if self.docs_build_action:
            #    self.context.build_data_docs(site_names=[self.site_name])  # Explicitly build data docs
            #    logger.info(f"Data Docs built for site: {self.site_name}")
            return result
        except Exception as e:
            logger.error(f"Error while running validation: {e}")
            raise ValueError(f"Error while running validation: {e}")

    def validate(self, expectations: List[gxe.Expectation]) -> gx.checkpoint.checkpoint.CheckpointResult:
        """Complete flow for adding data source, asset, expectations, and validation."""
        self.add_data_source()
        self.add_data_asset()
        self.add_expectations(expectations)  # expectation --dhiraj
        self.add_validation_definition()
        self.add_checkpoint()

        return self.run_validation(), self.context
