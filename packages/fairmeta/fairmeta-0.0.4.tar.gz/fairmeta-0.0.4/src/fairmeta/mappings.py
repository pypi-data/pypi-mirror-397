"""
Controlled vocabulary mappings used by FAIRMeta.

This module defines mappings from human-readable string values to
Health-RI / DCAT controlled vocabulary objects provided by sempyro.

These mappings are primarily used by MetadataRecord to normalize
string inputs into standardized, interoperable values.
"""

from sempyro.dcat import AccessRights
from sempyro.dcat.dcat_dataset import Frequency
from sempyro.hri_dcat import (
    DatasetStatus,
    DatasetTheme,
    DistributionStatus,
    GeonovumLicences,
)

ACCESS_RIGHTS_BY_NAME = {right.name: right for right in AccessRights}

DISTRIBUTION_STATUS_BY_NAME = {status.name: status for status in DistributionStatus}

FREQUENCY_BY_NAME = {frequency.name.lower(): frequency for frequency in Frequency}

LICENSE_BY_NAME = {lic.name: lic.value for lic in GeonovumLicences}

DATASET_STATUS_BY_NAME = {status.name: status for status in DatasetStatus}

DATASET_THEME_BY_NAME = {theme.name: theme for theme in DatasetTheme}

__all__ = [
    "ACCESS_RIGHTS_BY_NAME",
    "DISTRIBUTION_STATUS_BY_NAME",
    "FREQUENCY_BY_NAME",
    "LICENSE_BY_NAME",
    "DATASET_STATUS_BY_NAME",
    "DATASET_THEME_BY_NAME",
]