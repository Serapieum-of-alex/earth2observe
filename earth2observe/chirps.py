from typing import List
import datetime as dt
import os
from ftplib import FTP

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from osgeo import gdal
from pyramids.raster import Raster
from pyramids.utils import extractFromGZ
from earth2observe.datasource import DataSource, CatalogTemplate
from earth2observe.utils import print_progress_bar


class CHIRPS(DataSource):
    """CHIRPS."""
    api_url: str = "data.chc.ucsb.edu"

    def __init__(
            self,
            time: str = "daily",
            start: str = None,
            end: str = None,
            path: str = "",
            lat_lim: list = None,
            lon_lim: list = None,
            fmt: str = "%Y-%m-%d",
    ):
        """CHIRPS.

        Parameters
        ----------
        time (str, optional):
            'daily' or 'monthly'. Defaults to 'daily'.
        start (str, optional):
            [description]. Defaults to ''.
        end (str, optional):
            [description]. Defaults to ''.
        path (str, optional):
            Path where you want to save the downloaded data. Defaults to ''.
        variables (list, optional):
            Variable code: VariablesInfo('day').descriptions.keys(). Defaults to [].
        lat_lim (list, optional):
            [ymin, ymax] (values must be between -50 and 50). Defaults to [].
        lon_lim (list, optional):
            [xmin, xmax] (values must be between -180 and 180). Defaults to [].
        fmt (str, optional):
            [description]. Defaults to "%Y-%m-%d".
        """
        # Define timestep for the timedates
        if time.lower() == "daily":
            self.time_freq = "D"
            self.output_folder = os.path.join(path, "Precipitation", "CHIRPS", "Daily")
        elif time.lower() == "monthly":
            self.time_freq = "MS"
            self.output_folder = os.path.join(
                path, "Precipitation", "CHIRPS", "Monthly"
            )
        else:
            raise KeyError("The input time interval is not supported")

        self.time = time

        # make directory if it not exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # check time variables
        if start is None:
            self.start = pd.Timestamp("1981-01-01")
        else:
            self.start = dt.datetime.strptime(start, fmt)

        if end is None:
            self.end = pd.Timestamp("Now")
        else:
            self.end = dt.datetime.strptime(end, fmt)
        # Create days
        self.Dates = pd.date_range(self.start, self.end, freq=self.time_freq)
        self.create_grid(lat_lim, lon_lim)


    def create_grid(self, lat_lim: list, lon_lim: list):
        """Create_grid

            create grid from the lat/lon boundaries

        Parameters
        ----------
        lat_lim: []
            latitude boundaries
        lon_lim: []
            longitude boundaries
        """
        self.lat_lim = []
        self.lon_lim = []
        # Check space variables
        if lat_lim[0] < -50 or lat_lim[1] > 50:
            print(
                "Latitude above 50N or below 50S is not possible."
                " Value set to maximum"
            )
            self.lat_lim[0] = np.max(lat_lim[0], -50)
            self.lat_lim[1] = np.min(lon_lim[1], 50)
        if lon_lim[0] < -180 or lon_lim[1] > 180:
            print(
                "Longitude must be between 180E and 180W."
                " Now value is set to maximum"
            )
            self.lon_lim[0] = np.max(lat_lim[0], -180)
            self.lon_lim[1] = np.min(lon_lim[1], 180)
        else:
            self.lat_lim = lat_lim
            self.lon_lim = lon_lim
        # Define IDs
        self.yID = 2000 - np.int16(
            np.array(
                [np.ceil((lat_lim[1] + 50) * 20), np.floor((lat_lim[0] + 50) * 20)]
            )
        )
        self.xID = np.int16(
            np.array(
                [np.floor((lon_lim[0] + 180) * 20), np.ceil((lon_lim[1] + 180) * 20)]
            )
        )


    def download(self, progress_bar: bool = True, cores=None):
        """Download.

            downloads CHIRPS data

        Parameters
        ----------
        progress_bar : TYPE, optional
            will print a waitbar. The default is 1.
        cores : TYPE, optional
            The number of cores used to run the routine. It can be 'False'
                 to avoid using parallel computing routines. The default is None.

        Returns
        -------
        results : TYPE
            DESCRIPTION.
        """
        # Pass variables to parallel function and run
        args = [
            self.output_folder,
            self.time,
            self.xID,
            self.yID,
            self.lon_lim,
            self.lat_lim,
        ]

        if not cores:
            # Create Waitbar
            if progress_bar:
                total_amount = len(self.Dates)
                amount = 0
                print_progress_bar(
                    amount,
                    total_amount,
                    prefix="Progress:",
                    suffix="Complete",
                    length=50,
                )

            for Date in self.Dates:
                self.API(Date, args)
                if progress_bar:
                    amount = amount + 1
                    print_progress_bar(
                        amount,
                        total_amount,
                        prefix="Progress:",
                        suffix="Complete",
                        length=50,
                    )
            results = True
        else:
            results = Parallel(n_jobs=cores)(
                delayed(self.API)(Date, args) for Date in self.Dates
            )
        return results

    def API(self, Date, args):
        """form the request url abd trigger the request

        Parameters
        ----------
        Date:

        args: [list]

        """
        [output_folder, TimeCase, xID, yID, lon_lim, latlim] = args

        # Define FTP path to directory
        if TimeCase.lower() == "daily":
            pathFTP = f"pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/{Date.strftime('%Y')}/"
        elif TimeCase == "monthly":
            pathFTP = "pub/org/chg/products/CHIRPS-2.0/global_monthly/tifs/"
        else:
            raise KeyError("The input time interval is not supported")

        # create all the input name (filename) and output (outfilename, filetif, DiFileEnd) names
        if TimeCase.lower() == "daily":
            filename = f"chirps-v2.0.{Date.strftime('%Y')}.{Date.strftime('%m')}.{Date.strftime('%d')}.tif.gz"
            outfilename = os.path.join(
                output_folder,
                f"chirps-v2.0.{Date.strftime('%Y')}.{Date.strftime('%m')}.{Date.strftime('%d')}.tif"
            )
            DirFileEnd = os.path.join(
                output_folder,
                f"P_CHIRPS.v2.0_mm-day-1_daily_{Date.strftime('%Y')}.{Date.strftime('%m')}.{Date.strftime('%d')}.tif"
            )
        elif TimeCase == "monthly":
            filename = f"chirps-v2.0.{Date.strftime('%Y')}.{Date.strftime('%m')}.tif.gz"
            outfilename = os.path.join(
                output_folder,
                f"chirps-v2.0.{Date.strftime('%Y')}.{Date.strftime('%m')}.tif"
            )
            DirFileEnd = os.path.join(
                output_folder,
                f"P_CHIRPS.v2.0_mm-month-1_monthly_{Date.strftime('%Y')}.{Date.strftime('%m')}.{Date.strftime('%d')}.tif"
            )
        else:
            raise KeyError("The input time interval is not supported")

        self.callAPI(pathFTP, output_folder, filename)
        self.post_download(output_folder, filename, lon_lim, latlim, xID, yID, outfilename, DirFileEnd)


    @staticmethod
    def callAPI(pathFTP: str, output_folder: str, filename: str):
        """send the request to the server.

        RetrieveData method retrieves CHIRPS data for a given date from the
        https://data.chc.ucsb.edu/

        Parameters
        ----------
        filename
        output_folder
        pathFTP


        Raises
        ------
        KeyError
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.
        """
        # open ftp server
        # ftp = FTP("chg-ftpout.geog.ucsb.edu", "", "")
        ftp = FTP(CHIRPS.api_url)
        ftp.login()

        # find the document name in this directory
        ftp.cwd(pathFTP)
        listing = []

        # read all the file names in the directory
        ftp.retrlines("LIST", listing.append)

        # download the global rainfall file
        local_filename = os.path.join(output_folder, filename)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write, 8192)
        lf.close()


    def post_download(self, output_folder, filename, lon_lim, latlim, xID, yID, outfilename, DirFileEnd):
        """clip the downloaded data to the extent we want

        Parameters
        ----------
        output_folder: [str]
            directory where files will be saved
        filename: [str]
            file name
        lon_lim: [list]
        latlim: [list]
        xID: [list]
        yID: [list]
        outfilename: [str]
        DirFileEnd: [str]
        """
        try:
            # unzip the file
            zip_filename = os.path.join(output_folder, filename)
            extractFromGZ(zip_filename, outfilename, delete=True)

            # open tiff file
            src = gdal.Open(outfilename)
            dataset, NoDataValue = Raster.getRasterData(src)

            # clip dataset to the given extent
            data = dataset[yID[0] : yID[1], xID[0] : xID[1]]
            # replace -ve values with -9999
            data[data < 0] = -9999

            # save dataset as geotiff file
            geo = [lon_lim[0], 0.05, 0, latlim[1], 0, -0.05]
            Raster.createRaster(
                DirFileEnd,
                data,
                geo=geo,
                epsg="WGS84",
                nodatavalue=NoDataValue,
            )

            # delete old tif file
            os.remove(outfilename)

        except PermissionError:
            print(
                "The file covering the whole world could not be deleted please delete it after the download ends"
            )
        return True

    def listAttributes(self):
        """Print Attributes List."""

        print("\n")
        print(
            f"Attributes List of: {repr(self.__dict__['name'])} - {self.__class__.__name__} Instance\n"
        )
        self_keys = list(self.__dict__.keys())
        self_keys.sort()
        for key in self_keys:
            if key != "name":
                print(str(key) + " : " + repr(self.__dict__[key]))

        print("\n")

class Catalog(CatalogTemplate):
    """ CHIRPS data catalog"""

    def __init__(self):
        self.catalog = self.get_catalog()

    def get_catalog(self):
        """return the catalog"""
        return {
            "Precipitation": {
                "descriptions": "rainfall [mm/time step]",
                "units": "mm/time step",
                "temporal resolution": ["daily", "monthly"],
                "file name": "rainfall",
                "var_name": "R",
                }
        }

    def get_variable(self, var_name):
        """get the details of a specific variable"""
        return self.catalog.get(var_name)
