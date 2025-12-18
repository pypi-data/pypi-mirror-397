"""
Unit tests for FASTA parsing and cache operations.
Tests for: yield_compressed_query_fasta_entries, get_cache_file_entry, write_shared_ref_entries_cache
"""

import gzip
import os
import tempfile

import pytest

from kompa.kompa import (
    COMMON_SEPARATOR,
    QueryEntry,
    get_cache_file_entry,
    lz4_compress,
    write_shared_ref_entries_cache,
    yield_compressed_query_fasta_entries,
)


class TestYieldCompressedQueryFastaEntries:
    """Test suite for yield_compressed_query_fasta_entries function."""

    def test_parse_single_entry(self):
        """Test parsing a single FASTA entry."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">header1\n")
            f.write("ATCG\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 1
            assert isinstance(entries[0], QueryEntry)
            assert entries[0].header == b"header1"
            assert entries[0].seq == b"ATCG"
            assert entries[0].compressed_seq_len > 0
            assert len(entries[0].compressed_seq) == entries[0].compressed_seq_len
        finally:
            os.unlink(test_file)

    def test_parse_multiple_entries(self):
        """Test parsing multiple FASTA entries."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">header1\n")
            f.write("ATCG\n")
            f.write(">header2\n")
            f.write("GCTA\n")
            f.write(">header3\n")
            f.write("TTAA\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 3
            assert entries[0].header == b"header1"
            assert entries[0].seq == b"ATCG"
            assert entries[1].header == b"header2"
            assert entries[1].seq == b"GCTA"
            assert entries[2].header == b"header3"
            assert entries[2].seq == b"TTAA"
        finally:
            os.unlink(test_file)

    def test_parse_multiline_sequence(self):
        """Test parsing FASTA entry with multiline sequence."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">header1\n")
            f.write("ATCG\n")
            f.write("GCTA\n")
            f.write("TTAA\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 1
            assert entries[0].header == b"header1"
            assert entries[0].seq == b"ATCGGCTATTAA"
        finally:
            os.unlink(test_file)

    def test_parse_empty_file(self):
        """Test parsing empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 0
        finally:
            os.unlink(test_file)

    def test_parse_header_stripping(self):
        """Test that > is stripped from headers."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">my_header_123\n")
            f.write("ATCG\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert entries[0].header == b"my_header_123"
            assert not entries[0].header.startswith(b">")
        finally:
            os.unlink(test_file)

    def test_parse_gzipped_file(self):
        """Test parsing gzipped FASTA file."""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".fasta.gz"
        ) as f:
            test_file = f.name

        try:
            with gzip.open(test_file, "wt") as gz:
                gz.write(">header1\n")
                gz.write("ATCG\n")
                gz.write(">header2\n")
                gz.write("GCTA\n")

            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 2
            assert entries[0].header == b"header1"
            assert entries[0].seq == b"ATCG"
            assert entries[1].header == b"header2"
            assert entries[1].seq == b"GCTA"
        finally:
            os.unlink(test_file)

    def test_parse_with_empty_lines(self):
        """Test parsing with empty lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">header1\n")
            f.write("ATCG\n")
            f.write("\n")
            f.write(">header2\n")
            f.write("GCTA\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            assert len(entries) == 2
            assert entries[0].seq == b"ATCG"
            assert entries[1].seq == b"GCTA"
        finally:
            os.unlink(test_file)

    def test_compression_length_consistency(self):
        """Test that compressed_seq_len matches actual compressed length."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">header1\n")
            f.write("ATCGATCGATCG\n")
            test_file = f.name

        try:
            entries = list(yield_compressed_query_fasta_entries(test_file))
            entry = entries[0]
            assert entry.compressed_seq_len == len(entry.compressed_seq)
            # Verify it matches manual compression
            manual_compressed = lz4_compress(entry.seq)
            assert entry.compressed_seq_len == len(manual_compressed)
        finally:
            os.unlink(test_file)


class TestGetCacheFileEntry:
    """Test suite for get_cache_file_entry function."""

    def test_basic_entry(self):
        """Test creating basic cache entry."""
        header = b">test_header"
        seq_buf = bytearray(b"ATCG")

        result = get_cache_file_entry(header, seq_buf)

        assert isinstance(result, bytes)
        assert b"test_header" in result
        assert b"ATCG" in result
        assert COMMON_SEPARATOR in result
        assert result.endswith(b"\n")

    def test_entry_format(self):
        """Test that cache entry has correct format."""
        header = b">my_seq"
        seq_buf = bytearray(b"GCTA")

        result = get_cache_file_entry(header, seq_buf)

        # Should be: header:::seq:::compressed_len\n
        parts = result.rstrip(b"\n").split(COMMON_SEPARATOR)
        assert len(parts) == 3
        assert parts[0] == b"my_seq"  # header without >
        assert parts[1] == b"GCTA"
        assert parts[2].isdigit()  # compressed length as string

    def test_header_stripping(self):
        """Test that > is stripped from header."""
        header = b">>>>>test"
        seq_buf = bytearray(b"ATCG")

        result = get_cache_file_entry(header, seq_buf)

        # lstrip(b">") strips all leading > characters, not just one
        assert b"test" in result
        assert not result.startswith(b">")

    def test_empty_sequence(self):
        """Test cache entry with empty sequence."""
        header = b">empty"
        seq_buf = bytearray(b"")

        result = get_cache_file_entry(header, seq_buf)

        assert isinstance(result, bytes)
        parts = result.rstrip(b"\n").split(COMMON_SEPARATOR)
        assert parts[0] == b"empty"
        assert parts[1] == b""
        assert int(parts[2]) > 0  # Even empty data has compressed size

    def test_large_sequence(self):
        """Test cache entry with large sequence."""
        header = b">large"
        seq_buf = bytearray(b"A" * 10000)

        result = get_cache_file_entry(header, seq_buf)

        assert isinstance(result, bytes)
        parts = result.rstrip(b"\n").split(COMMON_SEPARATOR)
        assert parts[0] == b"large"
        assert len(parts[1]) == 10000
        assert int(parts[2]) > 0


class TestWriteSharedRefEntriesCache:
    """Test suite for write_shared_ref_entries_cache function."""

    def test_single_reference_file(self):
        """Test caching single reference file."""
        # Create test reference file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            f.write(">ref2\n")
            f.write("GCTA\n")
            ref_file = f.name

        # Create cache file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            result_path = write_shared_ref_entries_cache([ref_file], cache_file)

            assert result_path == cache_file
            assert os.path.exists(cache_file)

            # Read cache and verify format
            with open(cache_file, "rb") as f:
                content = f.read()
                lines = content.strip().split(b"\n")
                assert len(lines) == 2

                # Check first entry
                parts1 = lines[0].split(COMMON_SEPARATOR)
                assert parts1[0] == b"ref1"
                assert parts1[1] == b"ATCG"

                # Check second entry
                parts2 = lines[1].split(COMMON_SEPARATOR)
                assert parts2[0] == b"ref2"
                assert parts2[1] == b"GCTA"
        finally:
            os.unlink(ref_file)
            os.unlink(cache_file)

    def test_multiple_reference_files(self):
        """Test caching multiple reference files."""
        # Create test reference files
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            ref_file1 = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref2\n")
            f.write("GCTA\n")
            ref_file2 = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            result_path = write_shared_ref_entries_cache(
                [ref_file1, ref_file2], cache_file
            )

            assert result_path == cache_file

            with open(cache_file, "rb") as f:
                content = f.read()
                lines = content.strip().split(b"\n")
                # Should have 2 entries (one from each file)
                assert len(lines) >= 2
                assert b"ref1" in content
                assert b"ref2" in content
        finally:
            os.unlink(ref_file1)
            os.unlink(ref_file2)
            os.unlink(cache_file)

    def test_empty_reference_file(self):
        """Test caching empty reference file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            ref_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            result_path = write_shared_ref_entries_cache([ref_file], cache_file)

            assert result_path == cache_file

            with open(cache_file, "rb") as f:
                content = f.read()
                assert content == b""
        finally:
            os.unlink(ref_file)
            os.unlink(cache_file)

    def test_gzipped_reference_file(self):
        """Test caching gzipped reference file."""
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".fasta.gz"
        ) as f:
            ref_file = f.name

        with gzip.open(ref_file, "wt") as gz:
            gz.write(">ref1\n")
            gz.write("ATCG\n")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            result_path = write_shared_ref_entries_cache([ref_file], cache_file)

            with open(cache_file, "rb") as f:
                content = f.read()
                lines = content.strip().split(b"\n")
                assert len(lines) == 1
                parts = lines[0].split(COMMON_SEPARATOR)
                assert parts[0] == b"ref1"
                assert parts[1] == b"ATCG"
        finally:
            os.unlink(ref_file)
            os.unlink(cache_file)

    def test_multiline_sequences(self):
        """Test caching with multiline sequences."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".fasta") as f:
            f.write(">ref1\n")
            f.write("ATCG\n")
            f.write("GCTA\n")
            f.write("TTAA\n")
            ref_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cache") as f:
            cache_file = f.name

        try:
            write_shared_ref_entries_cache([ref_file], cache_file)

            with open(cache_file, "rb") as f:
                content = f.read()
                lines = content.strip().split(b"\n")
                parts = lines[0].split(COMMON_SEPARATOR)
                # Multiline sequence should be concatenated
                assert parts[1] == b"ATCGGCTATTAA"
        finally:
            os.unlink(ref_file)
            os.unlink(cache_file)
