import os
from typing import List
import glob
import shutil
import pytest
from earth2observe.chirps import CHIRPS


@pytest.fixture(scope="session")
def test_download_chirps(
        chirps_dates: list,
        daily_temporal_resolution: str,
        lat_bounds: List,
        lon_bounds: List,
        chirps_base_dir: str,
):
    Coello = CHIRPS(
        start=chirps_dates[0],
        end=chirps_dates[1],
        lat_lim=lat_bounds,
        lon_lim=lon_bounds,
        temporal_resolution=daily_temporal_resolution,
        path=chirps_base_dir
    )
    assert Coello.api_url == "data.chc.ucsb.edu"
    assert Coello.lon_boundaries == [-180, 180]
    assert Coello.lat_bondaries == [-50, 50]
    assert str(Coello.dates[0].date()) == chirps_dates[0]
    assert str(Coello.dates[-1].date()) == chirps_dates[1]

    return Coello


def test_download(
        test_download_chirps: CHIRPS,
        chirps_base_dir: str,
):
    test_download_chirps.download()
    print(os.listdir(os.path.join(f"{chirps_base_dir}/precipitation/chirps/daily")))
    filelist = glob.glob(os.path.join(f"{chirps_base_dir}/precipitation/chirps/daily", "chirps*.tif"))

    assert len(filelist) == 10
    # delete the files
    # [os.remove(i) for i in filelist]
    shutil.rmtree(f"{chirps_base_dir}/precipitation")