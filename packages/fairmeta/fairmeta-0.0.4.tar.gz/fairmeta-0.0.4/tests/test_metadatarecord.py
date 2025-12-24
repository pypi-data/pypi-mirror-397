"""
Unit tests for the MetadataRecord model.

This module validates schema construction, value normalization,
type enforcement, vocabulary normalization, and transformation to
HRI-compliant models.
"""

import pytest
from pydantic import ValidationError
from rdflib import URIRef
from sempyro.geo import Location
from sempyro.hri_dcat import HRIAgent, HRIVCard, HRIDataset, HRIDistribution

from fairmeta import metadata_model, schema_definitions_hri
from fairmeta.metadata_model import MetadataRecord
from test_utils import (
    FDPCatalog,
    build_adapted_metadata_record,
    is_list_field,
    resolve_metadata_value,
)

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception",
    [
        (None, None, None, None),  # Minimal record
        ("metadata_config", ("catalog", "dataset", "contact_point"), "invalid", AttributeError),
        ("metadata_config", ("catalog", "publisher"), "invalid", AttributeError),
        ("metadata_config", ("catalog", "contact_point", "fn"), "", ValueError),
        ("api_data", ("challenge_title",), [], ValueError),
        ("metadata_config", ("catalog", "dataset", "contact_point", "fn"), 'quoted "string"', None),
        ("metadata_config", ("catalog", "homepage"), "", None),
        ("metadata_config", ("catalog", "contact_point", "hasEmail"), "mailto:email@org.org", None),
    ],
)
def test_metadata_record_creation(
    target_source,
    metadata_config,
    api_data,
    path,
    value,
    expected_exception,
):
    """Test creation and validation of MetadataRecord instances."""
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            schema = build_adapted_metadata_record(
                target_source, metadata_config, api_data, path, value
            )
            schema.validate()
            match target_source:
                case "metadata_config":
                    target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
                    target = getattr(target, path[-1])
                case "api_data":
                    target, _ = resolve_metadata_value(schema, path, target_source, metadata_config)
                case _:
                    pass       
            if value:
                assert target == value         
        print(exc_info) 
    else:
        schema = build_adapted_metadata_record(
            target_source, metadata_config, api_data, path, value
        )
        assert isinstance(schema, MetadataRecord)
        combined_keywords = (
            metadata_config["catalog"]["dataset"]["keyword"]
            + api_data["challenge_keywords"]
        )
        assert schema.catalog.dataset[0].keyword == combined_keywords
        match target_source:
            case "metadata_config":
                target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
                target = getattr(target, path[-1])
                assert schema.api_data == api_data
            case "api_data":
                target, _ = resolve_metadata_value(schema, path, target_source, metadata_config)
                assert schema.config == metadata_config
            case _:
                assert schema.config == metadata_config
                assert schema.api_data == api_data
        if value:
            assert target == value
        schema.validate()

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception",
    [
        ("metadata_config", ("catalog", "contact_point", "fn"), 123, ValidationError),
        ("metadata_config", ("catalog", "contact_point", "fn"), True, ValidationError),
        ("metadata_config", ("catalog", "contact_point", "fn"), None, ValueError),
        ("metadata_config", ("catalog", "contact_point", "fn"), "Firstname Lastname", None),
        ("api_data", ("archive_title",), 123, ValidationError),
        ("api_data", ("archive_title",), "title", None),
    ],
)
def test_field_type_validation(
    target_source,
    metadata_config,
    api_data,
    path,
    value,
    expected_exception,
):
    """Test enforcement of basic field types."""
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            schema.validate() # Bad error: if type is ambigious (Kind | HRIVCard for example) it prints errors for both
        print(exc_info)
    else:
        schema.validate()

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception,expected_message",
    [
        ("metadata_config", ("catalog", "dataset", "theme"), ["HEAL"], None, None),
        ("metadata_config", ("catalog", "dataset", "theme"), ["INVALID_THEME"], ValueError, f"INVALID_THEME is not supported. Supported values: {', '.join(metadata_model.DATASET_THEME_BY_NAME.keys())}"),
        ("metadata_config", ("catalog", "dataset", "access_rights"), "public", None, None),
        ("metadata_config", ("catalog", "dataset", "access_rights"), "NOT_ALLOWED", ValueError, f"NOT_ALLOWED is not supported. Supported values: {', '.join(metadata_model.ACCESS_RIGHTS_BY_NAME.keys())}"),
        ("metadata_config", ("catalog", "dataset", "theme"), "HEAL", None, None),
        ("metadata_config", ("catalog", "dataset", "theme"), "BAD", ValueError, None),
        ("metadata_config", ("catalog", "language"), "Eng", None, None),
        ("metadata_config", ("catalog", "language"), "En", ValueError, None),
        ("metadata_config", ("catalog", "language"), "https://example.com", ValueError, None),
        ("metadata_config", ("catalog", "language"), "http://publications.europa.eu/resource/authority/language/anything", None, None), # Not correct but shouldn't raise error
        ("metadata_config", ("catalog", "dataset", "frequency"), "quarterly", None, None),
        ("metadata_config", ("catalog", "dataset", "frequency"), "dagelijks", ValueError, None),
        ("metadata_config", ("catalog", "license"), "cc_byncsa_30", None, None),
        ("metadata_config", ("catalog", "license"), "Apache-2.0", ValueError, None),
        ("metadata_config", ("catalog", "dataset", "distribution", "status"), "develoP", None, None),
        ("metadata_config", ("catalog", "dataset", "distribution", "status"), "asfd", ValueError, None)
    ],
)
def test_vocabulary_normalization(
    target_source,
    metadata_config,
    api_data,
    path,
    value,
    expected_exception,
    expected_message,
):
    """Test normalization of controlled vocabulary fields."""
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    if expected_exception:
        if expected_message:
            with pytest.raises(expected_exception, match=expected_message):
                MetadataRecord._normalize_vocabularies(schema)
        else:
            with pytest.raises(expected_exception) as exc_info:
                MetadataRecord._normalize_vocabularies(schema) # Prints good error
            print(exc_info)
    else:
        MetadataRecord._normalize_vocabularies(schema)

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception",
    [
        ("metadata_config", ("catalog", "contact_point", "hasEmail"), "name", ValueError),
        ("metadata_config", ("catalog", "contact_point", "hasEmail"), "email@org.com", None),
        ("metadata_config", ("catalog", "dataset", "contact_point", "fn"), "anyone", None),
        ("metadata_config", ("catalog", "dataset", "contact_point", "hasUrl"), ["https://example.com"], None),
        ("metadata_config", ("catalog", "contact_point", "hasUrl"), ["no url"], ValueError),
        ("metadata_config", ("catalog", "contact_point", "hasUrl"), None, None),
        ("metadata_config", ("catalog", "contact_point"), [schema_definitions_hri.Kind(hasEmail="email@email.com", fn="name"), HRIVCard(hasEmail="email@email.com", formatted_name="name")], None),
        ("metadata_config", ("catalog", "contact_point"), [schema_definitions_hri.Kind(hasEmail="email@email.com", fn="name"), HRIVCard(hasEmail="email@email.com", formatted_name="name"), "random"], ValueError)
    ],
)
def test_kind_to_hrivcard_transformation(
    target_source,
    metadata_config,
    api_data,
    path,
    value,
    expected_exception,
):
    """Test conversion from Kind to HRIVCard."""
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            MetadataRecord._kind_to_hrivcard(schema) # Prints good error
        print(exc_info)
    else:
        MetadataRecord._kind_to_hrivcard(schema)
        target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
        try:
            assert isinstance(target, HRIVCard)
        except:
            target = getattr(target, path[-1])
            assert all(isinstance(t, HRIVCard) for t in target)

        if path[-1] == "hasUrl" and value is not None:
            if isinstance(target, list):
                for t in target:
                    assert t.contact_page is not None
            else:
                assert target.contact_page is not None

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception",
    [
        ("metadata_config", ("catalog", "publisher", "mbox"), "name", ValueError), # No email in mailbox
        ("metadata_config", ("catalog", "publisher", "homepage"), "no link", ValueError), # No link in homepage
        ("metadata_config", ("catalog", "dataset", "creator", "type"), "typen", ValueError), # No link in type
        ("metadata_config", ("catalog", "dataset", "creator", "type"), "https://typen.com", None),
        ("metadata_config", ("catalog", "dataset", "creator", "spatial"), ["https://Nijmegen.com"], None),
        ("metadata_config", ("catalog", "dataset", "creator", "spatial"), ["Nijmegen"], ValueError), # No link in location
        ("metadata_config", ("catalog", "dataset", "creator", "spatial"), [Location(geometry="https://Nijmegen.com")], None),                                                    
        ("metadata_config", ("catalog", "publisher", "identifier"), ["identification"], None),
        ("metadata_config", ("catalog", "publisher", "publisher_type"), None, None),
        ("metadata_config", ("catalog", "dataset", "publisher", "publisher_type"), "https://publishertype.com", None),
        ("metadata_config", ("catalog", "dataset", "publisher", "publisher_type"), ["https://publishertype.com"], ValueError), # Publisher type in a list when it's not supposed to be
        ("metadata_config", ("catalog", "publisher"), [metadata_model.Agent(mbox="dummy@email.com",identifier=["id"],name=["name"],homepage="https://pagina.nl"), HRIAgent(name=["name"],identifier=["id"],mbox="email@email.com",homepage="https://pagina.nl")], None),
        ("metadata_config", ("catalog", "publisher"), [metadata_model.Agent(mbox="dummy@email.com",identifier=["id"],name=["name"],homepage="https://pagina.nl"), HRIAgent(name=["name"],identifier=["id"],mbox="email@email.com",homepage="https://pagina.nl"), "random"], ValueError), # Not Agent in list
        ],
    ) 
def test_agent_to_hriagent_transformation(
    target_source,
    metadata_config,
    api_data,
    path,
    value,
    expected_exception,
):
    """Test conversion from Agent to HRIAgent."""
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    if expected_exception:
        with pytest.raises(expected_exception) as exc_info:
            MetadataRecord._agent_to_hriagent(schema) # Prints good error
        print(exc_info)
    else:
        MetadataRecord._agent_to_hriagent(schema)
        target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
        try:
            assert isinstance(target, HRIAgent) 
        except:
            target = getattr(target, path[-1])
            assert all(isinstance(t, HRIAgent) for t in target)

        if path[-1] == "type":
            assert target.type is not None
        elif path[-1] == "spatial":
            assert target.spatial is not None

@pytest.mark.parametrize(
    "target_source,path,value,expected_exception",
    [
        (None, None, None, None),
    ],
)
def test_transformation_hri(
    target_source, 
    metadata_config, 
    api_data, 
    path, 
    value, 
    expected_exception,
):
    """Test transformation from MetadataRecord to HRI-compatible objects."""
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    schema.transform_values()
    disallowed_fields = {"distribution", "dataset"}
    filtered_fields = {k: v for k, v in vars(schema.catalog).items() if k not in disallowed_fields and v is not None}
    catalog = FDPCatalog(
        is_part_of=[URIRef("https://test.com")],
        dataset=[],
        **filtered_fields)
    for dataset in schema.catalog.dataset:
        filtered_fields = {k: v for k, v in vars(dataset).items() if k not in disallowed_fields and v is not None}
        hri_dataset = HRIDataset(
            **filtered_fields
        )
        for distribution in dataset.distribution:
            filtered_fields = {k: v for k, v in vars(distribution).items() if k not in disallowed_fields and v is not None}
            hri_distribution = HRIDistribution(
                **filtered_fields
            )            

@pytest.mark.parametrize("target_source,path,value,expected_exception,message",
    [
        ("api_data", (["challenge_title"]), None, ValueError, "Likely put null or null equivalent value in required field"),
        ("api_data", (["challenge_title"]), "title", None, None),
        ("metadata_config", ("catalog", "license"), None, None, None),
        ("metadata_config", ("catalog", "license"), "cc0", None, None),
        ("metadata_config", ("catalog", "dataset", "contact_point", "fn"), None, ValueError, "Likely put null or null equivalent value in required field"),
        ("metadata_config", ("catalog", "contact_point", "fn"), "", ValueError, None),
        ("api_data", (["challenge_title"]), [], ValueError, "Likely put null or null equivalent value in required field"),
        ("metadata_config", ("catalog", "license"), "", None, None)
    ],
)
def test_prune_none_fields(
    target_source, 
    metadata_config, 
    api_data, 
    path, 
    value, 
    expected_exception, 
    message
):
    """Tests if drop_none function removes null-equivalent values and doesn't interfere with validation function"""
    schema = build_adapted_metadata_record(target_source, metadata_config, api_data, path, value)
    if expected_exception:
        if message:
            with pytest.raises(expected_exception, match=message):
                schema.validate()
        else:
            with pytest.raises(expected_exception) as exc_info:
                schema.validate() # Good error
            print(exc_info)
    else:
        schema.validate()
        match target_source:
            case "metadata_config":
                target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
                target = getattr(target, path[-1])
            case "api_data":
                target, _ = resolve_metadata_value(schema, path, target_source, metadata_config)
            case _:
                pass       
        if value:
            assert target == value
        else:
            assert target == None

@pytest.mark.parametrize(
    "target_source,path,value,exception,message",
    [
        ("metadata_config", ("catalog", "dataset", "applicable_legislation"), "legislature", None, None),
        ("metadata_config", ("catalog", "dataset", "applicable_legislation"), ["https://license.com"], None, None),
        ("metadata_config", ("catalog", "dataset", "purpose"), None, None, None),
        ("metadata_config", ("catalog", "dataset", "purpose"), "purposefield", None, None),
        ("metadata_config", ("catalog", "dataset", "purpose"), ["purpose field", "purpose_2"], None, None),
        ("api_data", (["challenge_url"]), ["idee"], None, None), # Warning?
        ("api_data", (["challenge_url"]), ["idee2", "illegal_id"], TypeError, "Multiple values found for field 'identifier'")
    ],
)
def test_enforce_list_types(
    target_source, 
    metadata_config, 
    api_data, 
    path, 
    value, 
    exception, 
    message,
):  
    """Tests the function that creates lists where it needs to be, and removes lists where they don't need to be"""  
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value
    )
    if exception:
        if message:
            with pytest.raises(exception, match=message):
                MetadataRecord._enforce_list_types(schema)
        else:
            with pytest.raises(exception) as exc_info:
                MetadataRecord._enforce_list_types(schema) # Prints good error
            print(exc_info)
    else:
        MetadataRecord._enforce_list_types(schema)
        match target_source:
            case "metadata_config":
                target = resolve_metadata_value(schema, path[:-1], target_source, metadata_config)
                target = getattr(target, path[-1])
                list_type = is_list_field(schema, path)
            case "api_data":
                target, internal_path = resolve_metadata_value(schema, path, target_source, metadata_config)
                list_type = is_list_field(schema, internal_path)
            case _:
                pass
        if list_type and value is not None:
            assert isinstance(target, list)
        else:
            assert not isinstance(target, list)

@pytest.mark.parametrize(
    "target_source,path,value",
    [
        ("multi_conf", None, None)
    ],
)
def test_extra_datasets(
    target_source, 
    metadata_config, 
    api_data, 
    path, 
    value, 
    extra_api_data, 
    extra_dataset_expansion_config, 
    dataset_expansion_config,
):
    """Tests if multiple metadata_config files are handled correctly"""
    api_data = [api_data, extra_api_data]
    extra_metadata_config = [extra_dataset_expansion_config, dataset_expansion_config]
    schema = build_adapted_metadata_record(
        target_source, metadata_config, api_data, path, value, extra_metadata_configs=extra_metadata_config
    )
    assert schema.catalog.dataset[0].keyword == ["Test platform", "CT", "Prostate", "Medical", "keyword2"]
    assert schema.catalog.dataset[0].maximum_typical_age == extra_metadata_config[0]["dataset"]["maximum_typical_age"]