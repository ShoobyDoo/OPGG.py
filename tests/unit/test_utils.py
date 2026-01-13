"""Unit tests for utils.py - utility functions."""

from opgg.utils import Utils
from opgg.params import Region
from opgg.search_result import SearchResult
from opgg.summoner import Summoner


class TestUtils:
    """Test utility functions."""

    def test_filter_results_with_summoner_id_keeps_valid(self):
        """Test that filter keeps results with valid summoner_id."""
        valid_result = SearchResult(
            summoner=Summoner(summoner_id="valid123", game_name="Player"),
            region=Region.NA,
        )

        results = [valid_result]
        filtered = Utils.filter_results_with_summoner_id(results)

        assert len(filtered) == 1
        assert filtered[0].summoner.summoner_id == "valid123"

    def test_filter_results_with_summoner_id_removes_invalid(self):
        """Test that filter removes results without summoner_id."""
        invalid_result = SearchResult(
            summoner=Summoner(game_name="Player"),  # No summoner_id
            region=Region.NA,
        )

        results = [invalid_result]
        filtered = Utils.filter_results_with_summoner_id(results)

        assert len(filtered) == 0

    def test_filter_results_mixed(self):
        """Test filter with mix of valid and invalid results."""
        valid_result = SearchResult(
            summoner=Summoner(summoner_id="valid123"), region=Region.NA
        )
        invalid_result = SearchResult(summoner=Summoner(game_name="NoID"), region=Region.KR)

        results = [valid_result, invalid_result, valid_result]
        filtered = Utils.filter_results_with_summoner_id(results)

        assert len(filtered) == 2
        assert all(r.summoner.summoner_id == "valid123" for r in filtered)

    def test_filter_results_empty_list(self):
        """Test filter with empty input list."""
        filtered = Utils.filter_results_with_summoner_id([])
        assert filtered == []

    def test_safe_get_existing_attribute(self):
        """Test safe_get with existing nested attributes."""

        class MockObj:
            def __init__(self):
                self.child = type("Child", (), {"value": 42})()

        obj = MockObj()
        result = Utils.safe_get(obj, "child", "value")
        assert result == 42

    def test_safe_get_missing_attribute(self):
        """Test safe_get with missing attribute."""

        class MockObj:
            pass

        obj = MockObj()
        result = Utils.safe_get(obj, "missing", "attribute")
        assert result is None

    def test_read_local_json(self, tmp_path):
        """Test reading a local JSON file."""
        # Create a temporary JSON file
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value", "number": 42}')

        result = Utils.read_local_json(str(json_file))

        assert result["key"] == "value"
        assert result["number"] == 42
