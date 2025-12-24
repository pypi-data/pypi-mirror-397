"""
Client for interacting with the Radboud FAIR Data Point (FDP).

This module provides functionality to create, update, publish, and delete
DCAT-HRI compliant metadata records in the Radboud FDP.
"""

import logging
import os
from typing import List

import requests
from pydantic import AnyHttpUrl, Field
from rdflib import DCTERMS, URIRef
from sempyro.hri_dcat import HRICatalog, HRIDataset, HRIDistribution
from urllib.parse import urljoin, urlparse, urlunparse

from .metadata_model import MetadataRecord


class FDPCatalog(HRICatalog):
    is_part_of: [AnyHttpUrl] = Field(
        description="Link to parent object", 
        json_schema_extra={
            "rdf_term": DCTERMS.isPartOf, 
            "rdf_type": "uri"
        })


class RadboudFDPClient:
    """Client for publishing metadata to the Radboud FAIR Data Point."""

    BASE_URL = "https://fdp.radboudumc.nl"
    TEST_PATH_PREFIX = "/acc"

    def __init__(self, test: bool = False, token: str | None = None):
        """Initialize the FDP client.

        Args:
            test: Whether to use the acceptance (test) environment.
            token: Optional API token. If not provided, the environment
                variable ``Radboud_FDP_key`` is used.
        """
        self.test = test
        self.api_token = token or os.getenv("Radboud_FDP_key")

        self.base_url = self.BASE_URL
        self.post_base_url = (
            f"{self.BASE_URL}{self.TEST_PATH_PREFIX}"
            if test
            else self.BASE_URL
        )

    def get(self, endpoint: str) -> requests.Response:
        """Perform a GET request against the FDP API.

        Args:
            endpoint: Relative API endpoint.

        Returns:
            The HTTP response.
        """
        url = urljoin(f"{self.post_base_url}/", endpoint)
        response = requests.get(url, headers=self._auth_headers())
        self._check_response(response, action="GET")
        return response

    def create_and_publish(
        self,
        metadata_record: MetadataRecord,
        catalog_name: str,
    ) -> List[str]:
        """Create and publish a catalog, datasets, and distributions.

        Args:
            metadata_record: MetadataRecord containing catalog, datasets,
                and distributions.
            catalog_name: Name used to construct the catalog URI.

        Returns:
            A list of URLs of all created FDP resources.
        """
        created_urls: List[str] = []
        excluded_fields = {"dataset", "distribution"}

        # -------------------------
        # Create catalog
        # -------------------------
        catalog_fields = self._filter_fields(
            metadata_record.catalog,
            excluded_fields,
        )
        catalog = FDPCatalog(
            is_part_of=[URIRef(self.base_url)],
            dataset=[],
            **catalog_fields,
        )

        catalog_graph = catalog.to_graph(
            URIRef(f"{self.post_base_url}/catalog/{catalog_name}")
        )
        catalog_response = self._post_turtle(
            catalog_graph.serialize(format="turtle"),
            "catalog",
        )
        catalog_url = catalog_response.headers["Location"]
        created_urls.append(catalog_url)

        # -------------------------
        # Create datasets
        # -------------------------
        for dataset in metadata_record.catalog.dataset:
            dataset_fields = self._filter_fields(dataset, excluded_fields)
            hri_dataset = HRIDataset(**dataset_fields)

            dataset_graph = hri_dataset.to_graph(
                subject=URIRef(hri_dataset.identifier)
            )
            dataset_graph.add(
                (
                    URIRef(hri_dataset.identifier),
                    DCTERMS.isPartOf,
                    URIRef(catalog_url),
                )
            )

            dataset_response = self._post_turtle(
                dataset_graph.serialize(format="turtle"),
                "dataset",
            )
            dataset_url = dataset_response.headers["Location"]
            created_urls.append(dataset_url)

            # -------------------------
            # Create distributions
            # -------------------------
            for distribution in dataset.distribution or []:
                try:
                    distribution_fields = self._filter_fields(
                        distribution,
                        excluded_fields,
                    )

                    # Temporary SHACL workaround
                    HRIDistribution.model_fields["byte_size"].json_schema_extra[
                        "rdf_type"
                    ] = "xsd:nonNegativeInteger"

                    hri_distribution = HRIDistribution(**distribution_fields)

                    access_url = str(hri_distribution.access_url)
                    distribution_uri = URIRef(
                        f"{hri_dataset.identifier}/distribution/"
                        f"{access_url.split('/')[-1]}"
                    )

                    distribution_graph = hri_distribution.to_graph(
                        subject=distribution_uri
                    )
                    distribution_graph.add(
                        (
                            distribution_uri,
                            DCTERMS.isPartOf,
                            URIRef(dataset_url),
                        )
                    )

                    distribution_response = self._post_turtle(
                        distribution_graph.serialize(format="turtle"),
                        "distribution",
                    )
                    distribution_url = distribution_response.headers["Location"]
                    created_urls.append(distribution_url)

                    self._publish(distribution_url)
                except Exception:
                    logging.exception(
                        "Failed to create distribution for dataset %s",
                        hri_dataset.identifier,
                    )

            self._publish(dataset_url)

        self._publish(catalog_url)
        return created_urls

    def update(
        self,
        target_type: str,
        metadata_record: MetadataRecord,
        resource_url: str,
        parent_url: str,
    ) -> requests.Response:
        """Update an existing FDP resource.

        Args:
            target_type: One of ``catalog`` or ``dataset``.
            metadata_record: Updated metadata record.
            resource_url: URL of the resource to update.
            parent_url: URL of the parent resource.

        Returns:
            The HTTP response.
        """
        excluded_fields = {"dataset", "distribution"}

        if target_type == "catalog":
            fields = self._filter_fields(metadata_record, excluded_fields)
            catalog = FDPCatalog(
                is_part_of=[URIRef(self.base_url)],
                dataset=[parent_url],
                **fields,
            )
            graph = catalog.to_graph(URIRef(resource_url))

        elif target_type == "dataset":
            fields = self._filter_fields(metadata_record, excluded_fields)
            dataset = HRIDataset(**fields)
            graph = dataset.to_graph(subject=URIRef(resource_url))
            graph.add(
                (URIRef(resource_url), DCTERMS.isPartOf, URIRef(parent_url))
            )

        else:
            raise ValueError(f"Invalid target_type: {target_type}")

        response = self._put_turtle(
            graph.serialize(format="turtle"),
            resource_url,
        )
        logging.info(
            "Updated %s (expected 200): %s", target_type, response.status_code
        )
        return response

    def delete(self, resource_url: str, confirm: bool = True) -> requests.Response | None:
        """Delete a resource from the FDP.

        Args:
            resource_url: URL of the resource to delete.
            confirm: Whether to require interactive confirmation.

        Returns:
            The HTTP response, or None if deletion was cancelled.
        """
        if confirm and not self._confirm_deletion(resource_url):
            logging.info("Deletion cancelled for %s", resource_url)
            return None

        response = requests.delete(
            resource_url,
            headers=self._auth_headers(),
        )
        self._check_response(response, action="DELETE")
        logging.info("Deleted %s (expected 204)", resource_url)
        return response

    def _post_turtle(self, turtle_data: str, resource_type: str) -> requests.Response:
        url = f"{self.post_base_url}/{resource_type}"
        response = requests.post(
            url,
            headers=self._turtle_headers(),
            data=turtle_data,
            allow_redirects=True,
        )
        self._check_response(response, action="POST")
        logging.info(f"Posting: {resource_type}, response (should be 201): {response}")        
        return response

    def _put_turtle(self, turtle_data: str, resource_url: str) -> requests.Response:
        resource_url = self._apply_test_prefix(resource_url)
        response = requests.put(
            resource_url,
            headers=self._turtle_headers(accept="text/turtle"),
            data=turtle_data,
        )
        self._check_response(response, action="PUT")
        return response

    def _publish(self, resource_url: str) -> requests.Response:
        resource_url = self._apply_test_prefix(resource_url)
        publish_url = f"{resource_url}/meta/state"

        response = requests.put(
            publish_url,
            headers={
                **self._auth_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"current": "PUBLISHED"},
        )
        self._check_response(response, action="PUT")
        logging.info(f"Published, this should be 200: {response}")        
        return response

    def _check_response(
        self,
        response: requests.Response,
        action: str = "request",
    ) -> None:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.error(
                "%s failed (%s): %s",
                action.upper(),
                response.status_code,
                response.url,
            )
            logging.error("Response headers: %s", response.headers)
            logging.error("Response body:\n%s", response.text)
            raise

    def _apply_test_prefix(self, url: str) -> str:
        if not self.test:
            return url

        parsed = urlparse(url)
        return urlunparse(
            parsed._replace(path=f"{self.TEST_PATH_PREFIX}{parsed.path}")
        )

    def _filter_fields(self, obj, excluded_fields: set[str]) -> dict:
        return {
            key: value
            for key, value in vars(obj).items()
            if key not in excluded_fields and value is not None
        }

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_token}"}

    def _turtle_headers(self, accept: str = "text/turtle") -> dict[str, str]:
        return {
            **self._auth_headers(),
            "Accept": accept,
            "Content-Type": "text/turtle",
        }

    def _confirm_deletion(self, resource_url: str) -> bool:
        while True:
            user_input = input(
                f"Are you sure you want to DELETE {resource_url}? [yes/no]: "
            ).strip().lower()

            if user_input == "yes":
                return True
            if user_input in ("", "n", "no"):
                return False