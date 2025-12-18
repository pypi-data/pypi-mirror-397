"""
Unit tests for NCD classification logic.
Tests for: classify_query_entry, ClassifyQueryEntryArgs, ClassificationResultEntry
"""

import os
import tempfile

import pytest

from kompa.kompa import (
    COMMON_SEPARATOR,
    ClassificationResultEntry,
    ClassifyQueryEntryArgs,
    classify_query_entry,
    lz4_compress,
)


class TestClassifyQueryEntry:
    """Test suite for classify_query_entry function."""

    def test_basic_classification(self):
        """Test basic NCD classification with single reference."""
        # Create cache file with one reference
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            ref_seq = b"ATCGATCGATCG"
            compressed_len = len(lz4_compress(ref_seq))
            cache_line = (
                b"ref1"
                + COMMON_SEPARATOR
                + ref_seq
                + COMMON_SEPARATOR
                + str(compressed_len).encode()
                + b"\n"
            )
            f.write(cache_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCGATCGATCG",  # Same as reference
                query_compressed_len=len(lz4_compress(b"ATCGATCGATCG")),
                k_nearest=1,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            assert isinstance(result, ClassificationResultEntry)
            assert result.query_header == "query1"
            assert result.best_reference_header == "ref1"
            assert result.normalized_compression_distance >= 0.0
            assert result.frequency == 1
            assert result.max_k_nearest == 1
            assert result.spreading_limit == 0.05
        finally:
            os.unlink(cache_file)

    def test_k_nearest_neighbors(self):
        """Test classification with multiple k-nearest neighbors."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Create 5 references with varying similarity
            for i in range(5):
                ref_seq = b"ATCG" * (i + 1)
                compressed_len = len(lz4_compress(ref_seq))
                cache_line = (
                    f"ref{i}".encode()
                    + COMMON_SEPARATOR
                    + ref_seq
                    + COMMON_SEPARATOR
                    + str(compressed_len).encode()
                    + b"\n"
                )
                f.write(cache_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCGATCG",  # Similar to ref1
                query_compressed_len=len(lz4_compress(b"ATCGATCG")),
                k_nearest=3,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            assert result.max_k_nearest == 3
            assert result.frequency <= 3
            assert result.best_reference_header.startswith("ref")
        finally:
            os.unlink(cache_file)

    def test_empty_cache(self):
        """Test classification with empty cache returns zeroed result."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Write at least one byte so mmap doesn't fail on empty file
            f.write(b"\n")
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCG",
                query_compressed_len=len(lz4_compress(b"ATCG")),
                k_nearest=5,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            assert result.query_header == "query1"
            assert result.best_reference_header == ""
            assert result.normalized_compression_distance == 0.0
            assert result.frequency == 0
        finally:
            os.unlink(cache_file)

    def test_spreading_below_limit(self):
        """Test frequency counting when spreading is below limit."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Create multiple references with same header (duplicates)
            ref_seq = b"ATCGATCGATCG"
            compressed_len = len(lz4_compress(ref_seq))
            for i in range(3):
                cache_line = (
                    b"same_ref"
                    + COMMON_SEPARATOR
                    + ref_seq
                    + COMMON_SEPARATOR
                    + str(compressed_len).encode()
                    + b"\n"
                )
                f.write(cache_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCGATCGATCG",
                query_compressed_len=len(lz4_compress(b"ATCGATCGATCG")),
                k_nearest=3,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            # Should pick the most frequent (all 3 are same)
            assert result.best_reference_header == "same_ref"
            assert result.frequency == 3
        finally:
            os.unlink(cache_file)

    def test_spreading_above_limit(self):
        """Test that spreading above limit uses lowest NCD."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Create references with very different sequences
            refs = [
                (b"ref_close", b"ATCGATCG"),
                (b"ref_far", b"GGGGGGGG"),
            ]
            for header, seq in refs:
                compressed_len = len(lz4_compress(seq))
                cache_line = (
                    header
                    + COMMON_SEPARATOR
                    + seq
                    + COMMON_SEPARATOR
                    + str(compressed_len).encode()
                    + b"\n"
                )
                f.write(cache_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCGATCG",
                query_compressed_len=len(lz4_compress(b"ATCGATCG")),
                k_nearest=2,
                spreading_limit=0.01,  # Very low limit
            )

            result = classify_query_entry(args)

            # Should pick ref_close as it's more similar
            assert result.frequency == 1
        finally:
            os.unlink(cache_file)

    def test_malformed_cache_line_skipped(self):
        """Test that malformed cache lines are skipped."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Write malformed line (missing separator)
            f.write(b"malformed_line\n")
            # Write valid line
            ref_seq = b"ATCG"
            compressed_len = len(lz4_compress(ref_seq))
            valid_line = (
                b"ref1"
                + COMMON_SEPARATOR
                + ref_seq
                + COMMON_SEPARATOR
                + str(compressed_len).encode()
                + b"\n"
            )
            f.write(valid_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCG",
                query_compressed_len=len(lz4_compress(b"ATCG")),
                k_nearest=1,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            # Should still work with valid line
            assert result.best_reference_header == "ref1"
        finally:
            os.unlink(cache_file)

    def test_unicode_header_handling(self):
        """Test handling of headers with non-ASCII characters."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            ref_seq = b"ATCG"
            compressed_len = len(lz4_compress(ref_seq))
            # Header with unicode
            cache_line = (
                "réf1".encode("utf-8")
                + COMMON_SEPARATOR
                + ref_seq
                + COMMON_SEPARATOR
                + str(compressed_len).encode()
                + b"\n"
            )
            f.write(cache_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header="quéry1".encode("utf-8"),
                query_seq=b"ATCG",
                query_compressed_len=len(lz4_compress(b"ATCG")),
                k_nearest=1,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            assert result.query_header == "quéry1"
            assert result.best_reference_header == "réf1"
        finally:
            os.unlink(cache_file)

    def test_zero_compressed_length_skipped(self):
        """Test that references with zero compressed length are skipped."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".cache") as f:
            # Write entry with 0 compressed length (edge case)
            cache_line = (
                b"ref_zero" + COMMON_SEPARATOR + b"" + COMMON_SEPARATOR + b"0\n"
            )
            f.write(cache_line)
            # Write valid entry
            ref_seq = b"ATCG"
            compressed_len = len(lz4_compress(ref_seq))
            valid_line = (
                b"ref1"
                + COMMON_SEPARATOR
                + ref_seq
                + COMMON_SEPARATOR
                + str(compressed_len).encode()
                + b"\n"
            )
            f.write(valid_line)
            cache_file = f.name

        try:
            args = ClassifyQueryEntryArgs(
                cache_ref_path=cache_file,
                query_header=b"query1",
                query_seq=b"ATCG",
                query_compressed_len=len(lz4_compress(b"ATCG")),
                k_nearest=1,
                spreading_limit=0.05,
            )

            result = classify_query_entry(args)

            # Should use valid entry, skip zero length
            assert result.best_reference_header == "ref1"
        finally:
            os.unlink(cache_file)


class TestClassificationResultEntry:
    """Test suite for ClassificationResultEntry NamedTuple."""

    def test_create_entry(self):
        """Test creating ClassificationResultEntry."""
        entry = ClassificationResultEntry(
            query_header="query1",
            best_reference_header="ref1",
            normalized_compression_distance=0.5,
            frequency=3,
            max_k_nearest=5,
            spreading_limit=0.05,
        )

        assert entry.query_header == "query1"
        assert entry.best_reference_header == "ref1"
        assert entry.normalized_compression_distance == 0.5
        assert entry.frequency == 3
        assert entry.max_k_nearest == 5
        assert entry.spreading_limit == 0.05

    def test_immutable(self):
        """Test that ClassificationResultEntry is immutable."""
        entry = ClassificationResultEntry(
            query_header="query1",
            best_reference_header="ref1",
            normalized_compression_distance=0.5,
            frequency=3,
            max_k_nearest=5,
            spreading_limit=0.05,
        )

        with pytest.raises(AttributeError):
            entry.query_header = "new_query"


class TestClassifyQueryEntryArgs:
    """Test suite for ClassifyQueryEntryArgs NamedTuple."""

    def test_create_args(self):
        """Test creating ClassifyQueryEntryArgs."""
        args = ClassifyQueryEntryArgs(
            cache_ref_path="/path/to/cache",
            query_header=b"query1",
            query_seq=b"ATCG",
            query_compressed_len=100,
            k_nearest=5,
            spreading_limit=0.05,
        )

        assert args.cache_ref_path == "/path/to/cache"
        assert args.query_header == b"query1"
        assert args.query_seq == b"ATCG"
        assert args.query_compressed_len == 100
        assert args.k_nearest == 5
        assert args.spreading_limit == 0.05

    def test_immutable(self):
        """Test that ClassifyQueryEntryArgs is immutable."""
        args = ClassifyQueryEntryArgs(
            cache_ref_path="/path/to/cache",
            query_header=b"query1",
            query_seq=b"ATCG",
            query_compressed_len=100,
            k_nearest=5,
            spreading_limit=0.05,
        )

        with pytest.raises(AttributeError):
            args.k_nearest = 10
