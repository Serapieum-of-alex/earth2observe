import pytest
from typing import List
from pathlib import Path
from tests.gee.conftest import *



@pytest.fixture(scope="session")
def dates() -> List:
    return ["2009-01-01", "2009-01-10"]

@pytest.fixture(scope="session")
def daily_temporal_resolution() -> str:
    return "daily"

@pytest.fixture(scope="session")
def lat_bounds() -> List:
    return [4.19, 4.64]


@pytest.fixture(scope="session")
def lon_bounds() -> List:
    return [-75.65, -74.73]

@pytest.fixture(scope="session")
def chirps_base_dir() -> str:
    return "tests/data/chirps"


@pytest.fixture(scope="session")
def ecmwf_base_dir() -> Path:
    return Path("tests/data/ecmwf").absolute()


@pytest.fixture(scope="session")
def ecmwf_variables() -> List[str]:
    return ["E"]  # "T",