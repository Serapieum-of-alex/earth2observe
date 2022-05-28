"""
Created on Fri Apr  2 06:58:20 2021

@author: mofarrag
"""
import calendar
import datetime as dt
import os
from ftplib import FTP
import gzip

import numpy as np
import pandas as pd
from ecmwfapi import ECMWFDataServer
from joblib import Parallel, delayed
from netCDF4 import Dataset
from osgeo import gdal
import Hapi.weirdFn as weirdFn
from pyramids.raster import Raster


class RemoteSensing:
    """RemoteSensing.

    RemoteSensing class contains methods to download ECMWF data

    Methods:
        1- main
        2- DownloadData
        3- API
        4- ListAttributes
    """
    def __init__(
            self,
            Time="daily",
            start="",
            end="",
            Path="",
            Vars=[],
            latlim=[],
            lonlim=[],
            fmt="%Y-%m-%d",
    ):
        """
            RemoteSensing(self, Time='daily', start='', end='',Path='',
                          Vars=[], latlim=[], lonlim=[], fmt="%Y-%m-%d")

        Parameters:
            Time (str, optional):
                [description]. Defaults to 'daily'.
            start (str, optional):
                [description]. Defaults to ''.
            end (str, optional):
                [description]. Defaults to ''.
            Path (str, optional):
                Path where you want to save the downloaded data. Defaults to ''.
            Vars (list, optional):
                Variable code: VariablesInfo('day').descriptions.keys(). Defaults to [].
            latlim (list, optional):
                [ymin, ymax]. Defaults to [].
            lonlim (list, optional):
                [xmin, xmax]. Defaults to [].
            fmt (str, optional):
                [description]. Defaults to "%Y-%m-%d".
        """
        self.start = dt.datetime.strptime(start, fmt)
        self.end = dt.datetime.strptime(end, fmt)

        if Time == "six_hourly":
            # Set required data for the three hourly option
            self.string1 = "oper"
        # Set required data for the daily option
        elif Time == "daily":
            self.Dates = pd.date_range(self.start, self.end, freq="D")
        elif Time == "monthly":
            self.Dates = pd.date_range(self.start, self.end, freq="MS")

        self.Time = Time
        self.Path = Path
        self.Vars = Vars

        # correct latitude and longitude limits
        latlim_corr_one = np.floor(latlim[0] / 0.125) * 0.125
        latlim_corr_two = np.ceil(latlim[1] / 0.125) * 0.125
        self.latlim_corr = [latlim_corr_one, latlim_corr_two]

        # correct latitude and longitude limits
        lonlim_corr_one = np.floor(lonlim[0] / 0.125) * 0.125
        lonlim_corr_two = np.ceil(lonlim[1] / 0.125) * 0.125
        self.lonlim_corr = [lonlim_corr_one, lonlim_corr_two]
        # TODO move it to the ECMWF method later
        # for ECMWF only
        self.string7 = "%s/to/%s" % (self.start, self.end)


    def ECMWF(self, Waitbar: bool = True):
        """ECMWF

        ECMWF method downloads ECMWF daily data for a given variable, time
        interval, and spatial extent.


        Parameters
        ----------
        Waitbar : TYPE, optional
            0 or 1. to display the progress bar

        Returns
        -------
        None.
        """
        for var in self.Vars:
            # Download data
            print(f"\nDownload ECMWF {var} data for period {self.start} till {self.end}")

            self.DownloadData(var, Waitbar)  # CaseParameters=[SumMean, Min, Max]
        # delete the downloaded netcdf
        del_ecmwf_dataset = os.path.join(self.Path, "data_interim.nc")
        os.remove(del_ecmwf_dataset)


    def DownloadData(self, Var: str, Waitbar: bool):
        """
        This function downloads ECMWF six-hourly, daily or monthly data

        Parameters
        ----------
        Var: [str]

        """
        # Load factors / unit / type of variables / accounts
        VarInfo = Variables(self.Time)
        Varname_dir = VarInfo.file_name[Var]

        # Create Out directory
        out_dir = os.path.join(self.Path, self.Time, Varname_dir)

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        DownloadType = VarInfo.DownloadType[Var]

        if DownloadType == 1:
            string1 = "oper"
            string4 = "0"
            string6 = "00:00:00/06:00:00/12:00:00/18:00:00"
            string2 = "sfc"
            string8 = "an"

        if DownloadType == 2:
            string1 = "oper"
            string4 = "12"
            string6 = "00:00:00/12:00:00"
            string2 = "sfc"
            string8 = "fc"

        if DownloadType == 3:
            string1 = "oper"
            string4 = "0"
            string6 = "00:00:00/06:00:00/12:00:00/18:00:00"
            string2 = "pl"
            string8 = "an"

        parameter_number = VarInfo.number_para[Var]

        string3 = "%03d.128" % (parameter_number)
        string5 = "0.125/0.125"
        string9 = "ei"
        string10 = "%s/%s/%s/%s" % (
            self.latlim_corr[1],
            self.lonlim_corr[0],
            self.latlim_corr[0],
            self.lonlim_corr[1],
        )  # N, W, S, E

        # Download data by using the ECMWF API
        print("Use API ECMWF to collect the data, please wait")
        RemoteSensing.API(
            self.Path,
            DownloadType,
            string1,
            string2,
            string3,
            string4,
            string5,
            string6,
            self.string7,
            string8,
            string9,
            string10,
        )

        # Open the downloaded data
        NC_filename = os.path.join(self.Path, "data_interim.nc")
        fh = Dataset(NC_filename, mode="r")

        # Get the NC variable parameter
        parameter_var = VarInfo.var_name[Var]
        Var_unit = VarInfo.units[Var]
        factors_add = VarInfo.factors_add[Var]
        factors_mul = VarInfo.factors_mul[Var]

        # Open the NC data
        Data = fh.variables[parameter_var][:]
        Data_time = fh.variables["time"][:]
        lons = fh.variables["longitude"][:]
        lats = fh.variables["latitude"][:]

        # Define the georeference information
        Geo_four = np.nanmax(lats)
        Geo_one = np.nanmin(lons)
        Geo_out = tuple([Geo_one, 0.125, 0.0, Geo_four, 0.0, -0.125])

        # Create Waitbar
        if Waitbar:
            total_amount = len(self.Dates)
            amount = 0
            weirdFn.printWaitBar(
                amount, total_amount, prefix="Progress:", suffix="Complete", length=50
            )

        for date in self.Dates:

            # Define the year, month and day
            year = date.year
            month = date.month
            day = date.day

            # Hours since 1900-01-01
            start = dt.datetime(year=1900, month=1, day=1)
            end = dt.datetime(year, month, day)
            diff = end - start
            hours_from_start_begin = diff.total_seconds() / 60 / 60

            Date_good = np.zeros(len(Data_time))

            if self.Time == "daily":
                days_later = 1
            if self.Time == "monthly":
                days_later = calendar.monthrange(year, month)[1]

            Date_good[
                np.logical_and(
                    Data_time >= hours_from_start_begin,
                    Data_time < (hours_from_start_begin + 24 * days_later),
                )
            ] = 1

            Data_one = np.zeros(
                [int(np.sum(Date_good)), int(np.size(Data, 1)), int(np.size(Data, 2))]
            )
            Data_one = Data[np.int_(Date_good) == 1, :, :]

            # Calculate the average temperature in celcius degrees
            Data_end = factors_mul * np.nanmean(Data_one, 0) + factors_add

            if VarInfo.types[Var] == "flux":
                Data_end = Data_end * days_later

            VarOutputname = VarInfo.file_name[Var]

            # Define the out name
            name_out = os.path.join(
                out_dir,
                "%s_ECMWF_ERA-Interim_%s_%s_%d.%02d.%02d.tif"
                % (VarOutputname, Var_unit, self.Time, year, month, day),
            )

            # Create Tiff files
            # Raster.Save_as_tiff(name_out, Data_end, Geo_out, "WGS84")
            Raster.createRaster(path=name_out, arr=Data_end, geo=Geo_out, epsg="WGS84")

            if Waitbar == 1:
                amount = amount + 1
                weirdFn.printWaitBar(
                    amount,
                    total_amount,
                    prefix="Progress:",
                    suffix="Complete",
                    length=50,
                )

        fh.close()

        return ()


    @staticmethod
    def API(
            output_folder,
            DownloadType,
            string1,
            string2,
            string3,
            string4,
            string5,
            string6,
            string7,
            string8,
            string9,
            string10,
    ):

        os.chdir(output_folder)
        server = ECMWFDataServer()

        if DownloadType == 1 or DownloadType == 2:
            server.retrieve(
                {
                    "stream": "%s" % string1,
                    "levtype": "%s" % string2,
                    "param": "%s" % string3,
                    "dataset": "interim",
                    "step": "%s" % string4,
                    "grid": "%s" % string5,
                    "time": "%s" % string6,
                    "date": "%s" % string7,
                    "type": "%s"
                            % string8,  # http://apps.ecmwf.int/codes/grib/format/mars/type/
                    "class": "%s"
                             % string9,  # http://apps.ecmwf.int/codes/grib/format/mars/class/
                    "area": "%s" % string10,
                    "format": "netcdf",
                    "target": "data_interim.nc",
                }
            )

        if DownloadType == 3:
            server.retrieve(
                {
                    "levelist": "1000",
                    "stream": "%s" % string1,
                    "levtype": "%s" % string2,
                    "param": "%s" % string3,
                    "dataset": "interim",
                    "step": "%s" % string4,
                    "grid": "%s" % string5,
                    "time": "%s" % string6,
                    "date": "%s" % string7,
                    "type": "%s"
                            % string8,  # http://apps.ecmwf.int/codes/grib/format/mars/type/
                    "class": "%s"
                             % string9,  # http://apps.ecmwf.int/codes/grib/format/mars/class/
                    "area": "%s" % string10,
                    "format": "netcdf",
                    "target": "data_interim.nc",
                }
            )

        return ()


    @staticmethod
    def ExtractFromGZ(InputFile, OutputFile, delete=False):
        """
        ExtractFromGZ method extract data from the zip/.gz files,
        save the data

        Parameters
        ----------
        zip_filename : [str]
            zipped file name .
        outfilename : [str]
            directory where the unzipped data must be
                                stored.
        delete : [bool]
            True if you want to delete the zipped file after the extracting the data
        Returns
        -------
        None.
        """
        with gzip.GzipFile(InputFile, "rb") as zf:
            content = zf.read()
            save_file_content = open(OutputFile, "wb")
            save_file_content.write(content)

        save_file_content.close()
        zf.close()

        if delete:
            os.remove(InputFile)

class Variables:
    """
    This class contains the information about the ECMWF variables
    http://rda.ucar.edu/cgi-bin/transform?xml=/metadata/ParameterTables/WMO_GRIB1.98-0.128.xml&view=gribdoc
    """

    number_para = {
        "T": 130,
        "2T": 167,
        "SRO": 8,
        "SSRO": 9,
        "WIND": 10,
        "10SI": 207,
        "SP": 134,
        "Q": 133,
        "SSR": 176,
        "R": 157,
        "E": 182,
        "SUND": 189,
        "RO": 205,
        "TP": 228,
        "10U": 165,
        "10V": 166,
        "2D": 168,
        "SR": 173,
        "AL": 174,
        "HCC": 188,
    }

    var_name = {
        "T": "t",
        "2T": "t2m",
        "SRO": "sro",
        "SSRO": "ssro",
        "WIND": "wind",
        "10SI": "10si",
        "SP": "sp",
        "Q": "q",
        "SSR": "ssr",
        "R": "r",
        "E": "e",
        "SUND": "sund",
        "RO": "ro",
        "TP": "tp",
        "10U": "u10",
        "10V": "v10",
        "2D": "d2m",
        "SR": "sr",
        "AL": "al",
        "HCC": "hcc",
    }

    # ECMWF data
    descriptions = {
        "T": "Temperature [K]",
        "2T": "2 meter Temperature [K]",
        "SRO": "Surface Runoff [m]",
        "SSRO": "Sub-surface Runoff [m]",
        "WIND": "Wind speed [m s-1]",
        "10SI": "10 metre windspeed [m s-1]",
        "SP": "Surface Pressure [pa]",
        "Q": "Specific humidity [kg kg-1]",
        "SSR": "Surface solar radiation [W m-2 s]",
        "R": "Relative humidity [%]",
        "E": "Evaporation [m of water]",
        "SUND": "Sunshine duration [s]",
        "RO": "Runoff [m]",
        "TP": "Total Precipitation [m]",
        "10U": "10 metre U wind component [m s-1]",
        "10V": "10 metre V wind component [m s-1]",
        "2D": "2 metre dewpoint temperature [K]",
        "SR": "Surface roughness [m]",
        "AL": "Albedo []",
        "HCC": "High cloud cover []",
    }

    # Factor add to get output
    factors_add = {
        "T": -273.15,
        "2T": -273.15,
        "SRO": 0,
        "SSRO": 0,
        "WIND": 0,
        "10SI": 0,
        "SP": 0,
        "Q": 0,
        "SSR": 0,
        "R": 0,
        "E": 0,
        "SUND": 0,
        "RO": 0,
        "TP": 0,
        "10U": 0,
        "10V": 0,
        "2D": -273.15,
        "SR": 0,
        "AL": 0,
        "HCC": 0,
    }

    # Factor multiply to get output
    factors_mul = {
        "T": 1,
        "2T": 1,
        "SRO": 1000,
        "SSRO": 1000,
        "WIND": 1,
        "10SI": 1,
        "SP": 0.001,
        "Q": 1,
        "SSR": 1,
        "R": 1,
        "E": 1000,
        "SUND": 1,
        "RO": 1000,
        "TP": 1000,
        "10U": 1,
        "10V": 1,
        "2D": 1,
        "SR": 1,
        "AL": 1,
        "HCC": 1,
    }

    types = {
        "T": "state",
        "2T": "state",
        "SRO": "flux",
        "SSRO": "flux",
        "WIND": "state",
        "10SI": "state",
        "SP": "state",
        "Q": "state",
        "SSR": "state",
        "R": "state",
        "E": "flux",
        "SUND": "flux",
        "RO": "flux",
        "TP": "flux",
        "10U": "state",
        "10V": "state",
        "2D": "state",
        "SR": "state",
        "AL": "state",
        "HCC": "state",
    }

    file_name = {
        "T": "Tair2m",
        "2T": "Tair",
        "SRO": "Surf_Runoff",
        "SSRO": "Subsurf_Runoff",
        "WIND": "Wind",
        "10SI": "Wind10m",
        "SP": "Psurf",
        "Q": "Qair",
        "SSR": "SWnet",
        "R": "RelQair",
        "E": "Evaporation",
        "SUND": "SunDur",
        "RO": "Runoff",
        "TP": "P",
        "10U": "Wind_U",
        "10V": "Wind_V",
        "2D": "Dewpoint2m",
        "SR": "SurfRoughness",
        "AL": "Albedo",
        "HCC": "HighCloudCover",
    }

    DownloadType = {
        "T": 3,
        "2T": 1,
        "SRO": 0,
        "SSRO": 0,
        "WIND": 0,
        "10SI": 0,
        "SP": 1,
        "Q": 3,
        "SSR": 2,
        "R": 3,
        "E": 2,
        "SUND": 2,
        "RO": 2,
        "TP": 2,
        "10U": 1,
        "10V": 1,
        "2D": 1,
        "SR": 1,
        "AL": 1,
        "HCC": 1,
    }


    def __init__(self, step):

        # output units after applying factor
        if step == "six_hourly":
            self.units = {
                "T": "C",
                "2T": "C",
                "SRO": "mm",
                "SSRO": "mm",
                "WIND": "m_s-1",
                "10SI": "m_s-1",
                "SP": "kpa",
                "Q": "kg_kg-1",
                "SSR": "W_m-2_s",
                "R": "percentage",
                "E": "mm",
                "SUND": "s",
                "RO": "mm",
                "TP": "mm",
                "10U": "m_s-1",
                "10V": "m_s-1",
                "2D": "C",
                "SR": "m",
                "AL": "-",
                "HCC": "-",
            }

        elif step == "daily":
            self.units = {
                "T": "C",
                "2T": "C",
                "SRO": "mm",
                "SSRO": "mm",
                "WIND": "m_s-1",
                "10SI": "m_s-1",
                "SP": "kpa",
                "Q": "kg_kg-1",
                "SSR": "W_m-2_s",
                "R": "percentage",
                "E": "mm",
                "SUND": "s",
                "RO": "mm",
                "TP": "mm",
                "10U": "m_s-1",
                "10V": "m_s-1",
                "2D": "C",
                "SR": "m",
                "AL": "-",
                "HCC": "-",
            }

        elif step == "monthly":
            self.units = {
                "T": "C",
                "2T": "C",
                "SRO": "mm",
                "SSRO": "mm",
                "WIND": "m_s-1",
                "10SI": "m_s-1",
                "SP": "kpa",
                "Q": "kg_kg-1",
                "SSR": "W_m-2_s",
                "R": "percentage",
                "E": "mm",
                "SUND": "s",
                "RO": "mm",
                "TP": "mm",
                "10U": "m_s-1",
                "10V": "m_s-1",
                "2D": "C",
                "SR": "m",
                "AL": "-",
                "HCC": "-",
            }

        else:
            raise KeyError("The input time step is not supported")


    def __str__(self):

        print(
            "Variable name:"
            + "\n"
            + str(self.var_name)
            + "\n"
            + "Descriptions"
            + "\n"
            + str(self.descriptions)
            + "\n"
            + "Units : "
            + "\n"
            + str(self.units)
        )


    def ListAttributes(self):
        """
        Print Attributes List
        """

        print("\n")
        print(
            "Attributes List of: "
            + repr(self.__dict__["name"])
            + " - "
            + self.__class__.__name__
            + " Instance\n"
        )
        self_keys = list(self.__dict__.keys())
        self_keys.sort()
        for key in self_keys:
            if key != "name":
                print(str(key) + " : " + repr(self.__dict__[key]))

        print("\n")


class CHIRPS:


    def __init__(
            self,
            start="",
            end="",
            latlim=[],
            lonlim=[],
            Time="daily",
            Path="",
            fmt="%Y-%m-%d",
    ):
        # latlim -- [ymin, ymax] (values must be between -50 and 50)
        # lonlim -- [xmin, xmax] (values must be between -180 and 180)
        # TimeCase -- String equal to 'daily' or 'monthly'

        # Define timestep for the timedates
        if Time == "daily":
            self.TimeFreq = "D"
            self.output_folder = os.path.join(Path, "Precipitation", "CHIRPS", "Daily")
        elif Time == "monthly":
            self.TimeFreq = "MS"
            self.output_folder = os.path.join(
                Path, "Precipitation", "CHIRPS", "Monthly"
            )
        else:
            raise KeyError("The input time interval is not supported")
        self.Time = Time

        # make directory if it not exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # check time variables
        if start == "":
            start = pd.Timestamp("1981-01-01")
        else:
            self.start = dt.datetime.strptime(start, fmt)

        if end == "":
            end = pd.Timestamp("Now")
        else:
            self.end = dt.datetime.strptisme(end, fmt)
        # Create days
        self.Dates = pd.date_range(self.start, self.end, freq=self.TimeFreq)

        # Check space variables
        if latlim[0] < -50 or latlim[1] > 50:
            print(
                "Latitude above 50N or below 50S is not possible."
                " Value set to maximum"
            )
            self.latlim[0] = np.max(latlim[0], -50)
            self.latlim[1] = np.min(lonlim[1], 50)
        if lonlim[0] < -180 or lonlim[1] > 180:
            print(
                "Longitude must be between 180E and 180W."
                " Now value is set to maximum"
            )
            self.lonlim[0] = np.max(latlim[0], -180)
            self.lonlim[1] = np.min(lonlim[1], 180)
        else:
            self.latlim = latlim
            self.lonlim = lonlim
        # Define IDs
        self.yID = 2000 - np.int16(
            np.array([np.ceil((latlim[1] + 50) * 20), np.floor((latlim[0] + 50) * 20)])
        )
        self.xID = np.int16(
            np.array(
                [np.floor((lonlim[0] + 180) * 20), np.ceil((lonlim[1] + 180) * 20)]
            )
        )


    def Download(self, Waitbar=1, cores=None):
        """
        ============================================================
            Download(self, Waitbar=1, cores=None)
        ============================================================
        Download method downloads CHIRPS data

        Parameters
        ----------
        Waitbar : TYPE, optional
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
            self.Time,
            self.xID,
            self.yID,
            self.lonlim,
            self.latlim,
        ]

        if not cores:
            # Create Waitbar
            if Waitbar == 1:
                total_amount = len(self.Dates)
                amount = 0
                weirdFn.printWaitBar(
                    amount,
                    total_amount,
                    prefix="Progress:",
                    suffix="Complete",
                    length=50,
                )

            for Date in self.Dates:
                CHIRPS.RetrieveData(Date, args)
                if Waitbar == 1:
                    amount = amount + 1
                    weirdFn.printWaitBar(
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


    def RetrieveData(Date, args):
        """
        ===============================================
             RetrieveData(Date, args)
        ===============================================
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
        [output_folder, TimeCase, xID, yID, lonlim, latlim] = args

        # open ftp server
        # ftp = FTP("chg-ftpout.geog.ucsb.edu", "", "")
        ftp = FTP("data.chc.ucsb.edu")
        ftp.login()

        # Define FTP path to directory
        if TimeCase == "daily":
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
        if TimeCase == "daily":
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
            RemoteSensing.ExtractFromGZ(zip_filename, outfilename, delete=True)

            # open tiff file
            src = gdal.Open(outfilename)
            dataset, NoDataValue = Raster.getRasterData(src)

            # clip dataset to the given extent
            data = dataset[yID[0]: yID[1], xID[0]: xID[1]]
            # replace -ve values with -9999
            data[data < 0] = -9999

            # save dataset as geotiff file
            geo = [lonlim[0], 0.05, 0, latlim[1], 0, -0.05]
            Raster.createRaster(
                path=DirFileEnd,
                data=data,
                geo=geo,
                epsg="WGS84",
                nodatavalue=NoDataValue,
            )

            # delete old tif file
            os.remove(outfilename)

        except:
            print("file not exists")
        return True


    def ListAttributes(self):
        """
        Print Attributes List
        """

        print("\n")
        print(
            "Attributes List of: "
            + repr(self.__dict__["name"])
            + " - "
            + self.__class__.__name__
            + " Instance\n"
        )
        self_keys = list(self.__dict__.keys())
        self_keys.sort()
        for key in self_keys:
            if key != "name":
                print(str(key) + " : " + repr(self.__dict__[key]))

        print("\n")


# class MSWEP():
"http://www.gloh2o.org/mswx/"
