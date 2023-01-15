from typing import Dict
from abc import ABC, abstractmethod


class AbstractDataSource(ABC):
    """
    Bluebrint for all class for different datasources
    """
    def __init__(
            self,
            temporal_resolution: str = "daily",
            start: str = None,
            end: str = None,
            path: str = "",
            variables: list = None,
            lat_lim: list = None,
            lon_lim: list = None,
            fmt: str = "%Y-%m-%d",
    ):
        """

        Parameters
        ----------
        temporal_resolution (str, optional):
            [description]. Defaults to 'daily'.
        start (str, optional):
            [description]. Defaults to ''.
        end (str, optional):
            [description]. Defaults to ''.
        path (str, optional):
            Path where you want to save the downloaded data. Defaults to ''.
        variables (list, optional):
            Variable code: VariablesInfo('day').descriptions.keys(). Defaults to [].
        lat_lim (list, optional):
            [ymin, ymax]. Defaults to None.
        lon_lim (list, optional):
            [xmin, xmax]. Defaults to None.
        fmt (str, optional):
            [description]. Defaults to "%Y-%m-%d".
        """
        pass

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
    def initialize(self):
        """Initialize connection with the data source server (for non ftp servers)"""
        pass

    @abstractmethod
    def create_grid(self):
        """create a grid from the lat/lon boundaries"""
        pass


class AbstractCatalog(ABC):
    """abstrach class for the datasource catalog"""

    @abstractmethod
    def get_catalog(self):
        """read the catalog of the datasource from disk or retrieve it from server"""
        pass

    @abstractmethod
    def get_variable(self, var_name) -> Dict[str, str]:
        """get the details of a specific variable"""
        pass
