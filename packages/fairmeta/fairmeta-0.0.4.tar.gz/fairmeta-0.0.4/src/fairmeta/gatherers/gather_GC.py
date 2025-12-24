"""
GrandChallenge data gatherer.

This module provides the `GrandChallenge` class, which interfaces
with the Grand Challenge API to collect metadata from challenges and
archives.
"""

import logging
import os
from urllib.parse import quote
from typing import Any, Dict, List

import gcapi


class GrandChallenge:
    """Gatherer for Grand Challenge challenges and archives."""

    def __init__(self, token: str = None):
        """Initialize the Grand Challenge client.

        Args:
            token: Optional API token. If not provided, reads from
                the environment variable 'GC_key'.
        """
        self.client = gcapi.Client(token=token or os.getenv("GC_key"))

    def gather_data(self, slugs: List[str]) -> List[Dict[str, Any]]:
        """Gather challenge and archive data for a list of slugs.

        For each slug, this method fetches the archive and challenge data
        from the API, merges them into a single dictionary, and optionally
        counts the number of images in the archive.

        Args:
            slugs: List of challenge/archive slugs to gather.

        Returns:
            A list of dictionaries containing combined metadata for each slug.
        """
        combined_data: List[Dict[str, Any]] = []

        for slug in slugs:
            normalized_slug = quote(slug.strip("/"), safe="")
            combined_dict: Dict[str, Any] = {"id": normalized_slug}

            # Gather archive data
            try:
                archive_data = self._gather_archive(normalized_slug)
                combined_dict.update(
                    {f"archive_{k}": v for k, v in archive_data.items()}
                )
            except Exception as e:
                logging.warning(
                    "Could not gather data from archive '%s': %s", normalized_slug, e
                )
                archive_data = {}

            # Gather challenge data
            try:
                challenge_data = self._gather_challenge(normalized_slug)
                combined_dict.update(
                    {f"challenge_{k}": v for k, v in challenge_data.items()}
                )
            except Exception as e:
                logging.warning(
                    "Could not gather data from challenge '%s': %s",
                    normalized_slug,
                    e,
                )
                challenge_data = {}

            # Count images if archive exists
            archive_pk = archive_data.get("pk")
            if archive_pk:
                try:
                    images_iter = self.client.images.iterate_all(params={"archive": archive_pk})
                    first_image = next(images_iter, None)
                    num_images = len(self.client.images.list(params={"archive": archive_pk}))
                    combined_dict.update({"byte_size": num_images})
                except Exception as e:
                    logging.warning(
                        "Could not determine number of images for archive '%s': %s",
                        normalized_slug,
                        e,
                    )

            combined_data.append(combined_dict)

        return combined_data
    
    def _gather_archive(self, slug: str) -> Dict[str, Any]:
        """Retrieve archive metadata from the Grand Challenge API.

        Args:
            slug: Slug identifier for the archive.

        Returns:
            A dictionary containing the archive metadata.
        """
        archive = self.client.archives.detail(slug=slug.lower()) # .lower() because sometimes the archive slug is the challenge slug but lowercase
        return archive.__dict__

    def _gather_challenge(self, slug: str) -> Dict[str, Any]:
        """Retrieve challenge metadata from the Grand Challenge API.

        Args:
            slug: Slug identifier for the challenge.

        Returns:
            A dictionary containing the challenge metadata.
        """
        response = self.client.get(f"/challenges/{slug}", follow_redirects=True)
        response.raise_for_status()
        return response.json()