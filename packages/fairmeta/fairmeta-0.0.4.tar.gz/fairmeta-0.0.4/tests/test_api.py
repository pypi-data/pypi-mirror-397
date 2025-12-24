"""
Tests for FAIRMeta API integrations.

This module contains tests for:
- The Grand Challenge gatherer
- Posting, updating, publishing, and deleting metadata in the Radboud FDP
"""

import random
import string
from typing import Any, Dict, List, Tuple, Type

import pytest
import requests
from gcapi import Client
from httpx import HTTPStatusError, Request, Response
from rdflib import Graph

import test_utils
from fairmeta.gatherers.gather_GC import GrandChallenge
from fairmeta import metadata_model


@pytest.mark.parametrize(
    "slug,status_code,expected_exception",
    [
        ("LUNA16", 200, None),
        ("weird", 404, HTTPStatusError),
    ],
)
def test_grand_challenge_gather_challenge(
    monkeypatch: pytest.MonkeyPatch,
    slug: str,
    status_code: int,
    expected_exception: Type[Exception] | None,
) -> None:
    """Test gathering challenge data from the Grand Challenge API."""

    recorded_calls: List[Tuple[str, Dict[str, Any]]] = []

    def fake_get(self, path: str, **kwargs: Any) -> Response:
        recorded_calls.append((path, kwargs))

        if status_code == 200:
            content = {"name": slug, "pk": 1}
        else:
            content = {"detail": "Not found"}

        return Response(
            status_code=status_code,
            json=content,
            request=Request(
                "GET",
                f"https://grand-challenge.org/api/v1/challenges{path}",
            ),
        )

    monkeypatch.setattr(Client, "get", fake_get)

    # -----------------------------------------------------------------
    # Fake GC client internals
    # -----------------------------------------------------------------

    class FakeArchive:
        def __init__(self) -> None:
            self.pk = 2
            self.slug = slug.lower()

    class FakeArchives:
        def detail(self, slug: str) -> FakeArchive:
            return FakeArchive()

    class FakeImages:
        def __init__(self) -> None:
            self._items = [{"id": "img1"}, {"id": "img2"}]

        def iterate_all(self, params: Dict[str, Any]):
            yield from self._items

        def list(self, params: Dict[str, Any]):
            return self._items

    def fake_init(self) -> None:
        self.client = Client(token="token")
        self.client.archives = FakeArchives()
        self.client.images = FakeImages()

    monkeypatch.setattr(
        "fairmeta.gatherers.gather_GC.GrandChallenge.__init__",
        fake_init,
    )

    platform = GrandChallenge()

    if expected_exception:
        with pytest.raises(expected_exception):
            platform._gather_challenge(slug)
    else:
        challenge_data = platform._gather_challenge(slug)

        assert recorded_calls, "Expected GC API to be called"
        assert recorded_calls[0][0].endswith(
            f"/challenges/{slug}"
        ), f"Unexpected request path: {recorded_calls[0][0]}"
        assert isinstance(challenge_data, dict)
        assert challenge_data.get("name") == slug


def test_fdp_create_publish_and_delete(
    fdp_client,
    metadata_config,
    api_data,
) -> None:
    """Test creating, publishing, and deleting metadata in the FDP."""
    schema = test_utils.build_adapted_metadata_record(
        None,
        metadata_config,
        api_data,
        None,
        None,
    )

    metadata_model.MetadataRecord.transform_values(schema)

    catalog_name = "test_catalog"
    created_urls = fdp_client.create_and_publish(schema, catalog_name)

    for url in created_urls:
        response = requests.get(url)
        assert response.status_code == 200

    # Deleting the catalog should cascade-delete all contained resources
    delete_response = fdp_client.delete(
        created_urls[0],
        confirm=False,
    )
    assert delete_response.status_code == 204


def test_fdp_update_catalog_and_dataset(
    fdp_client,
    metadata_config,
    api_data,
) -> None:
    """Test updating catalog- and dataset-level metadata."""
    catalog_url = (
        "http://localhost:8080/catalog/"
        "953d4e65-6ed7-489d-9745-f8f42811d9df"
    )
    dataset_url = (
        "http://localhost:8080/dataset/"
        "14069853-68a6-496d-85ee-d17cc53bf9ab"
    )

    schema = test_utils.build_adapted_metadata_record(
        None,
        metadata_config,
        api_data,
        None,
        None,
    )

    random_letters = string.ascii_lowercase
    new_catalog_description = "".join(
        random.choice(random_letters) for _ in range(25)
    )
    new_dataset_description = "".join(
        random.choice(random_letters) for _ in range(25)
    )

    schema.catalog.description = new_catalog_description
    schema.catalog.dataset[0].description = new_dataset_description

    metadata_model.MetadataRecord.transform_values(schema)

    fdp_client.update(
        "catalog",
        schema.catalog,
        catalog_url,
        dataset_url,
    )
    catalog_response = fdp_client.get(catalog_url)
    assert new_catalog_description in catalog_response.text

    fdp_client.update(
        "dataset",
        schema.catalog.dataset[0],
        dataset_url,
        catalog_url,
    )
    dataset_response = fdp_client.get(dataset_url)
    assert new_dataset_description in dataset_response.text