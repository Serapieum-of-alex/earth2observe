"""Catalog of the Earth2Observe GEE datasource."""
import os
from typing import Dict, List
from dataclasses import dataclass
import yaml
from earth2observe.abstractdatasource import AbstractCatalog
from earth2observe.gee import __path__


@dataclass
class DatasetInfo:
    """Dataset."""

    name: str
    provider: str
    url: str
    spatial_resolution: int
    temporal_resolution: int
    start_date: str
    end_date: str
    bands: List[str]
    bands_description: List[str]
    min: List[int]
    max: List[int]
    date_format: str = "%Y-%m-%d"


class Catalog(AbstractCatalog):
    """abstract class for the datasource catalog."""

    def __init__(self):
        super().__init__()

    @property
    def datasets(self) -> List[str]:
        """get the list of available datasets."""
        return list(self.catalog.keys())

    def get_variable(self, var_name) -> Dict[str, str]:
        """get the variable information from the catalog."""
        return super().get_variable(var_name)

    def get_catalog(self) -> Dict:
        """read the catalog of the datasource from disk or retrieve it from server.


            get_catalog retrieves the dataset catalog

        Returns
        -------
        DataFrame
        """
        with open(os.path.join(__path__[0], "catalog.yaml"), 'r') as file:
            data = yaml.safe_load(file)
        return data

    def __getitem__(self, dataset_id: str) -> DatasetInfo:
        return DatasetInfo(**self.catalog[dataset_id])

    def __repr__(self):
        return self.catalog.__repr__()

    def __str__(self):
        return self.catalog.__str__()
