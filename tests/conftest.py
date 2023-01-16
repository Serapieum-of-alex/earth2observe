from pathlib import Path
from typing import List

import pytest

from tests.gee.conftest import *


@pytest.fixture(scope="session")
def dates() -> List:
    return ["2009-01-01", "2009-01-02"]


@pytest.fixture(scope="session")
def monthly_dates() -> List:
    return ["2009-01-01", "2009-02-01"]


@pytest.fixture(scope="session")
def number_downloaded_files() -> int:
    return 2


@pytest.fixture(scope="session")
def daily_temporal_resolution() -> str:
    return "daily"

@pytest.fixture(scope="session")
def monthly_temporal_resolution() -> str:
    return "monthly"


@pytest.fixture(scope="session")
def lat_bounds() -> List:
    return [4.19, 4.64]


@pytest.fixture(scope="session")
def lon_bounds() -> List:
    return [-75.65, -74.73]


@pytest.fixture(scope="session")
def chirps_base_dir() -> str:
    return "tests/data/delete/chirps"


@pytest.fixture(scope="session")
def ecmwf_base_dir() -> Path:
    return Path("tests/data/delete/ecmwf").absolute()

@pytest.fixture(scope="session")
def s3_era5_base_dir() -> Path:
    return Path("tests/data/delete/s3/era5").absolute()

@pytest.fixture(scope="session")
def chirps_variables() -> List[str]:
    return ["precipitation"]  # "T",

@pytest.fixture(scope="session")
def ecmwf_variables() -> List[str]:
    return ["E"]  # "T",

@pytest.fixture(scope="session")
def s3_era5_variables() -> List[str]:
    return ["precipitation"]


@pytest.fixture(scope="session")
def ecmwf_data_source() -> str:
    return "ecmwf"

@pytest.fixture(scope="session")
def chirps_data_source() -> str:
    return "chirps"

@pytest.fixture(scope="session")
def s3_data_source() -> str:
    return "amazon-s3"


@pytest.fixture(scope="session")
def ecmwf_data_source_output_dir() -> str:
    return Path("tests/data/delete/ecmwf-backend").absolute()


@pytest.fixture(scope="session")
def chirps_data_source_output_dir() -> str:
    return Path("tests/data/delete/chirps-backend").absolute()

@pytest.fixture(scope="session")
def s3_era5_data_source_output_dir() -> str:
    return Path("tests/data/delete/s3-era5").absolute()
