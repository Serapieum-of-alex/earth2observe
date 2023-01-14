from typing import Dict
from abc import ABC, abstractmethod


class DataSource(ABC):
    """
    Bluebrint for all class for different datasources
    """

    @abstractmethod
    def download(self):
        """Wrapper over all the given variables."""
        pass


    # @abstractmethod
    def downloadDataset(self):
        """Download single variable/dataset"""
        pass

    @abstractmethod
    def API(self):
        """send/recieve request to the dataset server"""
        pass

    @abstractmethod
    def create_grid(self):
        """create a grid from the lat/lon boundaries"""
        pass


class CatalogTemplate(ABC):
    """abstrach class for the datasource catalog"""

    @abstractmethod
    def get_catalog(self):
        """read the catalog of the datasource from disk or retrieve it from server"""
        pass

    @abstractmethod
    def get_variable(self, var_name) -> Dict[str, str]:
        """get the details of a specific variable"""
        pass
