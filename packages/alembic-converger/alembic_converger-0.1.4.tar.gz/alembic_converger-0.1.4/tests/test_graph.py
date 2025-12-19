"""
Tests for graph analysis module.
"""


from alembic_converger.graph import (
    get_merge_pairs,
    sort_heads_deterministically,
)


class TestDeterministicSorting:
    """Test deterministic sorting of heads."""

    def test_sort_empty_list(self):
        """Test sorting empty list."""
        result = sort_heads_deterministically([])
        assert result == []

    def test_sort_single_head(self):
        """Test sorting single head."""
        result = sort_heads_deterministically(["abc123"])
        assert result == ["abc123"]

    def test_sort_multiple_heads(self):
        """Test sorting multiple heads alphabetically."""
        heads = ["zzz", "aaa", "mmm", "bbb"]
        result = sort_heads_deterministically(heads)
        assert result == ["aaa", "bbb", "mmm", "zzz"]

    def test_sort_is_stable(self):
        """Test that sorting is stable and reproducible."""
        heads = ["rev3", "rev1", "rev2"]
        result1 = sort_heads_deterministically(heads)
        result2 = sort_heads_deterministically(heads)
        assert result1 == result2
        assert result1 == ["rev1", "rev2", "rev3"]


class TestMergePairs:
    """Test merge pair generation."""

    def test_no_pairs_for_empty_list(self):
        """Test no pairs for empty list."""
        result = get_merge_pairs([])
        assert result == []

    def test_no_pairs_for_single_head(self):
        """Test no pairs for single head."""
        result = get_merge_pairs(["abc123"])
        assert result == []

    def test_one_pair_for_two_heads(self):
        """Test one pair for two heads."""
        result = get_merge_pairs(["bbb", "aaa"])
        assert result == [("aaa", "bbb")]

    def test_pairs_are_sorted(self):
        """Test that pairs use sorted heads."""
        heads = ["zzz", "aaa", "mmm"]
        result = get_merge_pairs(heads)
        # Should merge first two sorted heads
        assert result == [("aaa", "mmm")]


class TestGraphValidation:
    """Test graph validation functions."""

    # Note: These tests would require mock RevisionMap objects
    # For now, we'll test the logic that doesn't require Alembic

    def test_deterministic_ordering(self):
        """Test that head ordering is deterministic."""
        heads1 = ["c", "a", "b"]
        heads2 = ["b", "c", "a"]

        sorted1 = sort_heads_deterministically(heads1)
        sorted2 = sort_heads_deterministically(heads2)

        assert sorted1 == sorted2
        assert sorted1 == ["a", "b", "c"]
