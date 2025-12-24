"""
Metadata model construction, transformation, and validation for FAIRMeta.

This module defines the MetadataRecord class, which is responsible for:
- Constructing a metadata schema from configuration files and API data
- Populating Health-RI-compatible DCAT metadata models
- Transforming values into controlled vocabularies
- Validating the resulting metadata prior to FDP upload
"""

from __future__ import annotations

import logging
import warnings
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, TypeAdapter, ValidationError
from sempyro.hri_dcat import HRIAgent, HRIVCard

from .mappings import *
from .schema_definitions_hri import Agent, Catalog, Dataset, Distribution, Kind

logger = logging.getLogger(__name__)


def _is_valid_http_url(value: str) -> bool:
    """Check whether a string is a valid HTTP URL.

    Args:
        value: String to validate.

    Returns:
        True if the string is a valid HTTP URL, False otherwise.
    """
    try:
        TypeAdapter(AnyHttpUrl).validate_python(value)
        return True
    except ValidationError:
        return False

class MetadataRecord(BaseModel):
    """Top-level metadata record for FAIRMeta.

    This class orchestrates schema construction, transformation to Health-RI
    controlled vocabularies, and validation of metadata prior to FDP upload.
    """

    catalog: Catalog
    config: Optional[Dict[str, Any]] = None
    data_configs: Optional[List[Dict[str, Any]]] = None
    api_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

    @classmethod
    def from_sources(
        cls,
        config: Optional[Dict[str, Any]] = None,
        api_data: Optional[List[Dict[str, Any]]] = None,
        data_config: Optional[List[Dict[str, Any]]] = None,
    ) -> MetadataRecord:
        """Create and populate a metadata schema instance.

        Args:
            config: Global configuration defining default metadata fields.
            api_data: Dataset-level metadata retrieved from an external API.
            data_config: Dataset-specific configuration overrides.

        Returns:
            A populated MetadataRecord instance.
        """
        schema_obj = cls.model_construct(
            config=config,
            api_data=api_data,
            data_configs=data_config,
        )

        if schema_obj.config is not None:
            cls._apply_config_defaults(schema_obj, schema_obj.config)

            if schema_obj.api_data:
                datasets = (
                    schema_obj.api_data
                    if isinstance(schema_obj.api_data, list)
                    else [schema_obj.api_data]
                )

                for dataset in datasets:
                    dataset_id = dataset.get("id")
                    dataset_config = None

                    if schema_obj.data_configs:
                        for cfg in schema_obj.data_configs:
                            if cfg.get("id") == dataset_id:
                                dataset_config = cfg
                                break

                    cls._populate_from_api(
                        schema_obj,
                        dataset,
                        schema_obj.config,
                        dataset_config=dataset_config,
                    )
        
        for dataset in schema_obj.catalog.dataset:
            valid_distributions = []
            for distribution in dataset.distribution:
                if distribution.is_complete():
                    valid_distributions.append(distribution)
                else:
                    warnings.warn(
                        f"Distribution rejected for {dataset.title}"
                    )
                
            dataset.distribution = valid_distributions
                    
        return schema_obj
    
    def transform_values(self) -> None:
        """Transform schema values into Health-RI-compliant representations."""
        self._enforce_list_types(self)
        self._normalize_vocabularies(self)
        self._agent_to_hriagent(self)
        self._kind_to_hrivcard(self)

    def validate(self) -> None:
        """Validate the metadata record.

        Ensures that required fields are present and values conform to their
        declared types.
        """
        # The _prune_none_fields function below is necessary because when
        # validating an HRIVCard or HRIAgent which has optional values that
        # are None, it gives a ValidationError
        cleaned = self._prune_none_fields(self) 
        type(self).model_validate(cleaned, strict=True)
        logger.info("Validation successful")
          
    @staticmethod
    def _apply_config_defaults(schema_obj: BaseModel, config: Dict[str, Any]) -> None:
        """Recursively fill schema fields using configuration defaults.

        Args:
            schema_obj: Metadata schema object being populated.
            config: Configuration dictionary.
        """
        try:
            for key, value in config.items():
                if isinstance(value, list):
                    if key == "keyword":
                        setattr(schema_obj, key, getattr(schema_obj, key) + value)
                    else:
                        setattr(schema_obj, key, value)
                else:
                    match key:
                        case "catalog":
                            if not hasattr(schema_obj, key):
                                setattr(schema_obj, key, Catalog.model_construct())
                            MetadataRecord._apply_config_defaults(
                                getattr(schema_obj, key), value
                            )
                        case "creator" | "publisher":
                            if not getattr(schema_obj, key, None):
                                setattr(schema_obj, key, Agent.model_construct())
                            MetadataRecord._apply_config_defaults(
                                getattr(schema_obj, key), value
                            )
                        case "contact_point":
                            if not getattr(schema_obj, key, None):
                                setattr(schema_obj, key, Kind.model_construct())
                            MetadataRecord._apply_config_defaults(
                                getattr(schema_obj, key), value
                            )
                        case "mapping" | "dataset" | "distribution":
                            continue
                        case _:
                            if value:
                                try:
                                    current = getattr(schema_obj, key)
                                    if current is not None:
                                        warnings.warn(
                                            f"Field value overwritten: {key}: "
                                            f"{current} -> {value}"
                                        )
                                except AttributeError:
                                    pass
                                setattr(schema_obj, key, value)

        except AttributeError as exc:
            raise AttributeError(
                "Invalid structure in creator, publisher, or contact_point fields"
            ) from exc

    @staticmethod
    def _populate_from_api(schema_obj, api_data: dict, config: dict, dataset_config = None):
        """Recursively fills in the fields from the api data"""
        for field, value in config.items():
            match field:
                case "catalog":
                    MetadataRecord._populate_from_api(getattr(schema_obj, field), api_data, value, dataset_config)
                case "dataset":
                    if not hasattr(schema_obj, field):
                        setattr(schema_obj, field, [])

                    new_dataset = Dataset.model_construct()
                    getattr(schema_obj, field).append(new_dataset)
                    MetadataRecord._apply_config_defaults(new_dataset, value)
                    if dataset_config:
                        MetadataRecord._apply_config_defaults(new_dataset, dataset_config["dataset"])
                    MetadataRecord._populate_from_api(new_dataset, api_data, value, dataset_config)

                case "distribution":
                    if not hasattr(schema_obj, field) or getattr(schema_obj, field) == None:
                        setattr(schema_obj, field, [])

                    new_distribution = Distribution.model_construct()
                    getattr(schema_obj, field).append(new_distribution)
                    MetadataRecord._apply_config_defaults(new_distribution, value)
                    if dataset_config:
                        distribution_exists = dataset_config["dataset"].get("distribution")
                        if distribution_exists:
                            MetadataRecord._apply_config_defaults(new_distribution, dataset_config["dataset"]["distribution"])
                    MetadataRecord._populate_from_api(new_distribution, api_data, value, dataset_config)

                case "mapping":
                    if isinstance(value, dict):
                        for api_field, internal_fields in value.items():
                            if api_field in api_data:
                                for internal_field in internal_fields:
                                    if api_data[api_field]:
                                        if internal_field == "keyword" and isinstance(schema_obj.keyword, list):
                                            setattr(schema_obj, internal_field, schema_obj.keyword + api_data[api_field]) # Not using extend here because it changes keyword in config
                                        else:
                                            setattr(schema_obj, internal_field, api_data[api_field])


    @staticmethod
    def _enforce_list_types(schema_obj: BaseModel) -> None:
        """Ensure list-typed fields are lists and scalar fields are not."""
        for field_name, field in schema_obj.model_fields.items():
            value = getattr(schema_obj, field_name)

            if isinstance(value, BaseModel):
                MetadataRecord._enforce_list_types(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, BaseModel):
                        MetadataRecord._enforce_list_types(v)

            is_list_type = "List" in str(field.annotation)

            if is_list_type and value is not None and not isinstance(value, list):
                setattr(schema_obj, field_name, [value])
            elif not is_list_type and isinstance(value, list):
                if len(value) == 1:
                    setattr(schema_obj, field_name, value[0])
                    warnings.warn(
                        f"List provided for field '{field_name}'",
                        stacklevel=2,
                    )
                else:
                    raise TypeError(
                        f"Multiple values found for field '{field_name}'"
                    )

    @staticmethod
    def _normalize_vocabularies(schema_obj: BaseModel) -> None:
        """Convert string fields to controlled vocabulary URIs."""
        for field_name in schema_obj.model_fields:
            value = getattr(schema_obj, field_name)

            if isinstance(value, BaseModel):
                MetadataRecord._normalize_vocabularies(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, BaseModel):
                        MetadataRecord._normalize_vocabularies(v)

            dict_backed = {
                "access_rights": ACCESS_RIGHTS_BY_NAME,
                "theme": DATASET_THEME_BY_NAME,
                "license": LICENSE_BY_NAME,
                "status": DATASET_STATUS_BY_NAME,
                "frequency": FREQUENCY_BY_NAME,
            }

            transformer_backed = {
                "format",
                "language",
                "legal_basis",
                "personal_data",
                "purpose",
            }

            if field_name in dict_backed and value:
                vocab = dict_backed[field_name]
                if field_name == "status" and isinstance(schema_obj, Distribution):
                    vocab = DISTRIBUTION_STATUS_BY_NAME

                if isinstance(value, list):
                    setattr(
                        schema_obj,
                        field_name,
                        [MetadataRecord._normalize_vocab_value(v, vocab) for v in value],
                    )
                else:
                    setattr(
                        schema_obj,
                        field_name,
                        MetadataRecord._normalize_vocab_value(value, vocab),
                    )

            elif field_name in transformer_backed and value:
                if isinstance(value, list):
                    setattr(
                        schema_obj,
                        field_name,
                        [
                            MetadataRecord._normalize_vocab_value(v, field_name) for v in value
                        ],
                    )
                else:
                    setattr(
                        schema_obj,
                        field_name,
                        MetadataRecord._normalize_vocab_value(value, field_name),
                    )

    @staticmethod
    def _normalize_vocab_value(value: Any, vocab: Any) -> Any:
        """Convert a value to a controlled vocabulary entry."""
        if not isinstance(value, str): # There is a bug where if there are multiple datasets, _normalize_vocab_value is called multiple times per object.
            return value
        
        if not isinstance(value, str):
            return value

        match vocab:
            case "format":
                return MetadataRecord._format_transformation(value)
            case "language":
                return MetadataRecord._language_transformation(value)
            case "legal_basis":
                return MetadataRecord._legal_basis_transformation(value)
            case "personal_data":
                return MetadataRecord._personal_data_transformation(value)
            case "purpose":
                return MetadataRecord._purpose_transformation(value)
            case _:
                try:
                    return vocab[value.lower()]
                except KeyError as exc:
                    raise ValueError(
                        f"{value} is not supported. "
                        f"Supported values: {', '.join(vocab.keys())}"
                    ) from exc        

    @staticmethod
    def _format_transformation(value: str) -> str:
        if not _is_valid_http_url(value):
            return (
                "http://publications.europa.eu/resource/authority/file-type/"
                f"{value}"
            )
        if "publications.europa.eu/resource/authority/file-type/" not in value:
            raise ValueError(
                "Format must use EU file-type authority URI"
            )
        return value

    @staticmethod
    def _language_transformation(value: str) -> str:
        if not _is_valid_http_url(value):
            match value.lower():
                case "nederlands" | "dutch" | "nld":
                    return (
                        "http://publications.europa.eu/resource/authority/language/NLD"
                    )
                case "english" | "engels" | "eng":
                    return (
                        "http://publications.europa.eu/resource/authority/language/ENG"
                    )
                case _:
                    raise ValueError(
                        "Language must be 'nld', 'eng', or an EU language URI"
                    )
        if "publications.europa.eu/resource/authority/language/" not in value:
            raise ValueError("Invalid language URI")
        return value

    @staticmethod
    def _legal_basis_transformation(value: str) -> str:
        return (
            value
            if _is_valid_http_url(value)
            else f"https://w3id.org/dpv#{value}"
        )

    @staticmethod
    def _personal_data_transformation(value: str) -> str:
        return (
            value
            if _is_valid_http_url(value)
            else f"https://w3id.org/dpv/pd#{value}"
        )

    @staticmethod
    def _purpose_transformation(value: str) -> str:
        return (
            value
            if _is_valid_http_url(value)
            else f"https://w3id.org/dpv#{value}"
        )              
                        
    @staticmethod
    def _agent_to_hriagent(schema_obj: BaseModel) -> None:
        """Convert Agent objects to HRIAgent objects."""
        for field_name in schema_obj.model_fields:
            value = getattr(schema_obj, field_name)

            if isinstance(value, Agent):
                setattr(
                    schema_obj,
                    field_name,
                    MetadataRecord._create_hriagent(value),
                )
            elif isinstance(value, list) and any(isinstance(v, Agent) for v in value):
                new_values = []
                for v in value:
                    if isinstance(v, Agent):
                        new_values.append(
                            MetadataRecord._create_hriagent(v)
                        )
                    elif isinstance(v, HRIAgent):
                        new_values.append(v)
                    elif isinstance(v, BaseModel):
                        MetadataRecord._agent_to_hriagent(v)
                        new_values.append(v)
                    else:
                        raise ValueError("Encountered not Agent or HRIAgent in list")
                setattr(schema_obj, field_name, new_values)
            elif isinstance(value, BaseModel):
                MetadataRecord._agent_to_hriagent(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, BaseModel):
                        MetadataRecord._agent_to_hriagent(v)

    @staticmethod
    def _create_hriagent(agent: Agent) -> HRIAgent:
        kwargs: Dict[str, Any] = {
            "mbox": agent.mbox,
            "identifier": agent.identifier,
            "name": agent.name,
            "homepage": agent.homepage,
        }
        for attr in (
            "spatial",
            "type",
            "publisher_type",
            "publisher_note",
        ):
            val = getattr(agent, attr)
            if val is not None:
                kwargs[attr] = val
        return HRIAgent(**kwargs)

    @staticmethod
    def _kind_to_hrivcard(schema_obj: BaseModel) -> None:
        """Convert Kind objects to HRIVCard objects."""
        for field_name in schema_obj.model_fields:
            value = getattr(schema_obj, field_name)

            if isinstance(value, Kind):
                setattr(
                    schema_obj,
                    field_name,
                    MetadataRecord._create_hrivcard(value),
                )
            elif isinstance(value, list) and any(isinstance(v, Kind) for v in value):
                new_values = []
                for v in value:
                    if isinstance(v, Kind):
                        new_values.append(
                            MetadataRecord._create_hrivcard(v)
                        )
                    elif isinstance(v, HRIVCard):
                        new_values.append(v)
                    elif isinstance(v, BaseModel):
                        MetadataRecord._kind_to_hrivcard(v)
                        new_values.append(v)
                    else:
                        raise ValueError("Encountered not Kind or VCard in list")               
                setattr(schema_obj, field_name, new_values)
            elif isinstance(value, BaseModel):
                MetadataRecord._kind_to_hrivcard(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, BaseModel):
                        MetadataRecord._kind_to_hrivcard(v)

    @staticmethod
    def _create_hrivcard(kind: Kind) -> HRIVCard:
        kwargs: Dict[str, Any] = {
            "hasEmail": kind.hasEmail,
            "formatted_name": kind.fn,
        }
        if kind.hasUrl is not None:
            kwargs["contact_page"] = kind.hasUrl
        return HRIVCard(**kwargs)
       
    @staticmethod
    def _prune_none_fields(data: Any) -> Any:
        """Remove None values from optional fields for validation."""
        if isinstance(data, BaseModel):
            result = {}
            for name, field in data.model_fields.items():
                try:
                    value = getattr(data, name)
                except:
                    raise ValueError("Likely put null or null equivalent value in required field")
                if value is not None or field.is_required():
                    result[name] = MetadataRecord._prune_none_fields(value)
            return result
        if isinstance(data, dict):
            return {
                k: MetadataRecord._prune_none_fields(v)
                for k, v in data.items()
                if v is not None
            }
        if isinstance(data, list):
            return [MetadataRecord._prune_none_fields(v) for v in data if v is not None]
        return data