import pytest
import os
import glob
import shutil
from typing import List
from earth2observe.ecmwf import ECMWF

@pytest.fixture(scope="session")
def test_create_ecmwf_object(
        dates: List,
        lat_bounds: List,
        lon_bounds: List,
        ecmwf_base_dir: str,
        ecmwf_variables: List[str],
):
    Coello = ECMWF(
        start=dates[0],
        end=dates[1],
        lat_lim=lat_bounds,
        lon_lim=lon_bounds,
        path=ecmwf_base_dir,
        variables=ecmwf_variables,
    )
    assert isinstance(Coello, ECMWF)
    return Coello


def test_download(
        test_create_ecmwf_object: ECMWF,
        ecmwf_base_dir: str,
):

    test_create_ecmwf_object.download()
    filelist = glob.glob(os.path.join(f"{ecmwf_base_dir}/daily/Evaporation/", f"*.tif"))
    assert len(filelist) == 10
    # delete the files
    shutil.rmtree(f"{ecmwf_base_dir}/daily")