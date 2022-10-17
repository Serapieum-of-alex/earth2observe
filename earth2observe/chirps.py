import datetime as dt
import os
from ftplib import FTP

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from osgeo import gdal
from pyramids.raster import Raster

from earth2observe.utils import extractFromGZ, print_progress_bar


class CHIRPS:
    """CHIRPS."""

    def __init__(
        self,
        start: str = "",
        end: str = "",
        lat_lim: list = [],
        lon_lim: list = [],
        time: str = "daily",
        path: str = "",
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
        self.lat_lim = []
        self.lon_lim = []
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
        if start == "":
            self.start = pd.Timestamp("1981-01-01")
        else:
            self.start = dt.datetime.strptime(start, fmt)

        if end == "":
            self.end = pd.Timestamp("Now")
        else:
            self.end = dt.datetime.strptime(end, fmt)
        # Create days
        self.Dates = pd.date_range(self.start, self.end, freq=self.time_freq)

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

    def Download(self, progress_bar: bool = True, cores=None):
        """Download.

        Download method downloads CHIRPS data

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
                CHIRPS.RetrieveData(Date, args)
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
                delayed(CHIRPS.RetrieveData)(Date, args) for Date in self.Dates
            )
        return results

    @staticmethod
    def RetrieveData(Date, args):
        """RetrieveData.

        RetrieveData method retrieves CHIRPS data for a given date from the
        https://data.chc.ucsb.edu/

        Parameters
        ----------
        Date : TYPE
            DESCRIPTION.
        args : TYPE
            A list of parameters defined in the DownloadData function.

        Raises
        ------
        KeyError
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.
        """
        # Argument
        [output_folder, TimeCase, xID, yID, lon_lim, latlim] = args

        # open ftp server
        # ftp = FTP("chg-ftpout.geog.ucsb.edu", "", "")
        ftp = FTP("data.chc.ucsb.edu")
        ftp.login()

        # Define FTP path to directory
        if TimeCase.lower() == "daily":
            pathFTP = (
                "pub/org/chg/products/CHIRPS-2.0/global_daily/tifs/p05/%s/"
                % Date.strftime("%Y")
            )
        elif TimeCase == "monthly":
            pathFTP = "pub/org/chg/products/CHIRPS-2.0/global_monthly/tifs/"
        else:
            raise KeyError("The input time interval is not supported")

        # find the document name in this directory
        ftp.cwd(pathFTP)
        listing = []

        # read all the file names in the directory
        ftp.retrlines("LIST", listing.append)

        # create all the input name (filename) and output (outfilename, filetif, DiFileEnd) names
        if TimeCase.lower() == "daily":
            filename = "chirps-v2.0.%s.%02s.%02s.tif.gz" % (
                Date.strftime("%Y"),
                Date.strftime("%m"),
                Date.strftime("%d"),
            )
            outfilename = os.path.join(
                output_folder,
                "chirps-v2.0.%s.%02s.%02s.tif"
                % (Date.strftime("%Y"), Date.strftime("%m"), Date.strftime("%d")),
            )
            DirFileEnd = os.path.join(
                output_folder,
                "P_CHIRPS.v2.0_mm-day-1_daily_%s.%02s.%02s.tif"
                % (Date.strftime("%Y"), Date.strftime("%m"), Date.strftime("%d")),
            )
        elif TimeCase == "monthly":
            filename = "chirps-v2.0.%s.%02s.tif.gz" % (
                Date.strftime("%Y"),
                Date.strftime("%m"),
            )
            outfilename = os.path.join(
                output_folder,
                "chirps-v2.0.%s.%02s.tif" % (Date.strftime("%Y"), Date.strftime("%m")),
            )
            DirFileEnd = os.path.join(
                output_folder,
                "P_CHIRPS.v2.0_mm-month-1_monthly_%s.%02s.%02s.tif"
                % (Date.strftime("%Y"), Date.strftime("%m"), Date.strftime("%d")),
            )
        else:
            raise KeyError("The input time interval is not supported")

        # download the global rainfall file
        try:
            local_filename = os.path.join(output_folder, filename)
            lf = open(local_filename, "wb")
            ftp.retrbinary("RETR " + filename, lf.write, 8192)
            lf.close()

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

    def ListAttributes(self):
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
