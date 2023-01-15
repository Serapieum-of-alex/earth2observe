import os
from typing import List
import glob
import shutil
import pytest
from earth2observe.chirps import CHIRPS


@pytest.fixture(scope="session")
def test_create_chirps_object(
        dates: List,
        daily_temporal_resolution: str,
        lat_bounds: List,
        lon_bounds: List,
        chirps_base_dir: str,
):
    Coello = CHIRPS(
        start=dates[0],
        end=dates[1],
        lat_lim=lat_bounds,
        lon_lim=lon_bounds,
        temporal_resolution=daily_temporal_resolution,
        path=chirps_base_dir
    )
    assert Coello.api_url == "data.chc.ucsb.edu"
    assert Coello.lon_boundaries == [-180, 180]
    assert Coello.lat_bondaries == [-50, 50]
    assert str(Coello.dates[0].date()) == dates[0]
    assert str(Coello.dates[-1].date()) == dates[1]

    return Coello


def test_download(
        test_create_chirps_object: CHIRPS,
        chirps_base_dir: str,
):
    fname = test_create_chirps_object.clipped_fname
    test_create_chirps_object.download()

    filelist = glob.glob(os.path.join(f"{chirps_base_dir}/chirps/precipitation", f"{fname}*.tif"))
    assert len(filelist) == 10
    # delete the files
    shutil.rmtree(f"{chirps_base_dir}/chirps/precipitation")