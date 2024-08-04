import glob
import os
import shutil
from typing import List

import pytest

from earth2observe.ecmwf import ECMWF


@pytest.fixture(scope="module")
def test_create_ecmwf_object(
    dates: List,
    lat_bounds: List,
    lon_bounds: List,
    ecmwf_base_dir: str,
    ecmwf_variables: List[str],
):
    ecmwf_base_dir = "AL"
    coello = ECMWF(
        start=dates[0],
        end=dates[1],
        lat_lim=lat_bounds,
        lon_lim=lon_bounds,
        path=ecmwf_base_dir,
        variables=ecmwf_variables,
    )
    assert isinstance(coello, ECMWF)
    return coello


# def test_download(
#     test_create_ecmwf_object: ECMWF,
#     ecmwf_base_dir: str,
#     number_downloaded_files: int,
# ):
#     test_create_ecmwf_object.download()
#     filelist = glob.glob(os.path.join(f"{ecmwf_base_dir}", f"*.tif"))
#     assert len(filelist) == number_downloaded_files
#     # delete the files
#     try:
#         shutil.rmtree(f"{ecmwf_base_dir}")
#     except PermissionError:
#         print("the downloaded files could not be deleted")
