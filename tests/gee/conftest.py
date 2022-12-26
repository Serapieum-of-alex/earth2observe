from typing import List

import pytest


@pytest.fixture(scope="module")
def catalog_columns() -> List[str]:
    return [
        "dataset",
        "name",
        "provider",
        "url",
        "bands",
        "band_describtion",
        "spatial_resolution",
        "temporal_resolution",
        "start_date",
        "end_date",
        "min",
        "max",
    ]
