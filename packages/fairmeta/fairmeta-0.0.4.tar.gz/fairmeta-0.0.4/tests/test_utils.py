"""
Utility helpers for FAIRMeta test suite.

This module provides shared helper functions to support metadata
transformation, path resolution, and test configuration manipulation.
"""

from copy import deepcopy
from typing import Any, Dict, List, Tuple

from pydantic import AnyHttpUrl, Field
from rdflib import DCTERMS
from sempyro.hri_dcat import HRICatalog

from fairmeta.metadata_model import MetadataRecord


class FDPCatalog(HRICatalog):
    """Test-specific FDP catalog extension with `is_part_of` relation."""

    is_part_of: List[AnyHttpUrl] = Field(
        description="Link to parent object",
        json_schema_extra={
            "rdf_term": DCTERMS.isPartOf,
            "rdf_type": "uri",
        },
    )


def merge_nested_dicts(
    base: Dict[str, Any],
    extension: Dict[str, Any],
) -> Dict[str, Any]:
    """Recursively merge one nested dictionary into another.

    Values in `extension` override or extend values in `base`.

    Args:
        base: Base dictionary to be extended.
        extension: Dictionary containing new or overriding values.

    Returns:
        The updated base dictionary.
    """
    for key, value in extension.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            merge_nested_dicts(base[key], value)
        else:
            base[key] = value
    return base


def find_metadata_path(
    metadata_config: Dict[str, Any],
    field_key: str,
) -> List[str]:
    """Find the nested metadata path for a mapped API field.

    Args:
        metadata_config: Metadata configuration dictionary.
        field_key: API field key to resolve.

    Returns:
        A list representing the attribute path in the metadata model.
    """
    for key, value in metadata_config.items():
        if key == "mapping" and field_key in value:
            return [value[field_key][0]]

        if isinstance(value, dict):
            sub_path = find_metadata_path(value, field_key)
            if sub_path:
                return [key] + sub_path

    return []


def resolve_metadata_value(
    root_obj: Any,
    path: List[str],
    source: str,
    metadata_config: Dict[str, Any],
):
    """Resolve a value from either metadata config or API data.

    Args:
        root_obj: Root object to traverse.
        path: Attribute path to resolve.
        source: Either `"metadata_config"` or `"api_data"`.
        metadata_config: Metadata configuration dictionary.

    Returns:
        Resolved value (and path when resolving from API data).

    Raises:
        ValueError: If source is invalid.
    """
    if source == "metadata_config":
        for key in path:
            root_obj = getattr(root_obj, key)
            if isinstance(root_obj, list):
                root_obj = root_obj[0]
        return root_obj

    if source == "api_data":
        api_key = path[0]
        internal_path = find_metadata_path(metadata_config, api_key)

        for key in internal_path[:-1]:
            root_obj = getattr(root_obj, key)
            if isinstance(root_obj, list):
                root_obj = root_obj[0]

        value = getattr(root_obj, internal_path[-1])
        return value, internal_path

    raise ValueError(f"Unknown source: {source}")


def build_adapted_metadata_record(
    target: str | None,
    metadata_config: Dict[str, Any],
    api_data: Dict[str, Any],
    path: List[str] | None,
    value: Any | None,
    extra_metadata_configs: List[Dict[str, Any]] | None = None,
) -> MetadataRecord:
    """Create a MetadataRecord with modified metadata or API data.

    Args:
        target: Target source to modify ("metadata_config", "api_data",
            "multi_conf", or None).
        metadata_config: Metadata configuration dictionary.
        api_data: API input data.
        path: Path to the field to modify.
        value: New value to assign.
        extra_metadata_configs: Optional additional metadata configs.

    Returns:
        A constructed MetadataRecord instance.
    """
    if target == "multi_conf":
        return MetadataRecord.from_sources(
            metadata_config,
            api_data,
            data_config=extra_metadata_configs,
        )

    if target == "metadata_config":
        adapted_config = deepcopy(metadata_config)
        data_to_modify = adapted_config
    elif target == "api_data":
        adapted_api_data = deepcopy(api_data)
        data_to_modify = adapted_api_data
    else:
        return MetadataRecord.from_sources(metadata_config, api_data)

    for key in path[:-1]:
        data_to_modify = data_to_modify[key]

    data_to_modify[path[-1]] = value

    if target == "metadata_config":
        return MetadataRecord.from_sources(adapted_config, api_data)

    return MetadataRecord.from_sources(metadata_config, adapted_api_data)


def is_list_field(
    model: MetadataRecord,
    path: List[str],
) -> bool:
    """Determine whether a model field is annotated as a list.

    Args:
        model: MetadataRecord instance.
        path: Attribute path to inspect.

    Returns:
        True if the field is a list, False otherwise.
    """
    for key in path[:-1]:
        model = getattr(model, key)
        if isinstance(model, list):
            model = model[0]

    field_info = model.__class__.model_fields[path[-1]]
    return "List" in str(field_info.annotation)
