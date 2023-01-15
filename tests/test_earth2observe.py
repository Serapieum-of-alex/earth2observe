import glob
import os
import shutil
from typing import List

import pytest

from earth2observe.chirps import CHIRPS
from earth2observe.earth2observe import Earth2Observe
from earth2observe.ecmwf import ECMWF


class TestChirpsBackend:
    @pytest.fixture(scope="session")
    def test_chirps_data_source_instantiate_object(
        self,
        chirps_data_source: str,
        dates: List,
        daily_temporal_resolution: str,
        chirps_variables: List[str],
        lat_bounds: List,
        lon_bounds: List,
        chirps_data_source_output_dir: str,
    ):
        e2o = Earth2Observe(
            data_source=chirps_data_source,
            start=dates[0],
            end=dates[1],
            variables=chirps_variables,
            lat_lim=lat_bounds,
            lon_lim=lon_bounds,
            temporal_resolution=daily_temporal_resolution,
            path=chirps_data_source_output_dir,
        )
        assert isinstance(e2o.DataSources, dict)
        assert isinstance(e2o.datasource, CHIRPS)
        assert e2o.datasource.vars == chirps_variables
        assert isinstance(e2o.datasource.lat_lim, list)
        return e2o

    def test_download_chirps_backend(
        self,
        test_chirps_data_source_instantiate_object: CHIRPS,
        chirps_data_source_output_dir: str,
        number_downloaded_files: int,
    ):
        test_chirps_data_source_instantiate_object.download()
        fname = "P_CHIRPS"
        filelist = glob.glob(
            os.path.join(
                f"{chirps_data_source_output_dir}/chirps/precipitation", f"{fname}*.tif"
            )
        )
        assert len(filelist) == number_downloaded_files
        # delete the files
        shutil.rmtree(f"{chirps_data_source_output_dir}/chirps/precipitation")


class TestECMWFBackend:
    @pytest.fixture(scope="session")
    def test_ecmwf_data_source_instantiate_object(
        self,
        ecmwf_data_source: str,
        dates: List,
        daily_temporal_resolution: str,
        ecmwf_variables: List[str],
        lat_bounds: List,
        lon_bounds: List,
        ecmwf_data_source_output_dir: str,
    ):
        e2o = Earth2Observe(
            data_source=ecmwf_data_source,
            start=dates[0],
            end=dates[1],
            variables=ecmwf_variables,
            lat_lim=lat_bounds,
            lon_lim=lon_bounds,
            temporal_resolution=daily_temporal_resolution,
            path=ecmwf_data_source_output_dir,
        )
        assert isinstance(e2o.DataSources, dict)
        assert isinstance(e2o.datasource, ECMWF)
        assert e2o.datasource.vars == ecmwf_variables
        return e2o

    def test_download_chirps_backend(
        self,
        test_ecmwf_data_source_instantiate_object: CHIRPS,
        ecmwf_data_source_output_dir: str,
        number_downloaded_files: int,
    ):
        test_ecmwf_data_source_instantiate_object.download()
        filelist = glob.glob(
            os.path.join(f"{ecmwf_data_source_output_dir}/daily/Evaporation/", f"*.tif")
        )
        assert len(filelist) == number_downloaded_files
        # delete the files
        shutil.rmtree(f"{ecmwf_data_source_output_dir}/daily")
