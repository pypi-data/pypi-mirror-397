"""
FAIRMeta command-line interface.

This module provides the CLI entry point for generating, validating,
and publishing metadata records based on a YAML configuration and
external platform metadata sources.
"""

import argparse
import logging
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv

from fairmeta.gatherers import GrandChallenge
from fairmeta.metadata_model import MetadataRecord
from fairmeta.uploader_radboudfdp import RadboudFDPClient

load_dotenv()

def build_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Generate and publish FAIR metadata records.",
    )

    parser.add_argument(
        "config",
        help="YAML configuration file",
    )
    parser.add_argument(
        "platform",
        help="Platform to fetch metadata from",
    )
    parser.add_argument(
        "-s",
        "--slug",
        help="Unique identifier of dataset",
        action="append",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--extra-dataset",
        help="YAML files with extra dataset-specific fields",
        action="append",
        required=False,
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    # parser.add_argument(
    #     'catalog_name', 
    #     help="Name of catalog in FDP",
    # )

    return parser


def load_yaml_file(path: str | Path) -> dict:
    """Load a YAML file into a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)
    
def fetch_platform_metadata(
    platform_key: str,
    slugs: List[str],
):
    """Fetch metadata from the specified external platform.

    Args:
        platform_key: Platform identifier (lowercase).
        slugs: Dataset slugs to fetch.

    Returns:
        Platform-specific API metadata.

    Raises:
        ValueError: If the platform is unsupported.
    """
    match platform_key:
        case "grand_challenge":
            platform_client = GrandChallenge()
            return platform_client.gather_data(slugs)
        case _:
            raise ValueError(
                f"Unsupported platform: {platform_key}"
            )



def main() -> None:
    """CLI entry point for FAIRMeta."""
    parser = build_argument_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    logging.info("Loading configuration file")
    platform_key = args.platform.lower()

    config_data = load_yaml_file(args.config)
    platforms_config = config_data.get("platforms", {})

    if platform_key not in platforms_config:
        available = ", ".join(platforms_config.keys())
        raise ValueError(
            f"Platform '{platform_key}' not found in config file. "
            f"Available platforms: {available}"
        )

    platform_config = platforms_config[platform_key]

    logging.info("Fetching data from platform: %s", platform_key)
    api_data = fetch_platform_metadata(
        platform_key=platform_key,
        slugs=args.slug,
    )

    extra_dataset_configs = []
    if args.extra_dataset:
        for dataset_path in args.extra_dataset:
            extra_dataset_configs.append(
                load_yaml_file(dataset_path)
            )

    metadata_record = MetadataRecord.from_sources(
        config=platform_config,
        api_data=api_data,
        data_config=extra_dataset_configs,
    )

    logging.info("Validating relaxed metadata schema")
    metadata_record.validate()

    MetadataRecord.transform_values(metadata_record)

    logging.info("Validating strict metadata schema")
    metadata_record.validate()

    fdp_client = RadboudFDPClient(test=args.test)

    # NOTE:
    # This catalog name does not currently affect the generated TTL output.
    catalog_name = "default_catalog_name"

    fdp_client.create_and_publish(
        metadata_record,
        catalog_name,
    )

    logging.info("Done")


if __name__ == "__main__":
    main()