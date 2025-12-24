import pytest
import polars as pl
from instagibbs.models import ensure_equal_exposure


@pytest.fixture
def sample_data() -> pl.DataFrame:
    """Create a sample DataFrame for testing"""
    return pl.DataFrame(
        {
            "start": [1, 1, 2, 2, 3, 3, 4, 4],
            "end": [10, 10, 15, 15, 20, 20, 25, 25],
            "exposure": [0.1, 0.5, 0.1, 0.5, 0.1, 0.5, 0.1, 0.3],
            "uptake": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        }
    )


def test_ensure_equal_exposure(sample_data: pl.DataFrame):
    """Test the ensure_equal_exposure function"""

    result = ensure_equal_exposure(sample_data)
    assert result.is_empty()

    result = ensure_equal_exposure(sample_data, [0.1, 0.5])
    assert set(result["start"]) == {1, 2, 3}
    assert len(result) == 6

    result = ensure_equal_exposure(sample_data[:-1])
    assert set(result["start"]) == {1, 2, 3}
    assert len(result) == 6
